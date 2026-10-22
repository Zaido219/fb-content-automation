import base64
import binascii
import logging
import os
import random
import time
from io import BytesIO
from typing import Optional

import requests
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from PIL import Image

from src.models.DTO import ImageGenerationPayload

load_dotenv()

logger = logging.getLogger(__name__)

# HTTP codes worth retrying / falling back on (capacity or rate limit issues).
# Anything else (400 bad request, 401/403 auth, 404 wrong model name) is raised
# immediately because switching models won't fix it.
RETRYABLE_CODES = {429, 500, 503, 504}


class ImagenClientWrapper:
    """Wrapper class communicating with Google AI Studio using the modern google-genai SDK."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-3.8-flash-image",
        fallback_models: Optional[list[str]] = None,
        retries_per_model: int = 2,
    ):
        resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not resolved_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")

        self.client = genai.Client(api_key=resolved_key)
        self.model = model
        self.retries_per_model = retries_per_model

        # NOTE: every model here must support image output, otherwise it will
        # respond successfully but return no image.
        # Names taken from client.models.list() for this API key.
        fallbacks = fallback_models or [
            "gemini-3.1-flash-lite-image",
            "gemini-2.5-flash-image",
        ]

        # Primary first, then fallbacks, without duplicates, order preserved.
        self.model_chain = list(dict.fromkeys([self.model, *fallbacks]))

    @staticmethod
    def _extract_images(response) -> list[Image.Image]:
        """Parse inline image bytes returned by the multimodal response."""
        images: list[Image.Image] = []
        if response.candidates:
            content = response.candidates[0].content
            for part in (content.parts or []) if content else []:
                if part.inline_data:
                    images.append(Image.open(BytesIO(part.inline_data.data)))
        return images

    def generate_image_from_payload(
        self,
        payload: ImageGenerationPayload,
    ) -> list[Image.Image]:
        """Generates an image via Gemini, falling back to other models on overload."""

        # negative_prompt isn't a top-level field in generate_content,
        # so it is folded into the prompt text.
        full_prompt = (
            f"Generate an image based on this description: {payload.prompt}\n\n"
            f"Negative constraints (do NOT include these elements): {payload.negative_prompt}"
        )

        last_error: Optional[Exception] = None

        for model_name in self.model_chain:
            for attempt in range(self.retries_per_model):
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=full_prompt,
                    )
                except errors.APIError as e:
                    # 404 = model name invalid/unsupported: skip to the next model
                    if e.code == 404:
                        logger.error("Model %s not found, skipping", model_name)
                        last_error = e
                        break
                    # 429 = quota/rate limit for THIS model. Retrying the same model
                    # won't help (it can take minutes to hours), so try the next one.
                    if e.code == 429:
                        logger.warning(
                            "%s quota exhausted (429), skipping: %s",
                            model_name, (e.message or "")[:1200],
                        )
                        last_error = e
                        break
                    if e.code not in RETRYABLE_CODES:
                        raise
                    last_error = e
                    logger.warning(
                        "%s failed (code %s), attempt %d/%d",
                        model_name, e.code, attempt + 1, self.retries_per_model,
                    )
                    # Exponential backoff with jitter; skip the wait after the last try.
                    if attempt < self.retries_per_model - 1:
                        time.sleep(2 ** attempt + random.random())
                    continue

                images = self._extract_images(response)
                if images:
                    if model_name != self.model:
                        logger.info("Succeeded using fallback model %s", model_name)
                    return images

                # Model answered but returned no image: move on to the next model.
                text = getattr(response, "text", None)
                logger.warning(
                    "%s returned no image (text reply: %r), trying next model",
                    model_name, (text or "")[:200],
                )
                break

            logger.warning("Giving up on %s, trying next fallback", model_name)

        if last_error:
            raise last_error
        raise RuntimeError("No model in the fallback chain returned an image.")


class CloudflareAPIError(Exception):
    """Error from the Cloudflare Workers AI REST API (mirrors errors.APIError's .code/.message)."""

    def __init__(self, code: int, message: str = ""):
        super().__init__(f"Cloudflare API error {code}: {message}")
        self.code = code
        self.message = message


class CloudflareImageClientWrapper:
    """Wrapper class communicating with the Cloudflare Workers AI REST API (FLUX models).

    Free tier: 10,000 neurons/day, resetting at 00:00 UTC. Once it is used up,
    requests fail until the reset, so quota errors are NOT retried here.
    """

    BASE_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
    MAX_STEPS = 8  # flux-1-schnell accepts 1-8 steps

    def __init__(
        self,
        account_id: Optional[str] = None,
        api_token: Optional[str] = None,
        model: str = "@cf/black-forest-labs/flux-1-schnell",
        retries: int = 2,
        steps: int = 4,
        timeout: float = 60.0,
    ):
        resolved_account = account_id or os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        resolved_token = api_token or os.environ.get("CLOUDFLARE_API_TOKEN")
        if not resolved_account:
            raise ValueError("CLOUDFLARE_ACCOUNT_ID environment variable is missing.")
        if not resolved_token:
            raise ValueError("CLOUDFLARE_API_TOKEN environment variable is missing.")

        self.model = model
        self.retries = retries
        self.steps = max(1, min(steps, self.MAX_STEPS))
        self.timeout = timeout
        self.url = self.BASE_URL.format(account_id=resolved_account, model=model)
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {resolved_token}"})

    @staticmethod
    def _extract_images(response: dict) -> list[Image.Image]:
        """Parse the base64 image returned in the Workers AI JSON response."""
        b64_image = (response.get("result") or {}).get("image")
        if not b64_image:
            return []
        try:
            image = Image.open(BytesIO(base64.b64decode(b64_image)))
            image.load()  # force decoding now so corrupt data fails here
        except (binascii.Error, OSError) as e:
            logger.warning("Could not decode image from Cloudflare response: %s", e)
            return []
        return [image]

    def _post(self, body: dict) -> dict:
        """POST to Workers AI and return the parsed JSON, raising CloudflareAPIError on failure."""
        try:
            resp = self.session.post(self.url, json=body, timeout=self.timeout)
        except requests.Timeout as e:
            raise CloudflareAPIError(504, f"request timed out: {e}") from e
        except requests.ConnectionError as e:
            raise CloudflareAPIError(503, f"connection failed: {e}") from e

        try:
            data = resp.json()
        except ValueError:
            data = {}

        if not resp.ok or not data.get("success", False):
            message = str(data.get("errors") or resp.text)[:1200]
            raise CloudflareAPIError(resp.status_code, message)
        return data

    def generate_image_from_payload(
        self,
        payload: ImageGenerationPayload,
    ) -> list[Image.Image]:
        """Generates an image via Cloudflare FLUX, retrying on transient errors."""

        # FLUX schnell has no negative prompt support, and writing the unwanted
        # elements into the prompt tends to make them appear, so it is ignored.
        body = {"prompt": payload.prompt, "steps": self.steps}

        last_error: Optional[Exception] = None

        for attempt in range(self.retries):
            try:
                response = self._post(body)
            except CloudflareAPIError as e:
                last_error = e
                # 429 = daily free quota (or rate limit). Retrying won't help.
                if e.code == 429:
                    logger.warning(
                        "%s quota exhausted (429): %s",
                        self.model, (e.message or "")[:1200],
                    )
                    raise
                if e.code not in RETRYABLE_CODES:
                    raise
                logger.warning(
                    "%s failed (code %s), attempt %d/%d",
                    self.model, e.code, attempt + 1, self.retries,
                )
                # Exponential backoff with jitter; skip the wait after the last try.
                if attempt < self.retries - 1:
                    time.sleep(2 ** attempt + random.random())
                continue

            images = self._extract_images(response)
            if images:
                return images
            raise RuntimeError(f"{self.model} returned no image.")

        if last_error:
            raise last_error
        raise RuntimeError("Cloudflare request was never attempted (retries must be >= 1).")


class FallbackImageGenerator:
    """Tries each image provider in order and returns the first successful result.

    Example:
        generator = FallbackImageGenerator([
            ImagenClientWrapper(),
            CloudflareImageClientWrapper(),
        ])
        images = generator.generate_image_from_payload(payload)
    """

    def __init__(self, providers: list):
        if not providers:
            raise ValueError("At least one image provider is required.")
        self.providers = providers

    def generate_image_from_payload(
        self,
        payload: ImageGenerationPayload,
    ) -> list[Image.Image]:
        errors_seen: list[str] = []
        last_error: Optional[Exception] = None

        for provider in self.providers:
            name = type(provider).__name__
            try:
                images = provider.generate_image_from_payload(payload)
            except Exception as e:  # any provider failure -> try the next provider
                logger.warning("%s failed, trying next provider: %s", name, e)
                errors_seen.append(f"{name}: {e}")
                last_error = e
                continue

            if images:
                if provider is not self.providers[0]:
                    logger.info("Succeeded using fallback provider %s", name)
                return images

            logger.warning("%s returned no images, trying next provider", name)
            errors_seen.append(f"{name}: returned no images")

        raise RuntimeError(
            "All image providers failed: " + " | ".join(errors_seen)
        ) from last_error
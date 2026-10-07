import logging
import os
import random
import time
from io import BytesIO
from typing import Optional

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
        model: str = "gemini-3.6-flash",
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
        fallbacks = fallback_models or [
            "gemini-3.1-flash-image",
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
                logger.warning("%s returned no image, trying next model", model_name)
                break

            logger.warning("Giving up on %s, trying next fallback", model_name)

        if last_error:
            raise last_error
        raise RuntimeError("No model in the fallback chain returned an image.")
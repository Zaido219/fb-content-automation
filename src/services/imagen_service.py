import os
from io import BytesIO
from typing import Optional
from dotenv import load_dotenv
from google import genai
from PIL import Image
from src.models.DTO import ImageGenerationPayload

load_dotenv()


class ImagenClientWrapper:
    """Wrapper class communicating with Google AI Studio using the modern google-genai SDK."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-3.6-flash",
    ):
        resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not resolved_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is missing."
            )

        self.client = genai.Client(api_key=resolved_key)
        self.model = model

    def generate_image_from_payload(
        self,
        payload: ImageGenerationPayload,
    ) -> list[Image.Image]:
        """Generates an image via Gemini multimodal generation in AI Studio."""
        
        # Structure the prompt text clearly since negative_prompt parameter isn't a top-level field in generate_content
        full_prompt = (
            f"Generate an image based on this description: {payload.prompt}\n\n"
            f"Negative constraints (do NOT include these elements): {payload.negative_prompt}"
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt,
        )

        images = []
        # Parse inline image bytes returned by the multimodal response
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    pil_img = Image.open(BytesIO(part.inline_data.data))
                    images.append(pil_img)

        return images
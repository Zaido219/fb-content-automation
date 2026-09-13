import os
from io import BytesIO
from typing import Optional
from PIL import Image
from google import genai
from google.genai import types
from models.DTO import ImageGenerationPayload


class ImagenClientWrapper:
    """Wrapper class responsible for communicating with the Gemini API to generate images using Imagen models."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "imagen-3.0-generate-002",
    ):
        # Fall back to GEMINI_API_KEY from environment if not explicitly provided
        resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not resolved_key:
            raise ValueError(
                "API Key is missing. Pass it to the constructor or set GEMINI_API_KEY environment variable."
            )

        self.client = genai.Client(api_key=resolved_key)
        self.model = model

    def generate_image_from_payload(
        self,
        payload: ImageGenerationPayload,
        number_of_images: int = 1,
    ) -> list[Image.Image]:
        config = types.GenerateImagesConfig(
            number_of_images=number_of_images,
            aspect_ratio=payload.aspect_ratio,
            output_mime_type=payload.output_mime_type,
            negative_prompt=payload.negative_prompt,
        )

        response = self.client.models.generate_images(
            model=self.model, prompt=payload.prompt, config=config
        )

        images = []
        for generated_img in response.generated_images:
            image_bytes = generated_img.image.image_bytes
            pil_img = Image.open(BytesIO(image_bytes))
            images.append(pil_img)

        return images
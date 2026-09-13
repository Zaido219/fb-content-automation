import os
from io import BytesIO
from typing import Optional
from PIL import Image
from google import genai
from google.genai import types


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

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        output_mime_type: str = "image/png",
        number_of_images: int = 1,
    ) -> list[Image.Image]:
        """Sends an image generation request to the Gemini API and returns PIL Image objects."""
        config = types.GenerateImagesConfig(
            number_of_images=number_of_images,
            aspect_ratio=aspect_ratio,
            output_mime_type=output_mime_type,
        )

        response = self.client.models.generate_images(
            model=self.model, prompt=prompt, config=config
        )

        images = []
        for generated_img in response.generated_images:
            image_bytes = generated_img.image.image_bytes
            pil_img = Image.open(BytesIO(image_bytes))
            images.append(pil_img)

        return images


class ImageSaver:
    """Utility class to separate file persistence logic from API generation logic (SRP)."""

    @staticmethod
    def save(
        image: Image.Image, filepath: str, format_type: str = "PNG"
    ) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        image.save(filepath, format=format_type)
        print(f"Image successfully saved to: {filepath}")


# Example usage:
if __name__ == "__main__":
    try:
        # Initialize client (uses GEMINI_API_KEY env var)
        generator = ImagenClientWrapper()

        prompt = "90s cartoon slice of life setting in the Philippines, high quality, vibrant colors"
        images = generator.generate_image(
            prompt=prompt, aspect_ratio="1:1", number_of_images=1
        )

        if images:
            ImageSaver.save(images[0], "output/cartoon_scene.png")

    except Exception as e:
        print(f"Failed to generate image: {e}")
import os
from PIL import Image


class ImageSaver:
    """Utility class to separate file persistence logic from API generation logic (SRP)."""

    @staticmethod
    def save(
        image: Image.Image, filepath: str, format_type: str = "PNG"
    ) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        try:
            image.save(filepath, format=format_type)
            print(f"Image successfully saved to: {filepath}")
        except Exception as e:
            print("Something wrong happened while saving file: {e}")
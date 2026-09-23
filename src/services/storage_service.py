import io
from pathlib import Path
from typing import Union
from PIL import Image


class ImageSaver:
    """Utility class to separate file persistence logic from API generation logic (SRP)."""

    @staticmethod
    def save(
        image_data: Union[bytes, Image.Image],
        filepath: Union[str, Path] = "storage/transient/candidate.png",
        format_type: str = "PNG",
    ) -> Path:
        """Saves PIL Image or raw image bytes to disk and returns the verified Path object."""
        target_path = Path(filepath).resolve()
        
        # Guarantee parent directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if isinstance(image_data, bytes):
                # Convert raw API bytes into a PIL Image instance
                image = Image.open(io.BytesIO(image_data))
            elif isinstance(image_data, Image.Image):
                image = image_data
            else:
                raise TypeError(f"Unsupported image_data type: {type(image_data)}")

            image.save(target_path, format=format_type)
            print(f"Image successfully saved to: {target_path}")
            return target_path

        except Exception as e:
            print(f"Something wrong happened while saving file: {e}")
            raise e
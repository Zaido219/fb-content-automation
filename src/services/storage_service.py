import io
from pathlib import Path
from typing import Union
from PIL import Image
import secrets
import string


class ImageSaver:
    """Utility class to separate file persistence logic from API generation logic (SRP)."""

    _MAX_TRANSIENT_IMAGES = 3

    @staticmethod
    def save(
        image_data: Union[bytes, Image.Image],
        format_type: str = "PNG",
    ) -> Path:
        """Saves PIL Image or raw image bytes to disk and returns the verified Path object."""
        filename = f"{ImageSaver._generate_filename()}.png" #this line assume that we will forever be using png's
        filepath: Union[str, Path] = f"storage/transient/{filename}"
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
            ImageSaver._limit_transient_images(target_path.parent)
            print(f"Image successfully saved to: {target_path}")
            return target_path

        except Exception as e:
            print(f"Something wrong happened while saving file: {e}")
            raise e

    @staticmethod
    def _limit_transient_images(directory: Path) -> None:
        """Remove the oldest PNG files so the transient folder keeps at most three."""
        images = sorted(
            (path for path in directory.glob("*.png") if path.is_file()),
            key=lambda path: (path.stat().st_mtime, path.name),
        )
        excess_count = len(images) - ImageSaver._MAX_TRANSIENT_IMAGES
        for image_path in images[:max(0, excess_count)]:
            image_path.unlink()
    
    @staticmethod
    def _generate_filename() -> str:
        """Private method to generate randomized file name"""
        alphabet = string.ascii_letters + string.digits
        random_string = ''.join(secrets.choice(alphabet) for _ in range(16))
        return random_string

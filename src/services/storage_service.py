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
        filename = ImageSaver._name_file(format_type)

        target_path = ImageSaver._create_directory(filename)
        image = ImageSaver._normalize_image(image_data)

        try:
            image.save(target_path, format=format_type)
        except Exception as exc:
            raise RuntimeError(f"Failed to save image to {target_path}") from exc
        
        ImageSaver._limit_transient_images(target_path.parent)
        print(f"Image successfully saved to: {target_path}")
        return target_path


    @staticmethod
    def _create_directory(filename:str):
            directory = Path("storage/transient")
            directory.mkdir(parents=True,exist_ok=True)

            return directory / filename

    @staticmethod
    def _name_file(format_type:str):
        filename = f"{ImageSaver._generate_filename()}.{format_type.lower()}"
        
        return filename 


    @staticmethod
    def _normalize_image(image_data) :
        if isinstance(image_data, bytes):
            # Convert raw API bytes into a PIL Image instance
            image = Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, Image.Image):
            image = image_data
        else:
            raise TypeError(f"Unsupported image_data type: {type(image_data)}")

        return image

        
    @staticmethod
    def _limit_transient_images(directory: Path, extension: set[str] | None = None) -> None:
        allowed_extensions = extension or {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}

        images = sorted(
            (
                path for path in directory.iterdir()
                if path.is_file() and path.suffix.lower() in allowed_extensions 
            ),
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

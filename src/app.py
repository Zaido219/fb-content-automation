import os
from pathlib import Path
from dotenv import load_dotenv

from src.builders.prompt_builder import PromptBuilder
from src.services.facebook_service import FacebookPoster
from src.services.imagen_service import ImagenClientWrapper
from src.services.storage_service import ImageSaver

load_dotenv()

if __name__ == "__main__":
    FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
    FB_PAGE_ID = os.getenv("FB_PAGE_ID")

    if not FB_ACCESS_TOKEN:
        raise ValueError("Missing FB_ACCESS_TOKEN environment variable")

    if not FB_PAGE_ID:
        raise ValueError("Missing FB_PAGE_ID environment variable")

    builder = PromptBuilder()
    image_saver = ImageSaver()
    client = ImagenClientWrapper()
    facebook_poster = FacebookPoster(FB_ACCESS_TOKEN, FB_PAGE_ID)

    print("Building payload...")
    payload = builder.orchestrate("Goku eating fishballs at a street food cart in Manila")

    print("Generating image from Imagen...")
    images = client.generate_image_from_payload(payload)

    # Ensure output path exists
    project_root = Path(__file__).resolve().parent.parent
    target_dir = project_root / "storage" / "approved"
    target_dir.mkdir(parents=True, exist_ok=True)  # Guarantees the directory exists

    output_filepath = target_dir / "goku_fishballs.png"

    if images:
        # Check whether ImageSaver uses instance or class methods
        image_saver.save(images[0], str(output_filepath))
        print(f"Image successfully generated and saved to: {output_filepath}")
    else:
        print("Imagen returned no image data.")
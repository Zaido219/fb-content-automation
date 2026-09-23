import os
from pathlib import Path
from src.builders.prompt_builder import PromptBuilder
from src.services.imagen_service import ImagenClientWrapper
from src.services.storage_service import ImageSaver
from src.services.facebook_service import FacebookPoster
from dotenv import load_dotenv


load_dotenv()

if __name__ == "__main__":
    FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
    FB_PAGE_ID = os.getenv("FB_PAGE_ID")

    if not FB_ACCESS_TOKEN:
        raise ValueError("Missing fb_access_token")

    if not FB_PAGE_ID:
        raise ValueError("Missing fb_page_id")

    
    builder = PromptBuilder()
    image_saver = ImageSaver()
    client = ImagenClientWrapper()
    facebook_poster = FacebookPoster(FB_ACCESS_TOKEN, FB_PAGE_ID)

    payload = builder.orchestrate("Goku eating fishballs at a street food cart in Manila")
    images = client.generate_image_from_payload(payload)

    project_root = Path(__file__).resolve().parent.parent
    target_dir = project_root/ "storage"/ "approved"
    output_filepath = target_dir / "goku_fishballs.png"

    if images:
        ImageSaver.save(images[0], str(output_filepath))
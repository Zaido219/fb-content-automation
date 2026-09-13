import os
from pathlib import Path
from src.builders.prompt_builder import PromptBuilder
from src.services.imagen_service import ImagenClientWrapper
from src.services.storage_service import ImageSaver

if __name__ == "__main__":
    builder = PromptBuilder()
    image_saver = ImageSaver()
    client = ImagenClientWrapper()

    payload = builder.orchestrate("Goku eating fishballs at a street food cart in Manila")
    images = client.generate_image_from_payload(payload)

    project_root = Path(__file__).resolve().parent.parent
    target_dir = project_root/ "storage"/ "approved"
    output_filepath = target_dir / "goku_fishballs.png"

    if images:
        ImageSaver.save(images[0], str(output_filepath))
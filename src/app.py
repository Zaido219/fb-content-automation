from builders.prompt_builder import PromptBuilder
from services.imagen_service import ImagenClientWrapper


if __name__ == "__main__":
    pb = PromptBuilder()
    icw = ImagenClientWrapper()

    creative_brief = pb.orchestrate("Goku eating fishballs at a street food cart in Manila")
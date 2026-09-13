from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ImageGenerationPayload:
    """Explicit contract between PromptBuilder and ImagenClientWrapper."""
    prompt:str
    negative_prompt: Optional[str] = None
    aspect_ratio: str = "1.1"
    output_mime_type = "image/png"
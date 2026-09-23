from abc import ABC, abstractmethod
from typing import Any, Dict, Union
from pathlib import Path

# allows for broader platform support in the future
class SocmedInterface(ABC):
    """Public contract for social media integration platforms."""
    @abstractmethod
    def publish_post_item(self,message:str, **kwargs:Any) -> Dict[str, Any]:
        """Publishes text content to the platform.
        Args:
            message: The primary text content of the post.
            **kwargs: Platform-specific options (e.g., media_ids, links).

        Returns:
            Dict containing standard response data (e.g., platform_post_id,
            status).
        """
        pass
    @abstractmethod
    def publish_photo_item(self,image_path:Union[str, Path], caption:str, **kwargs:Any):
        "Publishes photo contents to the platform"
        pass


class AppError(Exception):
    """Base exception for fb-content-automation."""
    pass
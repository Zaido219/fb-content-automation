import os
from pathlib import Path
from typing import Any, Union
import requests

from src.exceptions.exceptions import GraphAPIError
from src.interface.interface import SocmedInterface


class FacebookPoster(SocmedInterface):
    def __init__(self,access_token: str,page_id: str,api_version: str = "v20.0",session: requests.Session | None = None,):
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = f"https://graph.facebook.com/{api_version}"
        self.session = session or requests.Session()

    def _make_request(self, endpoint: str, payload: dict[str, Any], files: dict[str, Any] | None = None) -> dict[str, Any]:
        """Single internal engine for ALL Graph API POST requests.
        Handles execution, file attachment, response parsing, and unified error translation.
        """
        if not endpoint:
            raise ValueError("Endpoint cannot be null or empty")
        if payload is None:
            raise ValueError("Payload cannot be null")

        url = f"{self.base_url}/{endpoint}"
        request_payload = payload.copy()
        request_payload["access_token"] = self.access_token

        try:
            # Passes files directly to requests; if files is None, requests ignores it
            response = self.session.post(
                url, data=request_payload, files=files, timeout=30
            )
            try:
                data = response.json()
            except ValueError:
                response.raise_for_status()
                raise GraphAPIError(
                    f"Unexpected non-JSON response from server (HTTP {response.status_code})"
                )
            if "error" in data:
                error_info = data["error"]
                error_msg = error_info.get("message", "Unknown GraphAPI error")
                error_code = error_info.get("code")
                raise GraphAPIError(message=f"Facebook API Error [{error_code}]: {error_msg}",code=error_code,)
            
            response.raise_for_status()

            return data
        
        except requests.exceptions.RequestException as err:
            raise GraphAPIError(f"Network request failed: {err}") from err

    def publish_post_item(self, message: str, **kwargs: Any) -> dict[str, Any]:
        """Publishes text posts to /{page_id}/feed."""
        endpoint = f"{self.page_id}/feed"
        payload = {"message": message}
        payload.update(kwargs)
        return self._make_request(endpoint, payload)

    def publish_photo_item(self, image_path: Union[str, Path], caption: str = "", **kwargs: Any) -> dict[str, Any]:
        """Publishes binary photo files to /{page_id}/photos."""
        path = Path(image_path)

        if not path.is_file():
            raise FileNotFoundError(f"Image file not found at path: {path}")

        endpoint = f"{self.page_id}/photos"
        payload = {"caption": caption}
        payload.update(kwargs)
        # Context manager guarantees file stream closes safely after _make_request completes or fails
        with open(path, "rb") as image_file:
            files = {"source": image_file}
            return self._make_request(endpoint, payload, files=files)
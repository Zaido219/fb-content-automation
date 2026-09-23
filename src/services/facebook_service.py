import requests
from src.interface.interface import SocmedInterface
from typing import Optional


class FacebookPoster(SocmedInterface):
    def __init__(self, access_token:str, page_id:str, api_version:str = "v20.0",session: requests.Session | None = None):
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = f"https://graph.facebook.com/{api_version}"
        # inject an existing session or default to a new one
        self.session = session or requests.Session()

    def _make_request(self, endpoint:str, payload:dict):
        """Internal helper responsible for sending HTTP POST requests to
        Facebook.
        """
        if not endpoint:
            raise ValueError("endpoint cannot be null")
        if payload is None:
            raise ValueError("payload cannot be null")

        
        url = f"{self.base_url}/{endpoint}"

        request_payload = payload.copy()
        request_payload["access_token"] = self.access_token
        # send post request
        response = self.session.post(url, data=payload, timeout=10)
        # raise an error if Facebook returns 4xx or 5xx status code
        parsed_response = response.json9
        response.raise_for_status()

        return response.json()

    def publish_post_item(self, message:str, **kwargs):
        endpoint = f"{self.page_id}/feed"
        payload={"message":message}
        # include optional **kwargs
        payload.update(kwargs)

        return self._make_request(endpoint, payload)
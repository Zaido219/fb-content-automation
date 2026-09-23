import requests
from src.interface.interface import SocmedInterface
from src.exceptions.exceptions import GraphAPIError


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
        try:
            response = self.session.post(
                url,data=request_payload, timeout=10
            )
            # first attempt to parse json
            try:
                data = response.json()
            except ValueError:
                response.raise_for_status()
                raise GraphAPIError(
                    f"Unexpected non-JSON response from server (HTTP {response.status_code})"
                )
            # check for facebook's explicit json error object
            if "error" in data:
                error_info = data["error"]
                error_msg = error_info.get("message", "Unknwon GraphApi error")
                error_code = error_info.get("code")
                # Raise custom exception with API details (works for HTTP 200, 4xx, and 5xx)
                raise GraphAPIError(
                    message=f"Facebook API Error [{error_code}]: {error_msg}",
                    code=error_code,
                )
            # Backup check for standard HTTP 4xx/5xx status codes without an "error" key
            response.raise_for_status()

        except requests.exceptions.RequestException as err:
            # Catch connection errors, timeouts, or raise_for_status failures
            raise GraphAPIError(f"Network request failed: {err}") from err

        return data


    def publish_post_item(self, message:str, **kwargs):
        """Post text post"""
        endpoint = f"{self.page_id}/feed"
        payload={"message":message}
        # include optional **kwargs
        payload.update(kwargs)

        return self._make_request(endpoint, payload)
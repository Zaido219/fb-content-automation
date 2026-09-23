from src.interface.interface import AppError

class GraphAPIError(AppError):
    """Custom exception for Facebook Graph API failures."""

    def __init__(self, message: str, code: int | None = None):
        super().__init__(message)
        self.code = code
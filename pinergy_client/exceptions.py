"""Client exceptions."""


class PinergyAPIError(Exception):
    """Raised when the API returns an error (success=false or non-2xx)."""

    def __init__(self, message: str, status_code: int | None = None, body: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body or {}


class PinergyAuthError(PinergyAPIError):
    """Raised when authentication fails or token is missing/invalid."""

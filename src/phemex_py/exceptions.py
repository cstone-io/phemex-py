class PhemexError(Exception):
    """Base exception for all Phemex-related errors."""

    _default_message = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        cause: Exception | None = None,
        context: dict | None = None,
    ):
        self.message = message or self._default_message
        self.cause = cause
        self.context = context
        super().__init__(self.message)

    def __str__(self) -> str:
        parts = [f"{self.__class__.__name__}: {self.message}"]
        if self.cause:
            parts.append(f"Cause={self.cause!r}")
        if self.context:
            parts.append(f"Context={self.context}")
        return " | ".join(parts)


class ValidationError(PhemexError):
    """Input validation failed."""


class AuthenticationError(PhemexError):
    """Invalid or missing API credentials."""

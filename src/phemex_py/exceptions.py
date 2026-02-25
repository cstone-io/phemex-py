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


class PhemexAPIError(PhemexError):
    """Business-level error returned by the Phemex API (code != 0)."""

    def __init__(self, code: int, msg: str, data: dict | None = None):
        self.code = code
        self.msg = msg
        super().__init__(
            message=f"[{code}] {msg}",
            context={"code": code, "msg": msg, "data": data},
        )


class InsufficientMarginError(PhemexAPIError):
    """Insufficient margin to place or maintain the order."""


class OrderNotFoundError(PhemexAPIError):
    """The referenced order was not found."""


class DuplicateOrderError(PhemexAPIError):
    """Duplicate clOrdID — order already exists."""


class RateLimitExceededError(PhemexAPIError):
    """API rate limit exceeded."""


class InvalidPriceError(PhemexAPIError):
    """Order price is invalid or out of range."""


class PositionModeError(PhemexAPIError):
    """Position mode conflict (e.g. wrong posSide for current mode)."""


# Phemex business error code → exception class mapping.
# Codes sourced from Phemex docs and empirical observation.
_ERROR_CODE_MAP: dict[int, type[PhemexAPIError]] = {
    10001: RateLimitExceededError,
    11001: InsufficientMarginError,
    11004: InsufficientMarginError,
    11006: InsufficientMarginError,
    11082: InsufficientMarginError,
    30018: InvalidPriceError,
    30019: InvalidPriceError,
    35004: OrderNotFoundError,
    35014: DuplicateOrderError,
    39201: PositionModeError,
    39995: PositionModeError,
    39996: PositionModeError,
}


def raise_for_business_error(data: dict) -> None:
    """Raise a typed PhemexAPIError if the response envelope contains a non-zero code."""
    if not isinstance(data, dict) or "code" not in data:
        return
    code = data["code"]
    if code == 0:
        return
    msg = data.get("msg", "Unknown error")
    exc_cls = _ERROR_CODE_MAP.get(code, PhemexAPIError)
    raise exc_cls(code=code, msg=msg, data=data.get("data"))

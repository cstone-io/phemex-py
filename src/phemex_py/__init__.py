import logging

from .client import PhemexClient, AsyncPhemexClient, PhemexKind
from .core import PhemexDecimal, PhemexModel, PhemexRequest, PhemexResponse
from .exceptions import PhemexError, ValidationError, AuthenticationError
from .biz_errors import (
    PhemexBizError,
    DuplicateRequestError,
    DuplicateOrderError,
    OrderNotFoundError,
    OrderStateError,
    InsufficientBalanceError,
    LeverageRiskLimitError,
    PositionMarginError,
    ReduceOnlyError,
    InvalidOrderParamError,
    ConditionalOrderError,
    TakeProfitStopLossError,
    TrailingOrderError,
    BracketOrderError,
    AccountStatusError,
    RoutingError,
    WalletError,
    FeeRangeError,
    MarketDataUnavailableError,
    RpiError,
    raise_for_biz_error,
)

logging.getLogger("phemex_py").addHandler(logging.NullHandler())
logging.getLogger("phemex_py").setLevel(logging.WARNING)

__version__ = "0.3.0"
__all__ = [
    # Core
    "PhemexDecimal",
    "PhemexModel",
    "PhemexRequest",
    "PhemexResponse",
    # Client
    "PhemexKind",
    "PhemexClient",
    "AsyncPhemexClient",
    # Infrastructure exceptions
    "PhemexError",
    "ValidationError",
    "AuthenticationError",
    # Business errors
    "PhemexBizError",
    "DuplicateRequestError",
    "DuplicateOrderError",
    "OrderNotFoundError",
    "OrderStateError",
    "InsufficientBalanceError",
    "LeverageRiskLimitError",
    "PositionMarginError",
    "ReduceOnlyError",
    "InvalidOrderParamError",
    "ConditionalOrderError",
    "TakeProfitStopLossError",
    "TrailingOrderError",
    "BracketOrderError",
    "AccountStatusError",
    "RoutingError",
    "WalletError",
    "FeeRangeError",
    "MarketDataUnavailableError",
    "RpiError",
    "raise_for_biz_error",
]

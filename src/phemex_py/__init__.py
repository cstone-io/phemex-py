import logging

from .client import PhemexClient, AsyncPhemexClient, PhemexKind
from .core import PhemexDecimal, PhemexModel, PhemexRequest, PhemexResponse
from .exceptions import PhemexError, PhemexAPIError

logging.getLogger("phemex_py").addHandler(logging.NullHandler())
logging.getLogger("phemex_py").setLevel(logging.WARNING)

__version__ = "0.2.0"
__all__ = [
    "PhemexDecimal",
    "PhemexModel",
    "PhemexRequest",
    "PhemexResponse",
    "PhemexKind",
    "PhemexClient",
    "AsyncPhemexClient",
    "PhemexError",
    "PhemexAPIError",
]

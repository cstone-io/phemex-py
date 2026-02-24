import logging

from .client import PhemexClient, AsyncPhemexClient, PhemexKind
from .core import PhemexDecimal, PhemexModel
from .exceptions import PhemexError

logging.getLogger("phemex_py").addHandler(logging.NullHandler())
logging.getLogger("phemex_py").setLevel(logging.WARNING)

__version__ = "0.1.1"
__all__ = [
    "PhemexDecimal",
    "PhemexModel",
    "PhemexKind",
    "PhemexClient",
    "AsyncPhemexClient",
    "PhemexError"]

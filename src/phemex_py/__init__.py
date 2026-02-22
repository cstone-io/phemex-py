import logging

from .client import PhemexClient, AsyncPhemexClient
from .core import PhemexDecimal, PhemexModel
from .exceptions import PhemexError

logging.getLogger("phemex_py").addHandler(logging.NullHandler())
logging.getLogger("phemex_py").setLevel(logging.WARNING)

__version__ = "0.1.0"
__all__ = [
    "PhemexDecimal",
    "PhemexModel",
    "PhemexClient",
    "AsyncPhemexClient",
    "PhemexError"]

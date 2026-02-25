import json
from typing import Any, Literal, Self
from urllib.parse import quote

from pydantic import BaseModel

from .models import PhemexModel

type RequestData = dict[str, Any] | PhemexModel | None


class Request(BaseModel):
    """Helper to build Phemex API requests."""
    method: Literal["GET", "POST", "PUT", "DELETE"]
    path: str
    params: RequestData = None
    body: RequestData = None

    def dump(self, field: Literal["params", "body"]) -> dict | None:
        """Returns attribute as a dictionary"""
        attr = getattr(self, field)
        if attr is None:
            return None

        if isinstance(attr, dict):
            return attr

        dumpage = attr.model_dump(exclude_none=True)
        return dumpage

    def build_body_json(self) -> str:
        body = self.dump("body")
        if not body:
            return ""

        return json.dumps(body, separators=(",", ":"))

    def build_query_string(self) -> str:
        """Build deterministic query string WITHOUT leading '?'"""
        params = self.dump("params")
        if not params:
            return ""

        parts = []
        for k, v in params.items():
            if isinstance(v, list):
                for item in v:  # repeat the key for each value
                    if isinstance(item, bool):
                        item = str(item).lower()
                    parts.append(f"{k}={quote(str(item), safe='')}")
            else:
                if isinstance(v, bool):
                    v = str(v).lower()
                parts.append(f"{k}={quote(str(v), safe='')}")

        return "&".join(parts)

    # ----------- factory methods -----------
    @classmethod
    def get(cls, path: str, params: RequestData = None):
        return cls(method="GET", path=path, params=params)

    @classmethod
    def post(cls, path: str, body: RequestData = None, params: RequestData = None):
        return cls(method="POST", path=path, body=body, params=params)

    @classmethod
    def put(cls, path: str, params: RequestData = None, body: RequestData = None):
        return cls(method="PUT", path=path, params=params, body=body)

    @classmethod
    def delete(cls, path: str, params: RequestData = None):
        return cls(method="DELETE", path=path, params=params)


class Extractor:
    """
    Helper to extract data from nested API responses. Supports chaining operations.
    """

    def __init__(self, resp: dict):
        """
        Initialize the Extractor with the response data.
        :param resp: response result (JSON) from the API
        """
        self.resp = resp
        self.operations: list[str | int] = []

    def key(self, *key: str) -> Self:
        """
        Extract a value by key from a dictionary.
        """
        self.operations.extend(key)
        return self

    def first(self) -> Self:
        """
        Extract the first element from a list.
        """
        self.operations.append(0)
        return self

    def head(self, n: int) -> Self:
        """
        Extract the first n elements from a list. Returns a list, unlike
        first() which returns the element itself.
        """
        self.operations.append(slice(n))
        return self

    def extract(self):
        """
        Execute the extraction operations on the response data.
        """
        result = self.resp
        for op in self.operations:
            if isinstance(op, str) and isinstance(result, dict):
                result = result[op]

            elif isinstance(op, int) and isinstance(result, list):
                if op >= len(result):
                    raise IndexError("List index out of range")
                result = result[op]

            elif isinstance(op, slice) and isinstance(result, list):
                result = result[op]

        return result

    def data(self):
        """
        Shortcut to extract the 'data' key from the response as this is the
        most common response envelope.
        """
        return self.key("data").extract()

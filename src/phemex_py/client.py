import hmac
import hashlib
import logging
import time
from typing import Literal

import httpx

from .core.requests import Request, Extractor
from .exceptions import PhemexError

from .usdm_rest import USDMRest, AsyncUSDMRest

logger = logging.getLogger(__name__)

_SENSITIVE_HEADERS = {"x-phemex-access-token", "x-phemex-request-signature"}
_EXPIRY = 60  # default expiry time in seconds for request signatures

PhemexKind = Literal["vip", "public", "test"]

_BASE_URLS: dict[str, str] = {
    "vip": "https://vapi.phemex.com",
    "public": "https://api.phemex.com",
    "test": "https://testnet-api.phemex.com",
}


class BasePhemexClient:
    """
    Shared state and request preparation for sync and async Phemex clients.
    """

    def __init__(self, kind: PhemexKind, api_key: str, api_secret: str):
        self.base_url = _BASE_URLS[kind]
        self.api_key = api_key
        self.api_secret = api_secret.encode()

    def _prepare(self, req: Request) -> tuple[str, dict, bytes | None]:
        """
        Build the URL, signed headers, and encoded body for a request.

        :return: (url, headers, content)
        """
        query = req.build_query_string()
        body_json = req.build_body_json()

        expires = int(time.time()) + _EXPIRY
        parts = [req.path]
        if query:
            parts.append(query)
        parts.append(str(expires))
        if body_json:
            parts.append(body_json)

        payload = "".join(parts)
        signature = hmac.new(
            self.api_secret,
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "x-phemex-access-token": self.api_key,
            "x-phemex-request-expiry": str(expires),
            "x-phemex-request-signature": signature,
        }

        url = f"{self.base_url}{req.path}"
        if query:
            url = f"{url}?{query}"

        if body_json:
            headers["Content-Type"] = "application/json"

        safe_headers = {k: v for k, v in headers.items() if k not in _SENSITIVE_HEADERS}
        logger.debug("REQUEST")
        logger.debug(f"Request: {req.method} {url}")
        logger.debug(f"Headers: {safe_headers}")
        logger.debug(f"Body: {body_json or None}")

        content = body_json.encode("utf-8") if body_json else None
        return url, headers, content

    @staticmethod
    def _handle_response(resp: httpx.Response, req: Request, url: str, body_json: str | None):
        """
        Raise PhemexError on HTTP errors and return parsed JSON on success.
        """
        logger.debug("RESPONSE")
        logger.debug(f"Status Code: {resp.status_code}")
        logger.debug(f"Response Text: {resp.text}")

        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise PhemexError(
                message="Phemex API request failed",
                cause=e,
                context={
                    "request": {
                        "method": req.method,
                        "url": url,
                        "body": body_json or None,
                    },
                    "response": {
                        "status_code": resp.status_code,
                        "text": resp.text,
                    },
                }
            )

        return resp.json()


class PhemexClient(BasePhemexClient):
    """
    Sync client for Phemex API (https://phemex-docs.github.io/). Built using httpx.Client.
    """

    def __init__(self, kind: PhemexKind, api_key: str, api_secret: str):
        super().__init__(kind, api_key, api_secret)
        self.session = httpx.Client()
        self.usdm_rest = USDMRest(self)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        """Close the underlying HTTP session."""
        self.session.close()

    def request(self, req: Request):
        """
        Make an authenticated request to Phemex API.

        :param req: Request object
        :return: Parsed JSON response.
        """
        url, headers, content = self._prepare(req)
        resp = self.session.request(method=req.method, url=url, headers=headers, content=content)
        return self._handle_response(resp, req, url, req.build_body_json())

    # ----------------------------------------
    # Common endpoints shared across APIs
    # ----------------------------------------

    def server_time(self, ms: bool = True) -> int:
        """
        Fetch current Phemex server time (ms by default). For details, see:
        https://phemex-docs.github.io/#query-server-time-2
        """
        req = Request.get("/public/time")
        resp = self.request(req)
        timestamp = Extractor(resp).key("data", "serverTime").extract()
        return timestamp if ms else timestamp // 1000


class AsyncPhemexClient(BasePhemexClient):
    """
    Async client for Phemex API (https://phemex-docs.github.io/). Built using httpx.AsyncClient.
    """

    def __init__(self, kind: PhemexKind, api_key: str, api_secret: str):
        super().__init__(kind, api_key, api_secret)
        self.session = httpx.AsyncClient()
        self.usdm_rest = AsyncUSDMRest(self)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self):
        """Close the underlying async HTTP session."""
        await self.session.aclose()

    async def request(self, req: Request):
        """
        Make an authenticated request to Phemex API.

        :param req: Request object
        :return: Parsed JSON response.
        """
        url, headers, content = self._prepare(req)
        resp = await self.session.request(method=req.method, url=url, headers=headers, content=content)
        return self._handle_response(resp, req, url, req.build_body_json())

    # ----------------------------------------
    # Common endpoints shared across APIs
    # ----------------------------------------

    async def server_time(self, ms: bool = True) -> int:
        """
        Fetch current Phemex server time (ms by default). For details, see:
        https://phemex-docs.github.io/#query-server-time-2
        """
        req = Request.get("/public/time")
        resp = await self.request(req)
        timestamp = Extractor(resp).key("data", "serverTime").extract()
        return timestamp if ms else timestamp // 1000

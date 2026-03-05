import os
import time

import pytest
import pytest_asyncio

from phemex_py.biz_errors import PhemexBizError as PhemexAPIError
from phemex_py.client import PhemexClient, AsyncPhemexClient
from phemex_py.usdm_rest.models import PlaceOrderRequest


def pytest_collection_modifyitems(config, items):
    """Special hook from pytest to mark integration tests."""
    for item in items:
        if "tests/__integration__" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def symbol():
    val = os.getenv("INTEGRATION_TEST_SYMBOL")
    if not val:
        pytest.skip("INTEGRATION_TEST_SYMBOL must be set")
    return val


@pytest.fixture(scope="session")
def qty():
    val = os.getenv("INTEGRATION_TEST_QTY")
    if not val:
        pytest.skip("INTEGRATION_TEST_QTY must be set")
    return val


@pytest.fixture(scope="session")
def lmt_price():
    val = os.getenv("INTEGRATION_TEST_LMT_PRICE")
    if not val:
        pytest.skip("INTEGRATION_TEST_LMT_PRICE must be set")
    return val


@pytest.fixture(scope="session")
def client():
    """Real phemex connected to Phemex testnet."""
    kind = os.getenv("PHEMEX_KIND", "test")
    api_key = os.getenv("PHEMEX_KEY")
    api_secret = os.getenv("PHEMEX_SECRET")

    if not api_key or not api_secret:
        pytest.skip("PHEMEX_KEY and PHEMEX_SECRET must be set in environment")

    client = PhemexClient(kind=kind, api_key=api_key, api_secret=api_secret)
    yield client
    client.close()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def async_client():
    """Real async phemex connected to Phemex testnet."""
    kind = os.getenv("PHEMEX_KIND", "test")
    api_key = os.getenv("PHEMEX_KEY")
    api_secret = os.getenv("PHEMEX_SECRET")

    if not api_key or not api_secret:
        pytest.skip("PHEMEX_KEY and PHEMEX_SECRET must be set in environment")

    client = AsyncPhemexClient(kind=kind, api_key=api_key, api_secret=api_secret)
    yield client
    await client.close()


def _cleanup(client, symbol):
    """Cancel all orders and close any open position for the test symbol."""
    try:
        client.usdm_rest.cancel_all(symbol=symbol)
    except PhemexAPIError:
        pass
    time.sleep(0.5)

    try:
        pos_resp = client.usdm_rest.positions()
        for pos in pos_resp.positions:
            if pos.symbol == symbol and pos.signed_size != 0:
                side = "Buy" if pos.signed_size < 0 else "Sell"
                abs_qty = str(abs(pos.signed_size))
                close = PlaceOrderRequest(
                    symbol=symbol,
                    side=side,
                    pos_side=pos.pos_side,
                    order_type="Market",
                    quantity=abs_qty,
                    time_in_force="ImmediateOrCancel",
                    reduce_only=True,
                )
                client.usdm_rest.place_order(close)
                time.sleep(0.5)
    except PhemexAPIError:
        pass


@pytest.fixture(scope="session", autouse=True)
def clean_state(client, symbol):
    """Ensure no positions/orders for test symbol at session start and end."""
    _cleanup(client, symbol)
    yield
    _cleanup(client, symbol)


@pytest.fixture(autouse=True)
def cooldown():
    """Throttle tests slightly to avoid CloudFront edge saturation."""
    yield
    time.sleep(0.25)

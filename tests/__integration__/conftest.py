import os
import time

import pytest
import pytest_asyncio

from phemex_py.client import PhemexClient, AsyncPhemexClient


def pytest_collection_modifyitems(config, items):
    """Special hook from pytest to mark integration tests."""
    for item in items:
        if "tests/__integration__" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def client():
    """Real phemex connected to Phemex testnet."""
    api_url = os.getenv("PHEMEX_URL")
    api_key = os.getenv("PHEMEX_KEY")
    api_secret = os.getenv("PHEMEX_SECRET")

    if not api_key or not api_secret:
        pytest.skip("PHEMEX_KEY and PHEMEX_SECRET must be set in environment")

    client = PhemexClient(base_url=api_url, api_key=api_key, api_secret=api_secret)
    yield client
    client.close()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def async_client():
    """Real async phemex connected to Phemex testnet."""
    api_url = os.getenv("PHEMEX_URL")
    api_key = os.getenv("PHEMEX_KEY")
    api_secret = os.getenv("PHEMEX_SECRET")

    if not api_key or not api_secret:
        pytest.skip("PHEMEX_KEY and PHEMEX_SECRET must be set in environment")

    client = AsyncPhemexClient(base_url=api_url, api_key=api_key, api_secret=api_secret)
    yield client
    await client.close()


@pytest.fixture(autouse=True)
def cooldown():
    """Throttle tests slightly to avoid CloudFront edge saturation."""
    yield
    time.sleep(0.25)

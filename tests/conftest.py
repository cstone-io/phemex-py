from dotenv import load_dotenv
import pytest


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables from .env before any tests run."""
    load_dotenv()

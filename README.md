# phemex-py

[![PyPI version](https://img.shields.io/pypi/v/phemex-py)](https://pypi.org/project/phemex-py/)
[![Python](https://img.shields.io/pypi/pyversions/phemex-py)](https://pypi.org/project/phemex-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Typed, production-grade Python SDK for the [Phemex](https://phemex.com) crypto exchange API.

- Sync and async clients (built on [httpx](https://www.python-httpx.org/))
- Fully typed request/response models (built on [Pydantic](https://docs.pydantic.dev/))
- USD-M perpetual futures: orders, positions, market data, funding rates, and more

## Installation

```bash
pip install phemex-py
```

## Quick Start

### Authentication

You need a Phemex API key and secret. Create one from
your [Phemex account settings](https://phemex.com/account/apiKeys).

Set them as environment variables or pass them directly:

```dotenv
PHEMEX_URL=https://testnet-api.phemex.com
PHEMEX_KEY=
PHEMEX_SECRET=
```

### Sync Client

```python
from phemex_py import PhemexClient

with PhemexClient(
        base_url="https://api.phemex.com",
        api_key="your-api-key",
        api_secret="your-api-secret",
) as client:
    # Get server time
    server_time = client.server_time()

    # Get product info
    products = client.usdm_rest.product_information()

    # Get ticker
    ticker = client.usdm_rest.ticker(symbol="BTCUSDT")

    # Get open orders
    orders = client.usdm_rest.open_orders(symbol="BTCUSDT")

    # Get account positions
    positions = client.usdm_rest.positions()
```

### Async Client

```python
import asyncio
from phemex_py import AsyncPhemexClient


async def main():
    async with AsyncPhemexClient(
            base_url="https://api.phemex.com",
            api_key="your-api-key",
            api_secret="your-api-secret",
    ) as client:
        ticker = await client.usdm_rest.ticker(symbol="BTCUSDT")
        positions = await client.usdm_rest.positions()


asyncio.run(main())
```

### Testnet

Use the testnet base URL for paper trading:

```python
client = PhemexClient(
    base_url="https://testnet-api.phemex.com",
    api_key="your-testnet-key",
    api_secret="your-testnet-secret",
)
```

## API Coverage

### USD-M Perpetual REST API

| Category    | Endpoints                                                                                                           |
|-------------|---------------------------------------------------------------------------------------------------------------------|
| Market Data | `product_information`, `order_book`, `klines`, `trades`, `ticker`, `tickers`                                        |
| Orders      | `place_order`, `amend_order`, `cancel_order`, `bulk_cancel`, `cancel_all`                                           |
| Positions   | `positions`, `positions_with_pnl`, `switch_position_mode`, `set_leverage`, `assign_position_balance`                |
| Account     | `risk_units`                                                                                                        |
| History     | `open_orders`, `closed_orders`, `closed_positions`, `user_trades`, `order_history`, `lookup_order`, `trade_history` |
| Funding     | `funding_fee_history`, `funding_rates`                                                                              |

## Links

- [Phemex API Documentation](https://phemex-docs.github.io/)
- [GitHub Repository](https://github.com/cstone-io/phemex-py)
- [PyPI Package](https://pypi.org/project/phemex-py/)

## License

[MIT](LICENSE.txt)

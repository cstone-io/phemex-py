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
your [Phemex account settings](https://phemex.com/help-center/how-do-i-create-an-api-key).

Setting them as environment variables is a tried and true method:

```dotenv
PHEMEX_KIND=test
PHEMEX_KEY=
PHEMEX_SECRET=
```

The `kind` parameter controls which Phemex environment to connect to:

| Kind     | URL                              |
|----------|----------------------------------|
| `vip`    | `https://vapi.phemex.com`        |
| `public` | `https://api.phemex.com`         |
| `test`   | `https://testnet-api.phemex.com` |

### Sync Client

```python
from phemex_py import PhemexClient

with PhemexClient(
        kind="public",
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
            kind="public",
            api_key="your-api-key",
            api_secret="your-api-secret",
    ) as client:
        ticker = await client.usdm_rest.ticker(symbol="BTCUSDT")
        positions = await client.usdm_rest.positions()


asyncio.run(main())
```

### Testnet

Use `kind="test"` for paper trading:

```python
client = PhemexClient(
    kind="test",
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

## Philosophy

`phemex-py` is a **thin SDK/wrapper** around the Phemex REST API. It handles transport, authentication, serialization,
and type safety so you don't have to — but it intentionally stops there. Trading logic, strategy, and risk management
belong in your code (your "engine"), not in the SDK.

The guiding principle: **if Phemex returns it or requires it, we model it. If it requires judgment or strategy, that's
your job.**

### SDK responsibility (this library)

- Authentication, request signing, rate limit tracking
- Typed request/response models with validation
- Decoding Phemex conventions (e.g. leverage sign → margin mode)
- Convenience factories that prevent invalid API calls
- Computed properties that surface implicit data (`margin_mode`, `effective_leverage`, `signed_size`)

### Engine responsibility (your code)

- **Position normalization** — merging hedged Long/Short into a net position loses information (separate liquidation
  prices, margins, PnL). Whether and how to merge is strategy-dependent.
- **Order routing** — deciding when, what, and how much to trade
- **Risk management** — position sizing, max drawdown, kill switches
- **Retry/reconnect logic** — how to handle transient failures depends on your latency and correctness requirements
- **State management** — tracking fills, reconciling with exchange state

### Example: margin mode

The SDK gives you the building blocks:

```python
pos = client.usdm_rest.positions_with_pnl().get("BTCUSDT")
print(pos.margin_mode)  # "Cross" or "Isolated" — SDK decodes this
print(pos.effective_leverage)  # Always positive — SDK normalizes this

# SDK prevents invalid API calls:
req = SetLeverageRequest.with_margin_mode("BTCUSDT", 10, "Isolated")
```

But deciding *which* margin mode to use, *when* to change leverage, or *whether* to rebalance margin across positions —
that's engine logic.

## Links

- [Phemex API Documentation](https://phemex-docs.github.io/)
- [GitHub Repository](https://github.com/cstone-io/phemex-py)
- [PyPI Package](https://pypi.org/project/phemex-py/)

## License

[MIT](LICENSE.txt)

# Changelog

## 0.1.0 (2026-02-22)

Initial release.

### Features

- Sync and async clients for the Phemex API (`PhemexClient`, `AsyncPhemexClient`)
- HMAC-SHA256 request signing with configurable expiry
- USD-M Perpetual REST API coverage:
  - Market data: product information, order book, klines, trades, tickers
  - Orders: place, amend, cancel, bulk cancel, cancel all
  - Positions: query, query with PnL, switch mode, set leverage, assign balance
  - Account: risk units
  - History: open/closed orders, closed positions, user trades, order history, trade history
  - Funding: fee history, funding rates
- Fully typed request/response models via Pydantic v2
- Structured error handling with `PhemexError`
- PEP 561 typed package support (`py.typed`)

# Changelog

## 0.2.0 (2026-02-25)

### SDK Ergonomics: Position Mode, Leverage & Margin Mode

### Bug Fixes

- Fixed `SetLeverageRequest` validation bug: `short = self.long is not None` now correctly references `self.short`

### Added

- `PositionCore.position_mode` property — semantic alias for `pos_mode` (`"OneWay"` or `"Hedged"`)
- `PositionCore.margin_mode` property — returns `"Cross"` or `"Isolated"` derived from leverage sign convention
- `PositionCore.effective_leverage` property — absolute leverage value (always positive)
- `PositionCore.initial_margin_rate` property — `1 / abs(leverage)`, or `None` for zero (max cross)
- `SwitchModeRequest.make()` factory with `Literal["OneWay", "Hedged"]` constraint
- `SetLeverageRequest.with_margin_mode()` factory — auto-applies Phemex sign convention for Cross/Isolated
- `AssignPositionBalanceRequest.make()` factory — validates position is in Isolated margin mode
- Docstrings documenting Phemex leverage sign convention across risk-related models and endpoints
- Philosophy section in README explaining SDK vs engine responsibilities

### Hardening (from v0.1.1 development cycle)

- Forward compatibility: `extra="ignore"` for responses, `extra="forbid"` for requests
- Typed exceptions for Phemex business error codes (`InsufficientMarginError`, `OrderNotFoundError`, etc.)
- `.client_order_id()` on `OrderBuilder` for idempotent order placement
- Rate limit header parsing (`x-ratelimit-limit`, `x-ratelimit-remaining`, `retry-after`)
- `signed_size` property on `Position` and `PositionWithPnL` (negative for Short)
- Reworked `cancel_all` API to accept single symbol, list, or `None`

## 0.1.1 (2026-02-23)

### Breaking Changes

- `PhemexClient` and `AsyncPhemexClient` now take a `kind` parameter (`"vip"`, `"public"`, or `"test"`) instead of `base_url`
- Removed configurable `expiry` parameter from client constructors

### Added

- `PhemexKind` type alias exported from `phemex_py`
- `_BASE_URLS` module constant mapping kind to base URL

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

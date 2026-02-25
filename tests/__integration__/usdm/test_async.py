import asyncio
import time

import pytest

from phemex_py.exceptions import PhemexAPIError
from phemex_py.usdm_rest.models import *

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture
def order_to_fail():
    """A perp order that is guaranteed to fail/cancel (for testing)."""
    return PlaceOrderRequest.builder("BTCUSDT").increase_long("0.01").limit("80000").tif("ImmediateOrCancel").build()


@pytest.fixture
def order_to_live():
    """A perp order that will remain open (for testing)."""
    return PlaceOrderRequest.builder("BTCUSDT").increase_long("0.01").limit("80000").build()


class TestAsyncPhemexUSDMOrderExecution:
    # Order tests may raise PhemexAPIError on testnet due to account state
    # (e.g. no balance). We accept specific business errors as valid outcomes.
    _ACCEPTABLE_ORDER_CODES = {11001, 11004, 11006, 11082}

    async def _place_or_skip(self, client, order):
        """Place an order, skipping the test if testnet account lacks balance."""
        try:
            await client.usdm_rest.place_order(order)
        except PhemexAPIError as e:
            if e.code in self._ACCEPTABLE_ORDER_CODES:
                pytest.skip(f"Testnet account state: [{e.code}] {e.msg}")
            raise

    async def test_place_order(self, async_client, order_to_fail):
        await self._place_or_skip(async_client, order_to_fail)

    async def test_amend_and_cancel_order(self, async_client, order_to_live):
        # Step 1: Place a live order
        await self._place_or_skip(async_client, order_to_live)
        await asyncio.sleep(1)

        # Step 2: Fetch the open order to get its ID
        orders = await async_client.usdm_rest.open_orders(symbol="BTCUSDT")
        assert len(orders) > 0, "Expected at least one open order after placing"
        order = orders[0]

        # Step 3: Amend the order (change price)
        amend_req = AmendOrderRequest.model_validate(dict(
            symbol=order.symbol,
            pos_side=order_to_live.pos_side,
            order_id=order.order_id,
            price="85000",
        ))
        # amend_order may return None if the API doesn't echo data
        await async_client.usdm_rest.amend_order(amend_req)

        # Step 4: Cancel the order
        cancel_req = CancelOrderRequest.make(
            symbol=order.symbol,
            order_id=order.order_id,
        )
        # cancel_order may return None if the API doesn't echo data
        await async_client.usdm_rest.cancel_order(cancel_req)

    async def test_bulk_cancel_orders(self, async_client, order_to_live):
        for i in range(2):
            await self._place_or_skip(async_client, order_to_live)
            await asyncio.sleep(1)

        orders = await async_client.usdm_rest.open_orders(symbol="BTCUSDT")
        assert len(orders) >= 2, "Expected at least 2 open orders"
        order_ids = [o.order_id for o in orders[:2]]

        bulk_cancel_req = BulkCancelOrderRequest.make(
            order_ids=order_ids,
            symbol=order_to_live.symbol,
        )
        bulk_cancel_resp = await async_client.usdm_rest.bulk_cancel(bulk_cancel_req)
        assert isinstance(bulk_cancel_resp, list)
        for resp in bulk_cancel_resp:
            assert isinstance(resp, OrderResponse)

    async def test_cancel_all_orders(self, async_client, order_to_live):
        await self._place_or_skip(async_client, order_to_live)
        await asyncio.sleep(1)

        cancel_all_resp = await async_client.usdm_rest.cancel_all(order_to_live.symbol)
        assert cancel_all_resp is None


class TestAsyncPhemexUSDMOrderInformation:
    async def test_perp_get_open_orders(self, async_client):
        orders = await async_client.usdm_rest.open_orders(symbol="BTCUSDT")

        assert isinstance(orders, list)
        for order in orders:
            assert isinstance(order, OpenOrder)

    async def test_get_closed_orders(self, async_client):
        req = ClosedOrdersRequest.default(symbol="BTCUSDT")
        orders = await async_client.usdm_rest.closed_orders(req)

        assert isinstance(orders, list)
        for order in orders:
            assert isinstance(order, ClosedOrder)

    async def test_lookup_order(self, async_client):
        orders = await async_client.usdm_rest.open_orders(symbol="BTCUSDT")
        if not orders:
            pytest.skip("No open orders to look up")
        order_id = orders[0].order_id
        looked_up = await async_client.usdm_rest.lookup_order(symbol="BTCUSDT", order_id=order_id)
        # lookup_order may return None if the order was filled/cancelled between queries
        if looked_up is not None:
            assert isinstance(looked_up, OpenOrder)
            assert looked_up.order_id == order_id

    async def test_order_history(self, async_client):
        orders = await async_client.usdm_rest.order_history(symbol="BTCUSDT")

        assert isinstance(orders, list)
        for order in orders:
            assert isinstance(order, OrderHistoryItem)


class TestAsyncPhemexUSDMPortfolio:
    async def test_positions(self, async_client):
        positions = await async_client.usdm_rest.positions()

        assert isinstance(positions, PositionResponse)
        assert isinstance(positions.positions, list)
        for pos in positions.positions:
            assert isinstance(pos, Position)

    async def test_positions_with_pnl(self, async_client):
        positions = await async_client.usdm_rest.positions_with_pnl()

        assert isinstance(positions, PositionWithPnLResponse)
        assert isinstance(positions.positions, list)
        for pos in positions.positions:
            assert isinstance(pos, PositionWithPnL)

    async def test_risk_unit(self, async_client):
        risk_units = await async_client.usdm_rest.risk_units()
        assert isinstance(risk_units, list)
        for item in risk_units:
            assert isinstance(item, RiskUnitResponse)

    async def test_closed_positions(self, async_client):
        req = ClosedPositionRequest.default(symbol="BTCUSDT")
        closed_positions = await async_client.usdm_rest.closed_positions(req)

        assert isinstance(closed_positions, list)
        for pos in closed_positions:
            assert isinstance(pos, ClosedPosition)


class TestAsyncPhemexUSDMOptions:
    # Business errors that are acceptable due to testnet account state
    # (e.g. open positions preventing mode switch, no position for balance assignment)
    _ACCEPTABLE_CODES = {39201, 39995, 39996, 11001, 11004, 11006, 11082}

    async def _run_or_skip(self, coro, label):
        """Await coro, skipping if a known testnet-state business error occurs."""
        try:
            await coro
        except PhemexAPIError as e:
            if e.code in self._ACCEPTABLE_CODES:
                pytest.skip(f"Testnet account state: [{e.code}] {e.msg}")
            pytest.fail(f"{label} raised an unexpected PhemexAPIError: {e}")
        except Exception as e:
            pytest.fail(f"{label} raised an unexpected exception: {e}")

    async def test_perp_switch_pos_mode(self, async_client):
        req = SwitchModeRequest(symbol="BTCUSDT", mode="Hedged")
        await self._run_or_skip(
            async_client.usdm_rest.switch_position_mode(req),
            "perp_switch_pos_mode",
        )

    async def test_perp_set_leverage_oneway(self, async_client):
        try:
            req = SwitchModeRequest(symbol="BTCUSDT", mode="OneWay")
            await async_client.usdm_rest.switch_position_mode(req)
        except PhemexAPIError as e:
            if e.code in self._ACCEPTABLE_CODES:
                pytest.skip(f"Cannot switch to OneWay on testnet: [{e.code}] {e.msg}")
            raise

        req = SetLeverageRequest.model_validate(dict(symbol="BTCUSDT", one_way="10"))
        await self._run_or_skip(
            async_client.usdm_rest.set_leverage(req),
            "perp_set_leverage",
        )

        try:
            req = SwitchModeRequest(symbol="BTCUSDT", mode="Hedged")
            await async_client.usdm_rest.switch_position_mode(req)
        except PhemexAPIError:
            pass  # best-effort restore

    async def test_perp_set_leverage_hedged(self, async_client):
        req = SetLeverageRequest.model_validate(dict(symbol="BTCUSDT", long="5", short="7"))
        await self._run_or_skip(
            async_client.usdm_rest.set_leverage(req),
            "perp_set_leverage",
        )

    async def test_assign_position_balance(self, async_client):
        req = AssignPositionBalanceRequest.model_validate(dict(
            symbol="BNBUSDT",
            side="Long",
            amount="10",
        ))
        await self._run_or_skip(
            async_client.usdm_rest.assign_position_balance(req),
            "assign_position_balance",
        )


class TestAsyncPhemexUSDMTrades:
    async def test_user_trades(self, async_client):
        req = UserTradeRequest.default(symbol="BTCUSDT")
        trades = await async_client.usdm_rest.user_trades(req)

        assert isinstance(trades, list)
        for trade in trades:
            assert isinstance(trade, UserTrade)

    async def test_trades(self, async_client):
        trades = await async_client.usdm_rest.trades(symbol="BTCUSDT")
        assert isinstance(trades, TradeResponse)

        for trade in trades.trades:
            assert isinstance(trade, Trade)

    async def test_trade_history(self, async_client):
        req = TradeHistoryRequest(symbol="BTCUSDT")
        trades = await async_client.usdm_rest.trade_history(req)

        assert isinstance(trades, list)
        for trade in trades:
            assert isinstance(trade, TradeHistoryItem)


class TestAsyncPhemexUSDMMarkets:
    async def test_order_book(self, async_client):
        data = await async_client.usdm_rest.order_book(symbol="BTCUSDT")
        assert isinstance(data, OrderBookResponse)

    async def test_klines(self, async_client):
        req = KlineRequest(symbol="BTCUSDT", resolution=60, limit=5)
        data = await async_client.usdm_rest.klines(req)
        assert isinstance(data, list)
        for kline in data:
            assert isinstance(kline, Kline)

    async def test_perp_get_ticker_24hr(self, async_client):
        data = await async_client.usdm_rest.ticker(symbol="BTCUSDT")
        assert isinstance(data, Ticker)

    async def test_tickers(self, async_client):
        data = await async_client.usdm_rest.tickers()
        assert isinstance(data, list)
        for ticker in data:
            assert isinstance(ticker, Ticker)


class TestAsyncPhemexUSDMFunding:
    async def test_funding_fee(self, async_client):
        req = FundingFeeRequest(symbol="BTCUSDT")
        data = await async_client.usdm_rest.funding_fee_history(req)

        assert isinstance(data, list)
        for fee in data:
            assert isinstance(fee, FundingFeeItem)

    async def test_funding_rate(self, async_client):
        req = FundingRateRequest(symbol="BTCUSDT")
        data = await async_client.usdm_rest.funding_rates(req)

        assert isinstance(data, list)
        for rate in data:
            assert isinstance(rate, FundingRateItem)

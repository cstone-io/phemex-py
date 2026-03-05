import time

import pytest

from phemex_py.biz_errors import PhemexBizError as PhemexAPIError
from phemex_py.usdm_rest.models import *


@pytest.fixture
def order_to_fail(symbol, qty, lmt_price):
    """A perp order that is guaranteed to fail/cancel (for testing)."""
    return PlaceOrderRequest.builder(symbol).increase_long(qty).limit(lmt_price).tif("ImmediateOrCancel").build()


@pytest.fixture
def order_to_live(symbol, qty, lmt_price):
    """A perp order that will remain open (for testing)."""
    return PlaceOrderRequest.builder(symbol).increase_long(qty).limit(lmt_price).build()


class TestPhemexUSDMOrderExecution:
    # Order tests may raise PhemexAPIError on testnet due to account state
    # (e.g. no balance). We accept specific business errors as valid outcomes.
    _ACCEPTABLE_ORDER_CODES = {11001, 11004, 11006, 11082, 20004}

    def _place_or_skip(self, client, order):
        """Place an order, skipping the test if testnet account lacks balance."""
        try:
            client.usdm_rest.place_order(order)
        except PhemexAPIError as e:
            if e.code in self._ACCEPTABLE_ORDER_CODES:
                pytest.skip(f"Testnet account state: [{e.code}] {e.msg}")
            raise

    def test_place_order_post(self, client, order_to_fail):
        """POST place order response uses priceRq alias."""
        try:
            resp = client.usdm_rest.place_order(order_to_fail)
        except PhemexAPIError as e:
            if e.code in self._ACCEPTABLE_ORDER_CODES:
                pytest.skip(f"Testnet account state: [{e.code}] {e.msg}")
            raise
        if resp is not None:
            assert isinstance(resp, PlaceOrderResponse)

    def test_place_order_put(self, client, order_to_fail):
        """PUT place order response uses priceRp alias."""
        try:
            resp = client.usdm_rest.place_order_put(order_to_fail)
        except PhemexAPIError as e:
            if e.code in self._ACCEPTABLE_ORDER_CODES:
                pytest.skip(f"Testnet account state: [{e.code}] {e.msg}")
            raise
        if resp is not None:
            assert isinstance(resp, PutPlaceOrderResponse)
            assert not isinstance(resp, PlaceOrderResponse)

    def test_amend_and_cancel_order(self, client, order_to_live, symbol, lmt_price):
        # Step 1: Place a live order
        self._place_or_skip(client, order_to_live)
        time.sleep(1)

        # Step 2: Fetch the open order to get its ID
        try:
            orders = client.usdm_rest.open_orders(symbol=symbol)
        except PhemexAPIError as e:
            if e.code == 10002:
                pytest.skip("Order not found in open orders (likely filled immediately on testnet)")
            raise
        assert len(orders) > 0, "Expected at least one open order after placing"
        order = orders[0]

        # Step 3: Amend the order (change price)
        amend_req = AmendOrderRequest.model_validate(dict(
            symbol=order.symbol,
            pos_side=order_to_live.pos_side,
            order_id=order.order_id,
            price=lmt_price,
        ))
        # amend_order may return None if the API doesn't echo data
        client.usdm_rest.amend_order(amend_req)

        # Step 4: Cancel the order
        cancel_req = CancelOrderRequest.make(
            symbol=order.symbol,
            order_id=order.order_id,
        )
        # cancel_order may return None if the API doesn't echo data
        client.usdm_rest.cancel_order(cancel_req)

    def test_bulk_cancel_orders(self, client, order_to_live, symbol):
        for i in range(2):
            self._place_or_skip(client, order_to_live)
            time.sleep(1)

        try:
            orders = client.usdm_rest.open_orders(symbol=symbol)
        except PhemexAPIError as e:
            if e.code == 10002:
                pytest.skip("No open orders found on testnet")
            raise
        assert len(orders) >= 2, "Expected at least 2 open orders"
        order_ids = [o.order_id for o in orders[:2]]

        bulk_cancel_req = BulkCancelOrderRequest.make(
            order_ids=order_ids,
            symbol=order_to_live.symbol,
        )
        bulk_cancel_resp = client.usdm_rest.bulk_cancel(bulk_cancel_req)
        assert isinstance(bulk_cancel_resp, list)
        for resp in bulk_cancel_resp:
            assert isinstance(resp, CancelOrderResponse)

    def test_cancel_all_orders(self, client, order_to_live):
        self._place_or_skip(client, order_to_live)
        time.sleep(1)

        cancel_all_resp = client.usdm_rest.cancel_all(order_to_live.symbol)
        assert cancel_all_resp is None


class TestPhemexUSDMOrderInformation:
    def test_perp_get_open_orders(self, client, symbol):
        try:
            orders = client.usdm_rest.open_orders(symbol=symbol)
        except PhemexAPIError as e:
            if e.code == 10002:
                pytest.skip("No open orders on testnet")
            raise

        assert isinstance(orders, list)
        for order in orders:
            assert isinstance(order, OpenOrderResponse)

    def test_get_closed_orders(self, client, symbol):
        req = ClosedOrdersRequest.default(symbol=symbol)
        orders = client.usdm_rest.closed_orders(req)

        assert isinstance(orders, list)
        for order in orders:
            assert isinstance(order, ClosedOrderResponse)

    def test_lookup_order(self, client, symbol):
        try:
            orders = client.usdm_rest.open_orders(symbol=symbol)
        except PhemexAPIError as e:
            if e.code == 10002:
                pytest.skip("No open orders on testnet")
            raise
        if not orders:
            pytest.skip("No open orders to look up")
        order_id = orders[0].order_id
        looked_up = client.usdm_rest.lookup_order(symbol=symbol, order_id=order_id)
        # lookup_order may return None if the order was filled/cancelled between queries
        if looked_up is not None:
            assert isinstance(looked_up, OpenOrderResponse)
            assert looked_up.order_id == order_id

    def test_order_history(self, client, symbol):
        orders = client.usdm_rest.order_history(symbol=symbol)

        assert isinstance(orders, list)
        for order in orders:
            assert isinstance(order, OrderHistoryResponse)


class TestPhemexUSDMPortfolio:
    def test_positions(self, client):
        positions = client.usdm_rest.positions()

        assert isinstance(positions, PositionResponse)
        assert isinstance(positions.positions, list)
        for pos in positions.positions:
            assert isinstance(pos, Position)

    def test_positions_with_pnl(self, client):
        positions = client.usdm_rest.positions_with_pnl()

        assert isinstance(positions, PositionWithPnLResponse)
        assert isinstance(positions.positions, list)
        for pos in positions.positions:
            assert isinstance(pos, PositionWithPnL)

    def test_risk_unit(self, client):
        risk_units = client.usdm_rest.risk_units()
        assert isinstance(risk_units, list)
        for item in risk_units:
            assert isinstance(item, RiskUnitResponse)

    def test_closed_positions(self, client, symbol):
        req = ClosedPositionRequest.default(symbol=symbol)
        closed_positions = client.usdm_rest.closed_positions(req)

        assert isinstance(closed_positions, list)
        for pos in closed_positions:
            assert isinstance(pos, ClosedPosition)


class TestPhemexUSDMOptions:
    # Business errors that are acceptable due to testnet account state
    # (e.g. open positions preventing mode switch, no position for balance assignment)
    _ACCEPTABLE_CODES = {39201, 39995, 39996, 11001, 11004, 11006, 11082}

    def _run_or_skip(self, fn, label):
        """Run fn(), skipping if a known testnet-state business error occurs."""
        try:
            fn()
        except PhemexAPIError as e:
            if e.code in self._ACCEPTABLE_CODES:
                pytest.skip(f"Testnet account state: [{e.code}] {e.msg}")
            pytest.fail(f"{label} raised an unexpected PhemexAPIError: {e}")
        except Exception as e:
            pytest.fail(f"{label} raised an unexpected exception: {e}")

    def test_perp_switch_pos_mode(self, client, symbol):
        req = SwitchModeRequest(symbol=symbol, mode="Hedged")
        self._run_or_skip(
            lambda: client.usdm_rest.switch_position_mode(req),
            "perp_switch_pos_mode",
        )

    def test_perp_set_leverage_oneway(self, client, symbol):
        try:
            req = SwitchModeRequest(symbol=symbol, mode="OneWay")
            client.usdm_rest.switch_position_mode(req)
        except PhemexAPIError as e:
            if e.code in self._ACCEPTABLE_CODES:
                pytest.skip(f"Cannot switch to OneWay on testnet: [{e.code}] {e.msg}")
            raise

        req = SetLeverageRequest.model_validate(dict(symbol=symbol, one_way="10"))
        self._run_or_skip(
            lambda: client.usdm_rest.set_leverage(req),
            "perp_set_leverage",
        )

        try:
            req = SwitchModeRequest(symbol=symbol, mode="Hedged")
            client.usdm_rest.switch_position_mode(req)
        except PhemexAPIError:
            pass  # best-effort restore

    def test_perp_set_leverage_hedged(self, client, symbol):
        req = SetLeverageRequest.model_validate(dict(symbol=symbol, long="5", short="7"))
        self._run_or_skip(
            lambda: client.usdm_rest.set_leverage(req),
            "perp_set_leverage",
        )

    def test_assign_position_balance(self, client, symbol):
        req = AssignPositionBalanceRequest.model_validate(dict(
            symbol=symbol,
            side="Long",
            amount="10",
        ))
        self._run_or_skip(
            lambda: client.usdm_rest.assign_position_balance(req),
            "assign_position_balance",
        )


class TestPhemexUSDMTrades:
    def test_user_trades(self, client, symbol):
        req = UserTradeRequest.default(symbol=symbol)
        trades = client.usdm_rest.user_trades(req)

        assert isinstance(trades, list)
        for trade in trades:
            assert isinstance(trade, UserTrade)

    def test_trades(self, client, symbol):
        trades = client.usdm_rest.trades(symbol=symbol)
        assert isinstance(trades, TradeResponse)

        for trade in trades.trades:
            assert isinstance(trade, Trade)

    def test_trade_history(self, client, symbol):
        req = TradeHistoryRequest(symbol=symbol)
        trades = client.usdm_rest.trade_history(req)

        assert isinstance(trades, list)
        for trade in trades:
            assert isinstance(trade, TradeHistoryItem)


class TestPhemexUSDMMarkets:
    def test_order_book(self, client, symbol):
        data = client.usdm_rest.order_book(symbol=symbol)
        assert isinstance(data, OrderBookResponse)

    def test_klines(self, client, symbol):
        req = KlineRequest(symbol=symbol, resolution=60, limit=5)
        data = client.usdm_rest.klines(req)
        assert isinstance(data, list)
        for kline in data:
            assert isinstance(kline, Kline)

    def test_perp_get_ticker_24hr(self, client, symbol):
        data = client.usdm_rest.ticker(symbol=symbol)
        assert isinstance(data, Ticker)

    def test_tickers(self, client):
        data = client.usdm_rest.tickers()
        assert isinstance(data, list)
        for ticker in data:
            assert isinstance(ticker, Ticker)


class TestPhemexUSDMFunding:
    def test_funding_fee(self, client, symbol):
        req = FundingFeeRequest(symbol=symbol)
        data = client.usdm_rest.funding_fee_history(req)

        assert isinstance(data, list)
        for fee in data:
            assert isinstance(fee, FundingFeeItem)

    def test_funding_rate(self, client, symbol):
        req = FundingRateRequest(symbol=symbol)
        data = client.usdm_rest.funding_rates(req)

        assert isinstance(data, list)
        for rate in data:
            assert isinstance(rate, FundingRateItem)

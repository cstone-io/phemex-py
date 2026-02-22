from typing import TYPE_CHECKING
from typing_extensions import deprecated

from ..core.requests import Request, Extractor
from .models import *

if TYPE_CHECKING:
    from ..client import PhemexClient, AsyncPhemexClient


class USDMRest:
    """
    Client for Phemex USD-M perpetual API. For details, see:
    https://phemex-docs.github.io/#usd-m-perpetual-rest-api

    Methods are defined in the same order as the documentation.
    """

    def __init__(self, client: "PhemexClient") -> None:
        self.client = client

    def product_information(self) -> ProductResponse:
        """
        Fetch product information for all USD-M perpetual contracts. For details, see:
        https://phemex-docs.github.io/#query-product-information-2

        NOTE: this is a public endpoint and does not require authentication.
        """
        req = Request.get("/public/products")
        resp = self.client.request(req)
        data = Extractor(resp).data()
        return ProductResponse.model_validate(data)

    def product_information_plus(self):
        """
        Fetch extended product information for all USD-M perpetual contracts. For details, see:
        https://phemex-docs.github.io/#query-product-information-plus

        NOTE: this is a public endpoint and does not require authentication.
        """
        req = Request.get("/public/products-plus")
        resp = self.client.request(req)
        raise NotImplementedError("Response schema not yet defined, use 'product_information' endpoint for now.")

    @deprecated("'place_order' is the preferred method; this will be removed in a future release.")
    def place_order_put(self, request: PlaceOrderRequest) -> OrderResponse | None:
        """
        Place a new USD-M perpetual order (preferred endpoint using PUT). For details, see:
        https://phemex-docs.github.io/#place-order-http-put-prefered-2
        """
        req = Request.put("/g-orders/create", params=request)
        resp = self.client.request(req)
        data = Extractor(resp).data()
        return OrderResponse.model_validate(data) if data else None

    def place_order(self, request: PlaceOrderRequest) -> OrderResponse | None:
        """
        Place a new USD-M perpetual order using a POST. For details, see:
        https://phemex-docs.github.io/#place-order-http-post-2
        """
        req = Request.post("/g-orders", body=request)
        resp = self.client.request(req)
        data = Extractor(resp).data()
        return OrderResponse.model_validate(data) if data else None

    def amend_order(self, request: AmendOrderRequest) -> OrderResponse | None:
        """
        Amend an existing USD-M perpetual order. For details, see:
        https://phemex-docs.github.io/#amend-order-by-orderid
        """
        req = Request.put("/g-orders/replace", params=request)
        resp = self.client.request(req)
        data = Extractor(resp).data()
        return OrderResponse.model_validate(data) if data else None

    def cancel_order(self, request: CancelOrderRequest) -> OrderResponse | None:
        """
        Cancel an existing USD-M perpetual order. For details, see:
        https://phemex-docs.github.io/#cancel-single-order-by-orderid
        """
        req = Request.delete("/g-orders/cancel", params=request)
        resp = self.client.request(req)
        data = Extractor(resp).data()
        return OrderResponse.model_validate(data) if data else None

    def bulk_cancel(self, request: BulkCancelOrderRequest) -> list[OrderResponse]:
        """
        Bulk cancel USD-M perpetual orders. For details, see:
        https://phemex-docs.github.io/#bulk-cancel-orders-2
        """
        req = Request.delete("/g-orders", params=request)
        resp = self.client.request(req)
        data = Extractor(resp).data()
        return [OrderResponse.model_validate(item) for item in data]

    def cancel_all(self, symbol: str) -> None:
        """
        Cancel all orders for hedge supported symbols. For details, see:
        https://phemex-docs.github.io/#cancel-all-orders-2

        NOTE: this method cancels all orders for a given symbol, triggered and
        untriggered by invoking this endpoint twice.
        """
        untriggered = CancelAllOrdersRequest.make(symbol=symbol, untriggered=True)
        req_1 = Request.delete("/g-orders/all", params=untriggered)
        self.client.request(req_1)

        triggered = CancelAllOrdersRequest.make(symbol=symbol, untriggered=False)
        req_2 = Request.delete("/g-orders/all", params=triggered)
        self.client.request(req_2)

    def positions(self, currency: str = "USDT") -> PositionResponse:
        """
        Query account positions. For details, see:
        https://phemex-docs.github.io/#query-account-positions
        """
        req = Request.get("/g-accounts/accountPositions", params={"currency": currency})
        resp = self.client.request(req)
        data = Extractor(resp).data()
        return PositionResponse.model_validate(data)

    def positions_with_pnl(self, currency: str = "USDT") -> PositionWithPnLResponse:
        """
        Query account positions with unrealized PNL. For details, see:
        https://phemex-docs.github.io/#query-account-positions-with-unrealized-pnl

        NOTE: this can be a heavy endpoint if you have many positions. Use with caution.
        """
        req = Request.get("/g-accounts/positions", params={"currency": currency})
        resp = self.client.request(req)
        data = Extractor(resp).data()
        return PositionWithPnLResponse.model_validate(data)

    def risk_units(self) -> list[RiskUnitResponse]:
        """
        Fetch risk unit information. For details, see:
        https://phemex-docs.github.io/#query-risk-unit

        NOTE: the official docs do not provide any description for this endpoint.
        Below is a working interpretation:

        The “risk unit” API gives you a “risk‐unit balance / usage view” of
        your account from the perspective of margin / leverage constraints.This
        is analogous to “account margin usage summary” in other derivatives
        APIs, but Phemex’s term is “risk unit.”
        """
        req = Request.get("/g-accounts/risk-unit")
        resp = self.client.request(req)
        data = Extractor(resp).data()
        return [RiskUnitResponse.model_validate(item) for item in data]

    def switch_position_mode(self, request: SwitchModeRequest) -> None:
        """
        Toggle position mode between OneWay and Hedge. For details, see:
        https://phemex-docs.github.io/#switch-position-mode-synchronously

        NOTE: this persists the setting until it is changed again, even across sessions.
        """
        req = Request.put("/g-positions/switch-pos-mode-sync", params=request)
        self.client.request(req)

    def set_leverage(self, request: SetLeverageRequest) -> None:
        """
        Set leverage for a specific symbol. For details, see:
        https://phemex-docs.github.io/#set-leverage-2

        NOTE: this persists the setting until it is changed again, even across sessions.
        """
        req = Request.put("/g-positions/leverage", params=request)
        self.client.request(req)

    def set_risk_limit(self) -> None:
        """
        Set risk limit for a specific symbol. For details, see:
        https://phemex-docs.github.io/#set-risklimit

        NOTE: For hedged contracts, the 'Set Position Risk Limit API' has been
        deprecated. It is no longer possible to manually set the 'Risk Limit'.
        Instead, simply adjust the leverage multiplier as required, and the
        'Risk Limit' will be automatically adjusted.
        """
        raise NotImplementedError(
            "For hedged contracts, the 'Set Position Risk Limit API' has been deprecated. 'set_leverage' is the preferred method")

    def assign_position_balance(self, request: AssignPositionBalanceRequest) -> None:
        """
        Assign position balance between USDT and USD. For details, see:
        https://phemex-docs.github.io/#assign-position-balance

        NOTE: the official docs do not provide any description for this endpoint.
        Below is a working interpretation:

        Most likely a mechanism to adjust how much “balance” (i.e. margin capital)
        is allocated to a specific position. In many margin / derivatives systems
        (especially when using isolated margin or adjustable margin modes), you
        can tune how much margin is assigned to a specific position so as to
        reduce liquidation risk or control capital usage.
        """
        req = Request.post("/g-positions/assign", params=request)
        self.client.request(req)

    def open_orders(self, symbol: str) -> list[OpenOrder]:
        """
        Fetch all open USD-M perpetual orders for a given symbol. For details, see:
        https://phemex-docs.github.io/#query-open-orders-by-symbol-2
        """
        req = Request.get("/g-orders/activeList", params={"symbol": symbol})
        resp = self.client.request(req)
        data = Extractor(resp).data()
        if data is None:
            return []
        return [OpenOrder.model_validate(item) for item in data["rows"]]

    def closed_orders(self, request: ClosedOrdersRequest) -> list[ClosedOrder]:
        """
        Fetch recent closed USD-M perpetual orders for a given symbol. For details, see:
        https://phemex-docs.github.io/#query-closed-orders-by-symbol-2
        """
        req = Request.get("/exchange/order/v2/orderList", params=request)
        resp = self.client.request(req)
        data = Extractor(resp).data()
        if data is None:
            return []
        return [ClosedOrder.model_validate(item) for item in data]

    def closed_positions(self, request: ClosedPositionRequest) -> list[ClosedPosition]:
        """
        Fetch recent closed USD-M perpetual positions. For details, see:
        https://phemex-docs.github.io/#query-closed-positions
        """
        req = Request.get("/api-data/g-futures/closedPosition", params=request)
        resp = self.client.request(req)
        data = Extractor(resp).data()
        if data is None:
            return []
        return [ClosedPosition.model_validate(item) for item in data]

    def user_trades(self, request: UserTradeRequest) -> list[UserTrade]:
        """
        Fetch recent trade history. For details, see:
        https://phemex-docs.github.io/#query-user-trade-2
        """
        req = Request.get("/exchange/order/v2/tradingList", params=request)
        resp = self.client.request(req)
        data = Extractor(resp).data()
        if data is None:
            return []
        return [UserTrade.model_validate(item) for item in data]

    def order_book(self, symbol: str) -> OrderBookResponse:
        """
        Fetch order book data. For details, see:
        https://phemex-docs.github.io/#query-order-book-2
        """
        req = Request.get("/md/v2/orderbook", params={"symbol": symbol})
        resp = self.client.request(req)
        data = Extractor(resp).key("result").extract()
        return OrderBookResponse.model_validate(data)

    def klines(self, request: KlineRequest) -> list[Kline]:
        """
        Fetch kline/candlestick data. For details, see:
        https://phemex-docs.github.io/#query-kline-2
        """
        req = Request.get("/exchange/public/md/v2/kline/last", params=request)
        resp = self.client.request(req)
        data = Extractor(resp).data()
        if data is None:
            return []
        return [Kline.model_validate(item) for item in data["rows"]]

    def trades(self, symbol: str) -> TradeResponse:
        """
        Fetch recent trades. For details, see:
        https://phemex-docs.github.io/#query-trade
        """
        req = Request.get("/md/v2/trade", params={"symbol": symbol})
        resp = self.client.request(req)
        data = Extractor(resp).key("result").extract()
        return TradeResponse.model_validate(data)

    def ticker(self, symbol: str) -> Ticker:
        """
        Fetch 24hr ticker data for a given symbol. For details, see:
        https://phemex-docs.github.io/#query-24-ticker

        NOTE: this uses the newer v3 endpoint, v2 is no longer supported.
        """
        req = Request.get("/md/v3/ticker/24hr", params={"symbol": symbol})
        resp = self.client.request(req)
        data = Extractor(resp).key("result").extract()
        return Ticker.model_validate(data)

    def tickers(self) -> list[Ticker]:
        """
        Fetch 24hr ticker data for all symbols. For details, see:
        https://phemex-docs.github.io/#query-24-ticker-for-all-symbols

        NOTE: this uses the newer v3 endpoint, v2 is no longer supported.
        """
        req = Request.get("/md/v3/ticker/24hr/all")
        resp = self.client.request(req)
        data = Extractor(resp).key("result").extract()
        return [Ticker.model_validate(item) for item in data]

    def order_history(self, symbol: str) -> list[OrderHistoryItem]:
        """
        Fetch order history. For details, see:
        https://phemex-docs.github.io/#query-orders-history
        """
        req = Request.get("/api-data/g-futures/orders", params={"symbol": symbol})
        resp = self.client.request(req)
        data = Extractor(resp).key("data", "rows").extract()
        if data is None:
            return []
        return [OrderHistoryItem.model_validate(item) for item in data]

    def lookup_order(self, symbol: str, order_id: str) -> OpenOrder | None:
        """
        Fetch a specific order by symbol and order ID. For details, see:
        https://phemex-docs.github.io/#query-orders-by-ids
        """
        params = {"symbol": symbol, "orderID": order_id}
        req = Request.get("/api-data/g-futures/orders/by-order-id", params=params)
        resp = self.client.request(req)
        data = Extractor(resp).key("data", "rows").extract()
        if data is None or len(data) == 0:
            return None
        return OpenOrder.model_validate(data.pop())

    def trade_history(self, request: TradeHistoryRequest) -> list[TradeHistoryItem]:
        """
        Query user trade history. For details, see:
        https://phemex-docs.github.io/#query-trades-history
        """
        req = Request.get("/api-data/g-futures/trades", params=request)
        resp = self.client.request(req)
        data = Extractor(resp).key("data", "rows").extract()
        if data is None:
            return []
        return [TradeHistoryItem.model_validate(item) for item in data]

    def funding_fee_history(self, request: FundingFeeRequest) -> list[FundingFeeItem]:
        """
        Fetch funding fee history. For details, see:
        https://phemex-docs.github.io/#query-funding-fee-history-2
        """
        req = Request.get("/api-data/g-futures/funding-fees", params=request)
        resp = self.client.request(req)
        data = Extractor(resp).key("data", "rows").extract()
        if data is None:
            return []
        return [FundingFeeItem.model_validate(item) for item in data]

    def funding_rates(self, request: FundingRateRequest) -> list[FundingRateItem]:
        """
        Fetch historical funding rates. For details, see:
        https://phemex-docs.github.io/#query-real-funding-rates
        """
        req = Request.get("/contract-biz/public/real-funding-rates", params=request)
        resp = self.client.request(req)
        data = Extractor(resp).key("data", "rows").extract()
        if data is None:
            return []
        return [FundingRateItem.model_validate(item) for item in data]


class AsyncUSDMRest:
    """
    Async client for Phemex USD-M perpetual API. For details, see:
    https://phemex-docs.github.io/#usd-m-perpetual-rest-api

    Methods are defined in the same order as the documentation.
    """

    def __init__(self, client: "AsyncPhemexClient") -> None:
        self.client = client

    async def product_information(self) -> ProductResponse:
        """
        Fetch product information for all USD-M perpetual contracts. For details, see:
        https://phemex-docs.github.io/#query-product-information-2

        NOTE: this is a public endpoint and does not require authentication.
        """
        req = Request.get("/public/products")
        resp = await self.client.request(req)
        data = Extractor(resp).data()
        return ProductResponse.model_validate(data)

    async def product_information_plus(self):
        """
        Fetch extended product information for all USD-M perpetual contracts. For details, see:
        https://phemex-docs.github.io/#query-product-information-plus

        NOTE: this is a public endpoint and does not require authentication.
        """
        req = Request.get("/public/products-plus")
        await self.client.request(req)
        raise NotImplementedError("Response schema not yet defined, use 'product_information' endpoint for now.")

    @deprecated("'place_order' is the preferred method; this will be removed in a future release.")
    async def place_order_put(self, request: PlaceOrderRequest) -> OrderResponse | None:
        """
        Place a new USD-M perpetual order (preferred endpoint using PUT). For details, see:
        https://phemex-docs.github.io/#place-order-http-put-prefered-2
        """
        req = Request.put("/g-orders/create", params=request)
        resp = await self.client.request(req)
        data = Extractor(resp).data()
        return OrderResponse.model_validate(data) if data else None

    async def place_order(self, request: PlaceOrderRequest) -> OrderResponse | None:
        """
        Place a new USD-M perpetual order using a POST. For details, see:
        https://phemex-docs.github.io/#place-order-http-post-2
        """
        req = Request.post("/g-orders", body=request)
        resp = await self.client.request(req)
        data = Extractor(resp).data()
        return OrderResponse.model_validate(data) if data else None

    async def amend_order(self, request: AmendOrderRequest) -> OrderResponse | None:
        """
        Amend an existing USD-M perpetual order. For details, see:
        https://phemex-docs.github.io/#amend-order-by-orderid
        """
        req = Request.put("/g-orders/replace", params=request)
        resp = await self.client.request(req)
        data = Extractor(resp).data()
        return OrderResponse.model_validate(data) if data else None

    async def cancel_order(self, request: CancelOrderRequest) -> OrderResponse | None:
        """
        Cancel an existing USD-M perpetual order. For details, see:
        https://phemex-docs.github.io/#cancel-single-order-by-orderid
        """
        req = Request.delete("/g-orders/cancel", params=request)
        resp = await self.client.request(req)
        data = Extractor(resp).data()
        return OrderResponse.model_validate(data) if data else None

    async def bulk_cancel(self, request: BulkCancelOrderRequest) -> list[OrderResponse]:
        """
        Bulk cancel USD-M perpetual orders. For details, see:
        https://phemex-docs.github.io/#bulk-cancel-orders-2
        """
        req = Request.delete("/g-orders", params=request)
        resp = await self.client.request(req)
        data = Extractor(resp).data()
        return [OrderResponse.model_validate(item) for item in data]

    async def cancel_all(self, symbol: str) -> None:
        """
        Cancel all orders for hedge supported symbols. For details, see:
        https://phemex-docs.github.io/#cancel-all-orders-2

        NOTE: this method cancels all orders for a given symbol, triggered and
        untriggered by invoking this endpoint twice.
        """
        untriggered = CancelAllOrdersRequest.make(symbol=symbol, untriggered=True)
        req_1 = Request.delete("/g-orders/all", params=untriggered)
        await self.client.request(req_1)

        triggered = CancelAllOrdersRequest.make(symbol=symbol, untriggered=False)
        req_2 = Request.delete("/g-orders/all", params=triggered)
        await self.client.request(req_2)

    async def positions(self, currency: str = "USDT") -> PositionResponse:
        """
        Query account positions. For details, see:
        https://phemex-docs.github.io/#query-account-positions
        """
        req = Request.get("/g-accounts/accountPositions", params={"currency": currency})
        resp = await self.client.request(req)
        data = Extractor(resp).data()
        return PositionResponse.model_validate(data)

    async def positions_with_pnl(self, currency: str = "USDT") -> PositionWithPnLResponse:
        """
        Query account positions with unrealized PNL. For details, see:
        https://phemex-docs.github.io/#query-account-positions-with-unrealized-pnl

        NOTE: this can be a heavy endpoint if you have many positions. Use with caution.
        """
        req = Request.get("/g-accounts/positions", params={"currency": currency})
        resp = await self.client.request(req)
        data = Extractor(resp).data()
        return PositionWithPnLResponse.model_validate(data)

    async def risk_units(self) -> list[RiskUnitResponse]:
        """
        Fetch risk unit information. For details, see:
        https://phemex-docs.github.io/#query-risk-unit
        """
        req = Request.get("/g-accounts/risk-unit")
        resp = await self.client.request(req)
        data = Extractor(resp).data()
        return [RiskUnitResponse.model_validate(item) for item in data]

    async def switch_position_mode(self, request: SwitchModeRequest) -> None:
        """
        Toggle position mode between OneWay and Hedge. For details, see:
        https://phemex-docs.github.io/#switch-position-mode-synchronously
        """
        req = Request.put("/g-positions/switch-pos-mode-sync", params=request)
        await self.client.request(req)

    async def set_leverage(self, request: SetLeverageRequest) -> None:
        """
        Set leverage for a specific symbol. For details, see:
        https://phemex-docs.github.io/#set-leverage-2
        """
        req = Request.put("/g-positions/leverage", params=request)
        await self.client.request(req)

    async def set_risk_limit(self) -> None:
        """
        Set risk limit for a specific symbol. For details, see:
        https://phemex-docs.github.io/#set-risklimit
        """
        raise NotImplementedError(
            "For hedged contracts, the 'Set Position Risk Limit API' has been deprecated. 'set_leverage' is the preferred method")

    async def assign_position_balance(self, request: AssignPositionBalanceRequest) -> None:
        """
        Assign position balance between USDT and USD. For details, see:
        https://phemex-docs.github.io/#assign-position-balance
        """
        req = Request.post("/g-positions/assign", params=request)
        await self.client.request(req)

    async def open_orders(self, symbol: str) -> list[OpenOrder]:
        """
        Fetch all open USD-M perpetual orders for a given symbol. For details, see:
        https://phemex-docs.github.io/#query-open-orders-by-symbol-2
        """
        req = Request.get("/g-orders/activeList", params={"symbol": symbol})
        resp = await self.client.request(req)
        data = Extractor(resp).data()
        if data is None:
            return []
        return [OpenOrder.model_validate(item) for item in data["rows"]]

    async def closed_orders(self, request: ClosedOrdersRequest) -> list[ClosedOrder]:
        """
        Fetch recent closed USD-M perpetual orders for a given symbol. For details, see:
        https://phemex-docs.github.io/#query-closed-orders-by-symbol-2
        """
        req = Request.get("/exchange/order/v2/orderList", params=request)
        resp = await self.client.request(req)
        data = Extractor(resp).data()
        if data is None:
            return []
        return [ClosedOrder.model_validate(item) for item in data]

    async def closed_positions(self, request: ClosedPositionRequest) -> list[ClosedPosition]:
        """
        Fetch recent closed USD-M perpetual positions. For details, see:
        https://phemex-docs.github.io/#query-closed-positions
        """
        req = Request.get("/api-data/g-futures/closedPosition", params=request)
        resp = await self.client.request(req)
        data = Extractor(resp).data()
        if data is None:
            return []
        return [ClosedPosition.model_validate(item) for item in data]

    async def user_trades(self, request: UserTradeRequest) -> list[UserTrade]:
        """
        Fetch recent trade history. For details, see:
        https://phemex-docs.github.io/#query-user-trade-2
        """
        req = Request.get("/exchange/order/v2/tradingList", params=request)
        resp = await self.client.request(req)
        data = Extractor(resp).data()
        if data is None:
            return []
        return [UserTrade.model_validate(item) for item in data]

    async def order_book(self, symbol: str) -> OrderBookResponse:
        """
        Fetch order book data. For details, see:
        https://phemex-docs.github.io/#query-order-book-2
        """
        req = Request.get("/md/v2/orderbook", params={"symbol": symbol})
        resp = await self.client.request(req)
        data = Extractor(resp).key("result").extract()
        return OrderBookResponse.model_validate(data)

    async def klines(self, request: KlineRequest) -> list[Kline]:
        """
        Fetch kline/candlestick data. For details, see:
        https://phemex-docs.github.io/#query-kline-2
        """
        req = Request.get("/exchange/public/md/v2/kline/last", params=request)
        resp = await self.client.request(req)
        data = Extractor(resp).data()
        if data is None:
            return []
        return [Kline.model_validate(item) for item in data["rows"]]

    async def trades(self, symbol: str) -> TradeResponse:
        """
        Fetch recent trades. For details, see:
        https://phemex-docs.github.io/#query-trade
        """
        req = Request.get("/md/v2/trade", params={"symbol": symbol})
        resp = await self.client.request(req)
        data = Extractor(resp).key("result").extract()
        return TradeResponse.model_validate(data)

    async def ticker(self, symbol: str) -> Ticker:
        """
        Fetch 24hr ticker data for a given symbol. For details, see:
        https://phemex-docs.github.io/#query-24-ticker

        NOTE: this uses the newer v3 endpoint, v2 is no longer supported.
        """
        req = Request.get("/md/v3/ticker/24hr", params={"symbol": symbol})
        resp = await self.client.request(req)
        data = Extractor(resp).key("result").extract()
        return Ticker.model_validate(data)

    async def tickers(self) -> list[Ticker]:
        """
        Fetch 24hr ticker data for all symbols. For details, see:
        https://phemex-docs.github.io/#query-24-ticker-for-all-symbols

        NOTE: this uses the newer v3 endpoint, v2 is no longer supported.
        """
        req = Request.get("/md/v3/ticker/24hr/all")
        resp = await self.client.request(req)
        data = Extractor(resp).key("result").extract()
        return [Ticker.model_validate(item) for item in data]

    async def order_history(self, symbol: str) -> list[OrderHistoryItem]:
        """
        Fetch order history. For details, see:
        https://phemex-docs.github.io/#query-orders-history
        """
        req = Request.get("/api-data/g-futures/orders", params={"symbol": symbol})
        resp = await self.client.request(req)
        data = Extractor(resp).key("data", "rows").extract()
        if data is None:
            return []
        return [OrderHistoryItem.model_validate(item) for item in data]

    async def lookup_order(self, symbol: str, order_id: str) -> OpenOrder | None:
        """
        Fetch a specific order by symbol and order ID. For details, see:
        https://phemex-docs.github.io/#query-orders-by-ids
        """
        params = {"symbol": symbol, "orderID": order_id}
        req = Request.get("/api-data/g-futures/orders/by-order-id", params=params)
        resp = await self.client.request(req)
        data = Extractor(resp).key("data", "rows").extract()
        if data is None or len(data) == 0:
            return None
        return OpenOrder.model_validate(data.pop())

    async def trade_history(self, request: TradeHistoryRequest) -> list[TradeHistoryItem]:
        """
        Query user trade history. For details, see:
        https://phemex-docs.github.io/#query-trades-history
        """
        req = Request.get("/api-data/g-futures/trades", params=request)
        resp = await self.client.request(req)
        data = Extractor(resp).key("data", "rows").extract()
        if data is None:
            return []
        return [TradeHistoryItem.model_validate(item) for item in data]

    async def funding_fee_history(self, request: FundingFeeRequest) -> list[FundingFeeItem]:
        """
        Fetch funding fee history. For details, see:
        https://phemex-docs.github.io/#query-funding-fee-history-2
        """
        req = Request.get("/api-data/g-futures/funding-fees", params=request)
        resp = await self.client.request(req)
        data = Extractor(resp).key("data", "rows").extract()
        if data is None:
            return []
        return [FundingFeeItem.model_validate(item) for item in data]

    async def funding_rates(self, request: FundingRateRequest) -> list[FundingRateItem]:
        """
        Fetch historical funding rates. For details, see:
        https://phemex-docs.github.io/#query-real-funding-rates
        """
        req = Request.get("/contract-biz/public/real-funding-rates", params=request)
        resp = await self.client.request(req)
        data = Extractor(resp).key("data", "rows").extract()
        if data is None:
            return []
        return [FundingRateItem.model_validate(item) for item in data]

from abc import ABC
from typing import Annotated, Any, Self

from pydantic import field_validator, model_validator

from ..core.datetime import unix_now, MS
from ..exceptions import ValidationError
from ..core.models import PhemexModel, PhemexDecimal, PhemexDecimalLike
from ..core import fields as f


# --------------------------------------
# Product related models
# --------------------------------------

class Currency(PhemexModel):
    currency: Annotated[str, *f.Currency("currency")]
    display_currency: Annotated[str, *f.Currency.Display("displayCurrency")]

    name: Annotated[str, *f.Product.Name("name")]
    code: Annotated[int, *f.Product.Code("code")]
    status: Annotated[str, *f.Product.Status("status")]

    value_scale: Annotated[int, *f.ProductScale.Value("valueScale")]
    assets_precision: Annotated[int, *f.ProductPrecision.Asset("assetsPrecision")]
    min_value: Annotated[PhemexDecimal, *f.ProductLimit.MinValue("minValueEv", scaled=True)]
    max_value: Annotated[PhemexDecimal, *f.ProductLimit.MaxValue("maxValueEv", scaled=True)]

    address_tag: Annotated[int, *f.Product.NeedAddressTag("needAddrTag")]
    assets_display: Annotated[int, *f.Product.AssetsDisplay("inAssetsDisplay")]
    perpetual: Annotated[int, *f.Currency.PerpetualFlag("perpetual")]
    stable_coin: Annotated[int, *f.Currency.StableCoinFlag("stableCoin")]


class ProductCore(PhemexModel, ABC):
    symbol: Annotated[str, *f.Symbol("symbol")]
    display_symbol: Annotated[str, *f.Symbol.Display("displaySymbol")]
    base_currency: Annotated[str, *f.Currency.Base("baseCurrency")]
    quote_currency: Annotated[str, *f.Currency.Quote("quoteCurrency")]

    code: Annotated[int, *f.Product.Code("code")]
    product_type: Annotated[str, *f.Product.ProductType("type")]
    description: Annotated[str, *f.Product.Description("description")]
    status: Annotated[str, *f.Product.Status("status")]
    list_time: Annotated[int, *f.Product.ListTime("listTime")]

    price_scale: Annotated[int, *f.ProductScale.Price("priceScale")]
    ratio_scale: Annotated[int, *f.ProductScale.Ratio("ratioScale")]
    tip_order_quantity: Annotated[PhemexDecimal, *f.ProductLimit.TipOrderQuantity("tipOrderQty")]


class Spot(ProductCore):
    base_currency: Annotated[str, *f.Currency.Base("baseCurrency")]
    price_precision: Annotated[int, *f.ProductPrecision.Price("pricePrecision")]
    base_tick_size: Annotated[PhemexDecimal, *f.ProductTick.BaseSize("baseTickSizeEv", scaled=True)]
    base_quantity_precision: Annotated[int, *f.ProductPrecision.BaseQuantity("baseQtyPrecision")]
    quote_tick_size: Annotated[PhemexDecimal, *f.ProductTick.QuoteSize("quoteTickSizeEv", scaled=True)]
    quote_quantity_precision: Annotated[int, *f.ProductPrecision.QuoteQuantity("quoteQtyPrecision")]
    min_order_value: Annotated[PhemexDecimal, *f.ProductLimit.MinOrderValue("minOrderValueEv", scaled=True)]
    max_order_value: Annotated[PhemexDecimal, *f.ProductLimit.MaxOrderValue("maxOrderValueEv", scaled=True)]
    max_base_order_size: Annotated[PhemexDecimal, *f.ProductLimit.MaxBaseOrderSize("maxBaseOrderSizeEv", scaled=True)]
    default_maker_fee: Annotated[PhemexDecimal, *f.ProductLimit.DefaultMakerFee("defaultMakerFeeEr", scaled=True)]
    default_taker_fee: Annotated[PhemexDecimal, *f.ProductLimit.DefaultTakerFee("defaultTakerFeeEr", scaled=True)]
    buy_upper_limit: Annotated[PhemexDecimal, *f.ProductLimit.BuyUpperLimit("buyPriceUpperLimitPct")]
    sell_lower_limit: Annotated[PhemexDecimal, *f.ProductLimit.SellLowerLimit("sellPriceLowerLimitPct")]
    base_tick_size_alt: Annotated[str, *f.ProductTick.BaseSize("baseTickSize", alt=True)]
    quote_tick_size_alt: Annotated[str, *f.ProductTick.QuoteSize("quoteTickSize", alt=True)]
    min_order_value_alt: Annotated[str, *f.ProductLimit.MinOrderValue("minOrderValue", alt=True)]
    max_base_order_size_alt: Annotated[str, *f.ProductLimit.MaxBaseOrderSize("maxBaseOrderSize", alt=True)]
    max_order_value_alt: Annotated[str, *f.ProductLimit.MaxOrderValue("maxOrderValue", alt=True)]
    default_maker_fee_alt: Annotated[str, *f.ProductLimit.DefaultMakerFee("defaultMakerFee", alt=True)]
    default_taker_fee_alt: Annotated[str, *f.ProductLimit.DefaultTakerFee("defaultTakerFee", alt=True)]


class PerpetualCore(ProductCore, ABC):
    index_symbol: Annotated[str, *f.Symbol.Index("indexSymbol")]
    mark_symbol: Annotated[str, *f.Symbol.Mark("markSymbol")]
    funding_symbol: Annotated[str, *f.Symbol.FundingRate("fundingRateSymbol")]
    funding_symbol_alt: Annotated[str, *f.Symbol.FundingRateShort("fundingRate8hSymbol")]
    underlying_symbol: Annotated[str, *f.Symbol.Underlying("contractUnderlyingAssets")]
    settle_currency: Annotated[str, *f.Currency.Settle("settleCurrency")]
    major_symbol: Annotated[bool, *f.Symbol.Major("majorSymbol")]
    tick_size: Annotated[PhemexDecimal, *f.ProductTick.Size("tickSize")]
    min_price: Annotated[PhemexDecimal, *f.ProductLimit.MinPrice("minPriceEp", scaled=True)]
    max_price: Annotated[PhemexDecimal, *f.ProductLimit.MaxPrice("maxPriceEp", scaled=True)]
    default_leverage: Annotated[PhemexDecimal, *f.ProductLeverage.Default("defaultLeverage")]
    funding_interval: Annotated[int, *f.Funding.Interval("fundingInterval")]
    max_leverage: Annotated[int, *f.ProductLeverage.Max("maxLeverage")]
    leverage_margin: Annotated[PhemexDecimal, *f.ProductLeverage.MaxMargin("leverageMargin")]
    max_oi: Annotated[int, *f.Product.MaxOI("maxOI")]


class PerpetualV1(PerpetualCore):
    contract_size: Annotated[PhemexDecimal, *f.ProductLimit.ContractSize("contractSize")]
    lot_size: Annotated[PhemexDecimal, *f.ProductLimit.LotSize("lotSize")]
    price_precision: Annotated[int, *f.ProductPrecision.Price("pricePrecision")]
    max_quantity: Annotated[PhemexDecimal, *f.ProductLimit.MaxOrderQuantity("maxOrderQty")]


class PerpetualV2(PerpetualCore):
    sub_type: Annotated[str, *f.Product.ProductSubType("perpetualProductSubType")]
    base_currency: Annotated[str, *f.Currency.Base("baseCurrency")]
    price_precision: Annotated[int, *f.ProductPrecision.Price("pricePrecision")]
    tip_order_quantity_alt: Annotated[PhemexDecimal, *f.ProductLimit.TipOrderQuantity("tipOrderQty", alt=True)]
    max_order_quantity: Annotated[PhemexDecimal, *f.ProductLimit.MaxOrderQuantity("maxOrderQtyRq")]
    min_order_value: Annotated[PhemexDecimal, *f.ProductLimit.MinOrderValue("minOrderValueRq")]
    quantity_precision: Annotated[int, *f.ProductPrecision.Quantity("quantityPrecision")]
    quantity_step_size: Annotated[PhemexDecimal, *f.ProductLimit.QuantityStepSize("qtyStepSize")]
    max_open_leverage: Annotated[PhemexDecimal, *f.ProductLeverage.MaxOpen("maxOpenPosLeverage")]


class ProductRiskLimits(PhemexModel):
    limit: Annotated[int, *f.ProductRisk.MaxRiskLimit("limit")]
    initial_margin: Annotated[PhemexDecimal, *f.ProductRisk.InitialMargin("initialMarginEr", scaled=True)]
    initial_margin_alt: Annotated[str, *f.ProductRisk.InitialMargin("initialMargin", alt=True)]
    maintenance_margin: Annotated[PhemexDecimal, *f.ProductRisk.MaintenanceMargin("maintenanceMarginEr", scaled=True)]
    maintenance_margin_alt: Annotated[str, *f.ProductRisk.MaintenanceMargin("maintenanceMargin", alt=True)]


class ProductRisk(PhemexModel):
    symbol: Annotated[str, *f.Symbol("symbol")]
    steps: Annotated[str, *f.ProductRisk.RiskSteps("steps")]
    risk_limits: Annotated[list[ProductRiskLimits], f.NestedModel("riskLimits")]


class ProductLeverage(PhemexModel):
    initial_margin: Annotated[PhemexDecimal, *f.ProductRisk.InitialMargin("initialMarginEr", scaled=True)]
    initial_margin_alt: Annotated[str, *f.ProductRisk.InitialMargin("initialMargin", alt=True)]
    options: Annotated[list[int | float], *f.ProductLeverage.Options("options")]


class ProductRiskLimitsV2(PhemexModel):
    limit: Annotated[PhemexDecimal, *f.ProductRisk.MaxRiskLimit("limit")]
    initial_margin: Annotated[PhemexDecimal, *f.ProductRisk.InitialMargin("initialMarginRr")]
    maintenance_margin: Annotated[PhemexDecimal, *f.ProductRisk.MaintenanceMargin("maintenanceMarginRr")]


class ProductRiskV2(PhemexModel):
    symbol: Annotated[str, *f.Symbol("symbol")]
    steps: Annotated[str, *f.ProductRisk.RiskSteps("steps")]
    risk_limits: Annotated[list[ProductRiskLimits], f.NestedModel("riskLimits")]


class ProductLeverageV2(PhemexModel):
    options: Annotated[list[int | float], *f.ProductLeverage.Options("options")]
    initial_margin: Annotated[PhemexDecimal, *f.ProductRisk.InitialMargin("initialMarginRr")]


class LeverageMarginItem(PhemexModel):
    value: Annotated[PhemexDecimal, *f.ProductRisk.NotionalValue("notionalValueRv")]
    max_leverage: Annotated[PhemexDecimal, *f.ProductLeverage.Max("maxLeverage")]
    maintenance_margin: Annotated[PhemexDecimal, *f.ProductRisk.MaintenanceMargin("maintenanceMarginRateRr")]
    maintenance_amount: Annotated[PhemexDecimal, *f.ProductRisk.MaintenanceAmount("maintenanceAmountRv")]


class LeverageMargin(PhemexModel):
    index: Annotated[int, *f.ProductRisk.IndexID("index")]
    items: Annotated[list[LeverageMarginItem], f.NestedModel("items")]


class ProductResponse(PhemexModel):
    currencies: Annotated[list[Currency], f.NestedModel("currencies")]
    products: Annotated[list[Spot | PerpetualV1], f.NestedModel("products")]
    products_risk: Annotated[list[ProductRisk], f.NestedModel("riskLimits")]
    products_leverage: Annotated[list[ProductLeverage], f.NestedModel("leverages")]
    futures: Annotated[list[PerpetualV2], f.NestedModel("perpProductsV2")]
    futures_risk: Annotated[list[ProductRiskV2], f.NestedModel("riskLimitsV2")]
    futures_leverage: Annotated[list[ProductLeverageV2], f.NestedModel("leveragesV2")]
    leverage_margins: Annotated[list[LeverageMargin], f.NestedModel("leverageMargins")]

    scale: Annotated[int, *f.ProductScale.Ratio("ratioScale")]
    pilot: Annotated[bool | None, *f.Product.PilotTrading("perpProductsPilot")] = None
    checksum: Annotated[str, *f.Product.Checksum("md5Checksum")]


# --------------------------------------
# Order related models
# --------------------------------------

class OrderCore(PhemexModel):
    client_id: Annotated[str | None, *f.Order.ClientID("clOrdID")] = None
    order_type: Annotated[str | None, *f.Order.OrderType("orderType")] = None
    symbol: Annotated[str | None, *f.Symbol("symbol")] = None
    side: Annotated[str | None, *f.Order.Side("side")] = None
    quantity: Annotated[PhemexDecimal | None, *f.Order.Quantity("orderQtyRq")] = None
    price: Annotated[PhemexDecimal | None, *f.Order.Price("priceRp")] = None

    reduce_only: Annotated[bool | None, *f.OrderCondition.ReduceOnly("reduceOnly")] = None
    time_in_force: Annotated[str | None, *f.OrderCondition.TimeInForce("timeInForce")] = None

    peg_type: Annotated[str | None, *f.OrderCondition.PegType("pegPriceType")] = None
    peg_offset: Annotated[PhemexDecimal | None, *f.OrderCondition.PegOffsetValue("pegOffsetValueRp")] = None
    stop_direction: Annotated[str | None, *f.OrderCondition.StopDirection("stopDirection")] = None
    stop_price: Annotated[PhemexDecimal | None, *f.OrderCondition.StopPrice("stopPxRp")] = None
    sl_price: Annotated[PhemexDecimal | None, *f.OrderCondition.StopLossPrice("stopLossRp")] = None
    sl_price_alt: Annotated[PhemexDecimal | None, *f.OrderCondition.StopLossPrice("slPxRp", alt=True)] = None
    tp_price: Annotated[PhemexDecimal | None, *f.OrderCondition.TakeProfitPrice("takeProfitRp")] = None
    tp_price_alt: Annotated[PhemexDecimal | None, *f.OrderCondition.TakeProfitPrice("tpPxRp", alt=True)] = None
    trigger: Annotated[str | None, *f.OrderCondition.TriggerType("triggerType")] = None


class OrderResponse(OrderCore):
    """
    Many order endpoints share this output model i.e. place order, amend order, get order
    """
    order_id: Annotated[str | None, *f.Order.ID("orderID")] = None
    error: Annotated[int | None, *f.ErrorCode("bizError")] = None

    action_time_ns: Annotated[int | None, *f.Time.Action("actionTimeNs")] = None
    trans_time_ns: Annotated[int | None, *f.Time.Transaction("transactTimeNs")] = None
    order_status: Annotated[str | None, *f.Order.Status("ordStatus")] = None
    exec_status: Annotated[str | None, *f.OrderExecution.Status("execStatus")] = None
    exec_instructions: Annotated[str | None, *f.OrderExecution.Instructions("execInst")] = None

    closed_size: Annotated[PhemexDecimal | None, *f.Position.ClosedSize("closedSizeRq")] = None
    closed_pnl: Annotated[PhemexDecimal | None, *f.PNL.Closed("closedPnlRv")] = None
    cum_qty: Annotated[PhemexDecimal | None, *f.OrderQuantity.Cumulative("cumQtyRq")] = None
    cum_value: Annotated[PhemexDecimal | None, *f.OrderValue.Cumulative("cumValueRv")] = None
    leaves_qty: Annotated[PhemexDecimal | None, *f.OrderQuantity.Leaves("leavesQtyRq")] = None
    leaves_value: Annotated[PhemexDecimal | None, *f.OrderValue.Leaves("leavesValueRv")] = None
    display_qty: Annotated[PhemexDecimal | None, *f.OrderQuantity.Display("displayQtyRq")] = None

    peg_price: Annotated[PhemexDecimal | None, *f.OrderCondition.PegPrice("priceRq")] = None
    peg_proportion: Annotated[
        PhemexDecimal | None, *f.OrderCondition.PegOffsetProportion("pegOffsetProportionRr")] = None


class OpenOrder(OrderCore):
    order_id: Annotated[str, *f.Order.ID("orderID")]
    client_id: Annotated[str | None, *f.Order.ClientID("clOrdID")] = None
    error: Annotated[int, *f.ErrorCode("bizError")]
    order_type: Annotated[str, *f.Order.OrderType("orderType")]

    action_time: Annotated[int, *f.Time.Action("actionTimeNs")]
    trans_time: Annotated[int, *f.Time.Transaction("transactTimeNs")]
    order_status: Annotated[str, *f.Order.Status("ordStatus")]

    closed_size: Annotated[PhemexDecimal | None, *f.Position.ClosedSize("closedSizeRq")] = None
    closed_pnl: Annotated[PhemexDecimal | None, *f.PNL.Closed("closedPnlRv")] = None
    cum_value: Annotated[PhemexDecimal | None, *f.OrderValue.Cumulative("cumValueRv")] = None
    cum_qty: Annotated[PhemexDecimal | None, *f.OrderQuantity.Cumulative("cumQtyRq")] = None
    leaves_qty: Annotated[PhemexDecimal | None, *f.OrderQuantity.Leaves("leavesQtyRq")] = None
    leaves_value: Annotated[PhemexDecimal | None, *f.OrderValue.Leaves("leavesValueRv")] = None
    display_qty: Annotated[PhemexDecimal | None, *f.OrderQuantity.Display("displayQtyRq")] = None

    exec_instructions: Annotated[str | None, *f.OrderExecution.Instructions("execInst")] = None
    exec_status: Annotated[str | None, *f.OrderExecution.Status("execStatus")] = None

    peg_proportion: Annotated[
        PhemexDecimal | None, *f.OrderCondition.PegOffsetProportion("pegOffsetProportionRr")] = None


class OrderBuilder:
    """
    Mixin to add helper methods for building place order requests.
    Defaults (can be easily overriden):
    - Long
    - Market Order
    - Good Till Cancel (GTC)
    """

    def build(self) -> "PlaceOrderRequest":
        """Instantiate the final Pydantic model."""
        return PlaceOrderRequest(**self._data)

    def __init__(self, symbol: str):
        self._data: dict[str, Any] = {
            "symbol": symbol,
            "order_type": "Market",
            "time_in_force": "GoodTillCancel",
        }

    def increase_long(self, qty: PhemexDecimalLike) -> Self:
        """Orders default to Long unless explicitly set to Short."""
        self._data["quantity"] = qty
        self._data["pos_side"] = "Long"
        self._data["side"] = "Buy"
        self._data["reduce_only"] = False
        return self

    def reduce_long(self, qty: PhemexDecimalLike) -> Self:
        """Helper to reduce Long positions via Sell orders."""
        self._data["quantity"] = qty
        self._data["pos_side"] = "Long"
        self._data["side"] = "Sell"
        self._data["reduce_only"] = True
        return self

    def increase_short(self, qty: PhemexDecimalLike) -> Self:
        """Helper to increase Short positions via Sell orders."""
        self._data["quantity"] = qty
        self._data["pos_side"] = "Short"
        self._data["side"] = "Sell"
        self._data["reduce_only"] = False
        return self

    def reduce_short(self, qty: PhemexDecimalLike) -> Self:
        """Helper to reduce Short positions via Buy orders."""
        self._data["quantity"] = qty
        self._data["pos_side"] = "Short"
        self._data["side"] = "Buy"
        self._data["reduce_only"] = True
        return self

    def limit(self, price: PhemexDecimalLike) -> Self:
        self._data.update({
            "order_type": "Limit",
            "price": price,
        })
        return self

    def stop(self, stop_price: PhemexDecimalLike) -> Self:
        self._data.update({
            "order_type": "Stop",
            "stop_price": stop_price,
            "trigger": "ByLastPrice",
        })
        return self

    def tif(self, value: str) -> Self:
        """
        Default behavior is GoodTillCancel. Override with this method.
        """
        self._data["time_in_force"] = value
        return self


class PlaceOrderRequest(OrderCore):
    text: Annotated[str | None, *f.Request.Text("text")] = None
    pos_side: Annotated[str, *f.Position.Side("posSide")]
    sl_trigger: Annotated[str | None, *f.OrderCondition.StopLossTrigger("slTrigger")] = None
    tp_trigger: Annotated[str | None, *f.OrderCondition.TakeProfitTrigger("tpTrigger")] = None
    close_on_trigger: Annotated[bool | None, *f.OrderCondition.CloseOnTrigger("closeOnTrigger")] = None
    stp_instruction: Annotated[str | None, *f.OrderCondition.STPInstruction("stpInstruction")] = None

    @classmethod
    def builder(cls, symbol: str) -> OrderBuilder:
        """Helper to create an OrderBuilder for the given symbol."""
        return OrderBuilder(symbol)

    @model_validator(mode="after")
    def validate_quantity(self):
        if not self.quantity:
            raise ValidationError(message="Quantity is required for all orders")
        return self

    @model_validator(mode="after")
    def validate_limit_price(self):
        if self.order_type == "Limit" and not self.price:
            raise ValidationError(message="Price is required for Limit orders")
        return self

    @model_validator(mode="after")
    def validate_conditional_orders(self):
        conditional_types = {
            "Stop",
            "StopLimit",
            "MarketIfTouched",
            "LimitIfTouched",
            "ProtectedMarket",
            "StopAsLimit",
            "MarketIfTouchedAsLimit",
            "Bracket",
            "BoTpLimit",
            "BoSlLimit",
            "BoSlMarket",
        }
        if self.order_type in conditional_types and not self.stop_price:
            raise ValidationError(
                message=f"Stop Price is required for {self.order_type} orders",
                context=dict(
                    order_type=self.order_type,
                    order_type_options=list(conditional_types),
                )
            )
        return self

    @model_validator(mode="after")
    def validate_take_profit(self):
        if self.tp_price and not self.tp_trigger:
            raise ValidationError(message="Take Profit Trigger is required when Take Profit Price is set"
                                  )
        if self.tp_price_alt and not self.tp_price:
            raise ValidationError(message="Take Profit Price (Advanced) requires Take Profit Price")
        return self

    @model_validator(mode="after")
    def validate_stop_loss(self):
        if self.sl_price and not self.sl_trigger:
            raise ValidationError(message="Stop Loss Trigger is required when Stop Loss Price is set")
        if self.sl_price_alt and not self.sl_price:
            raise ValidationError(message="Stop Loss Price (Advanced) requires Stop Loss Price")
        return self

    @model_validator(mode="after")
    def validate_exclusive_flags(self):
        if self.reduce_only and self.close_on_trigger:
            raise ValidationError(message="Reduce Only and Close on Trigger cannot both be true")
        return self


class AmendOrderRequest(PhemexModel):
    order_id: Annotated[str | None, *f.Order.ID("orderID")] = None
    client_id: Annotated[str | None, *f.Order.ClientID("clOrdID")] = None
    pos_side: Annotated[str, *f.Position.Side("posSide")]
    symbol: Annotated[str, *f.Symbol("symbol")]

    quantity: Annotated[PhemexDecimal | None, *f.Order.Quantity("orderQtyRq")] = None
    price: Annotated[PhemexDecimal | None, *f.Order.Price("priceRp")] = None

    peg_type: Annotated[str | None, *f.OrderCondition.PegType("pegPriceType")] = None
    peg_offset: Annotated[PhemexDecimal | None, *f.OrderCondition.PegOffsetValue("pegOffsetValueRp")] = None
    stop_price: Annotated[PhemexDecimal | None, *f.OrderCondition.StopPrice("stopPxRp")] = None
    sl_price: Annotated[PhemexDecimal | None, *f.OrderCondition.StopLossPrice("stopLossRp")] = None
    tp_price: Annotated[PhemexDecimal | None, *f.OrderCondition.TakeProfitPrice("takeProfitRp")] = None
    trigger: Annotated[str | None, *f.OrderCondition.TriggerType("triggerType")] = None

    @model_validator(mode="after")
    def validate_ids(self):
        if not (self.order_id or self.client_id):
            raise ValidationError(message="Either Order ID or Client ID must be provided")
        if self.order_id and self.client_id:
            raise ValidationError(message="Provide only one of Order ID or Client ID, not both")
        return self

    @model_validator(mode="after")
    def validate_changes(self):
        if not any([
            self.price,
            self.quantity,
            self.peg_type,
            self.peg_offset,
            self.stop_price,
            self.sl_price,
            self.tp_price,
            self.trigger,
        ]):
            raise ValidationError(message="Cannot amend order without at least one change")
        return self


class CancelOrderRequest(PhemexModel):
    order_id: Annotated[str | None, *f.Order.ID("orderID")] = None
    client_id: Annotated[str | None, *f.Order.ClientID("clOrdID")] = None
    symbol: Annotated[str, *f.Symbol("symbol")]
    pos_side: Annotated[str, *f.Position.Side("posSide")]

    @model_validator(mode="after")
    def validate_ids(self):
        if not (self.order_id or self.client_id):
            raise ValidationError(message="Either Order ID or Client ID must be provided")
        if self.order_id and self.client_id:
            raise ValidationError(message="Provide only one of Order ID or Client ID, not both")
        return self

    @classmethod
    def make(cls, symbol: str, order_id: str):
        """Helper to create a CancelOrderRequest from an order ID."""
        return cls(
            symbol=symbol,
            order_id=order_id,
            pos_side="Long"  # TODO: extend configurability
        )


class BulkCancelOrderRequest(PhemexModel):
    order_ids: Annotated[list[str] | None, *f.Order.ID("orderID")] = None
    client_ids: Annotated[list[str] | None, *f.Order.ClientID("clOrdID")] = None
    symbol: Annotated[str, *f.Symbol("symbol")]
    pos_side: Annotated[str, *f.Position.Side("posSide")]

    @model_validator(mode="after")
    def validate_ids(self):
        if not (self.order_ids or self.client_ids):
            raise ValidationError(message="Either Order IDs or Client IDs must be provided")
        if self.order_ids and self.client_ids:
            raise ValidationError(message="Provide only one of Order IDs or Client IDs, not both")
        return self

    @classmethod
    def make(cls, symbol: str, order_ids: list[str]):
        """Helper to create a BulkCancelOrderRequest from a list of order IDs."""
        return cls(
            symbol=symbol,
            order_ids=order_ids,
            pos_side="Long"  # TODO: extend configurability
        )


class CancelAllOrdersRequest(PhemexModel):
    symbol: Annotated[str | None, *f.Symbol("symbol")] = None
    untriggered: Annotated[bool | None, *f.Request.Untriggered("untriggered")] = None
    text: Annotated[str | None, *f.Request.Text("text")] = None

    @classmethod
    def make(cls, symbol: str, untriggered: bool = True):
        """
        Helper to create a CancelAllOrdersRequest from a symbol.
        Untriggered = False to cancel all orders including triggered ones.
        """
        return cls(
            symbol=symbol,
            untriggered=untriggered,
        )


class ClosedOrdersRequest(PhemexModel):
    symbol: Annotated[str | None, *f.Symbol("symbol")] = None
    currency: Annotated[str, *f.Currency("currency")]
    order_status: Annotated[int | None, *f.OrderCode.Status("ordStatus")] = None
    order_type: Annotated[int | None, *f.OrderCode.OrderType("ordType")] = None
    start_time: Annotated[int, *f.Request.StartTime("start")]
    end_time: Annotated[int, *f.Request.EndTime("end")]
    offset: Annotated[int, *f.Request.Offset("offset")]
    limit: Annotated[int, *f.Request.Limit("limit")]
    with_count: Annotated[bool | None, *f.Request.IncludeCount("withCount")] = None

    @classmethod
    def default(cls, symbol: str, currency: str = "USDT") -> Self:
        return cls(
            symbol=symbol,
            currency=currency,
            start_time=unix_now() - MS.WEEK,
            end_time=unix_now() - MS.MINUTE,
            offset=0,
            limit=200,
        )


class ClosedOrder(PhemexModel):
    order_id: Annotated[str, *f.Order.ID("orderId")]
    client_id: Annotated[str, *f.Order.ClientID("clOrdId")]
    created_at: Annotated[int, *f.Time.CreatedAt("createdAt")]
    updated_at: Annotated[int, *f.Time.UpdatedAt("updatedAt")]
    action_by: Annotated[int, *f.Action.User("actionBy")]
    order_details: Annotated[str | None, *f.Order.Details("orderDetailsVos")] = None
    order_status: Annotated[int, *f.OrderCode.Status("ordStatus")]
    execution_status: Annotated[int, *f.OrderCode.ExecutionStatus("execStatus")]
    error_code: Annotated[int, *f.ErrorCode("bizError")]

    symbol: Annotated[str, *f.Symbol("symbol")]
    order_type: Annotated[int, *f.OrderCode.OrderType("ordType")]
    trade_type: Annotated[int, *f.OrderCode.TradeType("tradeType")]
    pos_side: Annotated[int, *f.OrderCode.PositionSide("posSide")]
    side: Annotated[int, *f.OrderCode.Side("side")]
    quantity: Annotated[PhemexDecimal, *f.Order.Quantity("orderQtyRq")]
    price: Annotated[PhemexDecimal, *f.Order.Price("priceRp")]

    peg_type: Annotated[int, *f.OrderCode.PegType("pegPriceType")]
    peg_offset: Annotated[PhemexDecimal | None, *f.OrderCondition.PegOffsetValue("pegOffsetValueRp")] = None
    stop_direction: Annotated[int, *f.OrderCode.StopDirection("stopDirection")]
    stop_price: Annotated[PhemexDecimal, *f.OrderCondition.StopPrice("stopPxRp")]
    trigger: Annotated[int, *f.OrderCode.TriggerType("trigger")]

    display_quantity: Annotated[PhemexDecimal | None, *f.OrderQuantity.Display("displayQtyRq")] = None
    execution_quantity: Annotated[PhemexDecimal, *f.OrderExecution.Quantity("execQtyRq")]
    leaves_quantity: Annotated[PhemexDecimal, *f.OrderQuantity.Leaves("leavesQtyRq")]

    execution_price: Annotated[PhemexDecimal, *f.OrderExecution.Price("execPriceRp")]
    average_price: Annotated[PhemexDecimal | None, *f.OrderValue.AverageTransactionPrice("avgTransactPriceRp")] = None

    cumulative_value: Annotated[PhemexDecimal, *f.OrderValue.Cumulative("cumValueRv")]
    order_value: Annotated[PhemexDecimal, *f.OrderValue.Nominal("orderValueRv")]
    leaves_value: Annotated[PhemexDecimal, *f.OrderValue.Leaves("leavesValueRv")]

    execution_fee: Annotated[PhemexDecimal, *f.OrderExecution.Fee("execFeeRv")]
    total_pnl: Annotated[PhemexDecimal | None, *f.PNL.Total("totalPnlRv")] = None


class OrderHistoryItem(PhemexModel):
    order_id: Annotated[str, *f.Order.ID("orderId")]
    client_id: Annotated[str, *f.Order.ClientID("clOrdId")]
    status: Annotated[str, *f.Order.Status("ordStatus")]
    action_time: Annotated[int, *f.Time.Action("actionTimeNs")]
    transact_time: Annotated[int, *f.Time.Transaction("transactTimeNs")]
    error_code: Annotated[int, *f.ErrorCode("bizError")]

    order_type: Annotated[str, *f.Order.OrderType("ordType")]
    symbol: Annotated[str, *f.Symbol("symbol")]
    side: Annotated[str, *f.Order.Side("side")]
    quantity: Annotated[PhemexDecimal, *f.Order.Quantity("orderQtyRq")]
    price: Annotated[PhemexDecimal, *f.Order.Price("priceRp")]

    closed_pnl: Annotated[PhemexDecimal, *f.PNL.Closed("closedPnlRv")]
    closed_size: Annotated[PhemexDecimal, *f.Position.ClosedSize("closedSizeRq")]
    cum_quantity: Annotated[PhemexDecimal, *f.OrderQuantity.Cumulative("cumQtyRq")]
    cum_value: Annotated[PhemexDecimal, *f.OrderValue.Cumulative("cumValueRv")]
    display_quantity: Annotated[PhemexDecimal, *f.OrderQuantity.Display("displayQtyRq")]
    leaves_quantity: Annotated[PhemexDecimal, *f.OrderQuantity.Leaves("leavesQtyRq")]
    leaves_value: Annotated[PhemexDecimal, *f.OrderValue.Leaves("leavesValueRv")]

    reduce_only: Annotated[bool, *f.OrderCondition.ReduceOnly("reduceOnly")]
    time_in_force: Annotated[str, *f.OrderCondition.TimeInForce("timeInForce")]
    stop_direction: Annotated[str, *f.OrderCondition.StopDirection("stopDirection")]
    sl_price: Annotated[PhemexDecimal, *f.OrderCondition.StopLossPrice("stopLossRp")]
    tp_price: Annotated[PhemexDecimal, *f.OrderCondition.TakeProfitPrice("takeProfitRp")]


# --------------------------------------
# Position related models
# --------------------------------------


class Account(PhemexModel):
    account_id: Annotated[int, *f.Account.ID("accountId")]
    user_id: Annotated[int, *f.User.ID("userID")]
    user_mode: Annotated[int | None, *f.User.Mode("userMode")] = None
    status: Annotated[int | None, *f.Account.Status("status")] = None
    currency: Annotated[str, *f.Currency("currency")]
    total_balance: Annotated[PhemexDecimal, *f.AccountBalance.Total("accountBalanceRv")]
    used_balance: Annotated[PhemexDecimal, *f.AccountBalance.Used("totalUsedBalanceRv")]
    bonus_balance: Annotated[PhemexDecimal, *f.AccountBalance.Bonus("bonusBalanceRv")]

    @property
    def balance(self) -> PhemexDecimal:
        """Calculate and return the available balance as a float."""
        return self.total_balance - self.used_balance


class PositionCore(PhemexModel, ABC):
    account_id: Annotated[int, *f.Account.ID("accountID")]
    exec_seq: Annotated[int, *f.Position.ExecutionSequence("execSeq")]
    status: Annotated[str, *f.Position.Status("positionStatus")]

    symbol: Annotated[str, *f.Symbol("symbol")]
    currency: Annotated[str, *f.Currency("currency")]
    side: Annotated[str | None, *f.Order.Side("side")] = None
    pos_side: Annotated[str, *f.Position.Side("posSide")]
    pos_mode: Annotated[str, *f.Position.Mode("posMode")]

    assigned_balance: Annotated[PhemexDecimal, *f.PositionBalance.Assigned("assignedPosBalanceRv")]
    used_balance: Annotated[PhemexDecimal, *f.PositionBalance.Used("usedBalanceRv")]
    value: Annotated[PhemexDecimal, *f.PositionValue.Nominal("valueRv")]

    entry_price: Annotated[PhemexDecimal, *f.PositionPrice.Entry("avgEntryPriceRp")]
    bankrupt_price: Annotated[PhemexDecimal, *f.PositionPrice.Bankrupt("bankruptPriceRp")]
    liquidation_price: Annotated[PhemexDecimal, *f.PositionPrice.Liquidation("liquidationPriceRp")]
    mark_price: Annotated[PhemexDecimal, *f.Price.Mark("markPriceRp")]

    margin: Annotated[PhemexDecimal, *f.PositionMargin.Allocated("positionMarginRv")]
    initial_margin: Annotated[PhemexDecimal, *f.ProductRisk.InitialMargin("initMarginReqRr")]
    maintenance_margin: Annotated[PhemexDecimal, *f.ProductRisk.MaintenanceMargin("maintMarginReqRr")]
    cross_margin: Annotated[bool | None, *f.PositionMargin.Cross("crossMargin")] = None

    cum_closed_pnl: Annotated[PhemexDecimal, *f.PNL.CumulativeClosed("cumClosedPnlRv")]
    cur_realized_pnl: Annotated[PhemexDecimal, *f.PNL.CurrentRealized("curTermRealisedPnlRv")]
    estimated_loss: Annotated[PhemexDecimal, *f.PositionLoss.Estimated("estimatedOrdLossRv")]
    bankrupt_comm: Annotated[PhemexDecimal, *f.PositionRisk.BankruptCommission("bankruptCommRv")]

    buy_to_cost: Annotated[PhemexDecimal, *f.PositionCost.BuySideCost("buyValueToCostRr")]
    sell_to_cost: Annotated[PhemexDecimal, *f.PositionCost.SellSideCost("sellValueToCostRr")]
    cost_basis: Annotated[PhemexDecimal, *f.PositionCost.CostBasis("posCostRv")]

    deleverage_percentile: Annotated[PhemexDecimal, *f.PositionRisk.DeleveragePercentile("deleveragePercentileRr")]
    leverage_ratio: Annotated[PhemexDecimal, *f.PositionLeverage.Ratio("leverageRr")]
    risk_limit: Annotated[PhemexDecimal, *f.PositionRisk.RiskLimit("riskLimitRv")]

    term: Annotated[int, *f.PositionTerm.Index("term")]
    last_term: Annotated[int, *f.PositionTerm.LastTermEndTime("lastTermEndTimeNs")]
    last_funding: Annotated[int, *f.PositionTerm.LastFundingTime("lastFundingTimeNs")]
    cum_funding_fee: Annotated[PhemexDecimal, *f.PositionFee.CumulativeFunding("cumFundingFeeRv")]
    cum_trans_fee: Annotated[PhemexDecimal, *f.PositionFee.CumulativeTransaction("cumTransactFeeRv")]


class Position(PositionCore):
    user_id: Annotated[int, *f.User.ID("userID")]
    trans_time: Annotated[int, *f.Time.Transaction("transactTimeNs")]

    size: Annotated[PhemexDecimal, *f.Position.Size("size")]
    entry_price_alt: Annotated[PhemexDecimal, *f.PositionPrice.Entry("avgEntryPrice", alt=True)]

    buy_quantity: Annotated[PhemexDecimal, *f.OrderQuantity.BuyLeaves("buyLeavesQtyRq")]
    buy_value: Annotated[PhemexDecimal, *f.OrderValue.BuyLeaves("buyLeavesValueRv")]
    sell_quantity: Annotated[PhemexDecimal, *f.OrderQuantity.SellLeaves("sellLeavesQtyRq")]
    sell_value: Annotated[PhemexDecimal, *f.OrderValue.SellLeaves("sellLeavesValueRv")]

    maker_fee: Annotated[PhemexDecimal, *f.PositionFee.Maker("makerFeeRateRr")]
    taker_fee: Annotated[PhemexDecimal, *f.PositionFee.Taker("takerFeeRateRr")]


class PositionResponse(PhemexModel):
    account: Annotated[Account, f.NestedModel("account")]
    positions: Annotated[list[Position], f.NestedModel("positions")]


class PositionWithPnL(PositionCore):
    size: Annotated[PhemexDecimal, *f.Position.Size("sizeRq")]
    mark_value: Annotated[PhemexDecimal | None, *f.PositionValue.Mark("markValueEv", scaled=True)] = None
    sl_price: Annotated[PhemexDecimal, *f.OrderCondition.StopLossPrice("stopLossEp", scaled=True)]
    tp_price: Annotated[PhemexDecimal, *f.OrderCondition.TakeProfitPrice("takeProfitEp", scaled=True)]

    realized_pnl: Annotated[PhemexDecimal | None, *f.PNL.Realized("realisedPnlEv", scaled=True)] = None
    cum_realized_pnl: Annotated[PhemexDecimal | None, *f.PNL.CumulativeRealized("cumRealisedPnlEv", scaled=True)] = None
    unrealized_pnl: Annotated[PhemexDecimal, *f.PNL.Unrealized("unRealisedPnlRv")]
    unrealized_loss: Annotated[
        PhemexDecimal | None, *f.PositionLoss.Unrealized("unRealisedPosLossEv", scaled=True)] = None

    @property
    def equity(self) -> PhemexDecimal:
        """
        Equity of this position = margin + unrealized PnL.
        This represents the current account value tied to this position.
        """
        return self.margin + self.unrealized_pnl


class PositionWithPnLResponse(PhemexModel):
    account: Annotated[Account, f.NestedModel("account")]
    positions: Annotated[list[PositionWithPnL], f.NestedModel("positions")]

    def get(self, symbol: str) -> PositionWithPnL | None:
        """Get a position by symbol, or return None if not found."""
        for pos in self.positions:
            if pos.symbol == symbol and pos.size != 0:
                return pos

        return None

    @property
    def exposure(self) -> PhemexDecimal:
        """Total absolute notional exposure (risk size) across all positions."""
        values = [pos.value for pos in self.positions]
        return PhemexDecimal.sum(values)

    @property
    def equity(self) -> PhemexDecimal:
        """
        Account equity = true account value.
        Safest is to use Phemex's own field directly.
        """
        return self.account.total_balance

    @property
    def cash(self) -> PhemexDecimal:
        """Shortcut to available cash (free balance)."""
        return self.account.balance


class ClosedPositionRequest(PhemexModel):
    symbol: Annotated[str | None, *f.Symbol("symbol")] = None
    currency: Annotated[str | None, *f.Currency("currency")] = None
    offset: Annotated[int, *f.Request.Offset("offset")] = None
    limit: Annotated[int, *f.Request.Limit("limit")] = None
    count: Annotated[bool | None, *f.Request.IncludeCount("withCount")] = None

    @classmethod
    def default(cls, symbol: str, currency: str = "USDT") -> Self:
        return cls(
            symbol=symbol,
            currency=currency,
            offset=0,
            limit=200,
            count=False
        )


class ClosedPosition(PhemexModel):
    symbol: Annotated[str, *f.Symbol("symbol")]
    currency: Annotated[str, *f.Currency("currency")]
    side: Annotated[int, *f.OrderCode.Side("side")]
    finished: Annotated[int, *f.Position.FinishedFlag("finished")]
    closed_size: Annotated[PhemexDecimal, *f.Position.ClosedSize("closedSizeRq")]

    open_time: Annotated[int, *f.Position.OpenTime("openedTimeNs")]
    updated_time: Annotated[int, *f.Time.LastUpdated("updatedTimeNs")]
    open_price: Annotated[PhemexDecimal, *f.PositionPrice.Open("openPrice")]
    close_price: Annotated[PhemexDecimal, *f.Price.Close("closePrice")]

    cum_entry_value: Annotated[PhemexDecimal | None, *f.PositionValue.CumulativeEntry("cumEntryValueRv")] = None
    closed_pnl: Annotated[PhemexDecimal, *f.PNL.Closed("closedPnlRv")]
    realized_pnl: Annotated[PhemexDecimal | None, *f.PNL.Realized("realizedPnlRv")] = None
    roi: Annotated[PhemexDecimal, *f.Position.ROI("roi")]

    leverage: Annotated[PhemexDecimal, *f.PositionLeverage.Current("leverage")]
    term: Annotated[int, *f.PositionTerm.Index("term")]
    funding_fee: Annotated[PhemexDecimal, *f.Funding.Fee("fundingFeeRv")]
    exchange_fee: Annotated[PhemexDecimal, *f.PositionFee.Exchange("exchangeFeeRv")]


# --------------------------------------
# Risk related models
# --------------------------------------


class SwitchModeRequest(PhemexModel):
    symbol: Annotated[str, *f.Symbol("symbol")]
    mode: Annotated[str, *f.Position.Mode("targetPosMode")]


class AssignPositionBalanceRequest(PhemexModel):
    symbol: Annotated[str, *f.Symbol("symbol")]
    side: Annotated[str, *f.Position.Side("posSide")]
    amount: Annotated[PhemexDecimal, *f.PositionBalance.Assigned("posBalanceRv")]


class SetLeverageRequest(PhemexModel):
    symbol: Annotated[str, *f.Symbol("symbol")]
    one_way: Annotated[PhemexDecimal | None, *f.PositionLeverage.Leverage("leverageRr")] = None
    long: Annotated[PhemexDecimal | None, *f.PositionLeverage.LongLeverage("longLeverageRr")] = None
    short: Annotated[PhemexDecimal | None, *f.PositionLeverage.ShortLeverage("shortLeverageRr")] = None

    @classmethod
    def create(cls, symbol: str, leverage: PhemexDecimalLike) -> Self:
        """Helper to quickly change leverage for hedged mode for a given symbol."""
        return cls.model_validate(dict(
            symbol=symbol,
            long=PhemexDecimal(leverage),
            short=PhemexDecimal(leverage),
        ))

    @model_validator(mode="after")
    def validate_leverage_fields(self):
        if self.one_way:  # OneWay mode: cannot use long/short self
            if self.long or self.short:
                raise ValidationError(
                    message="Provide either One-Way Leverage OR both Long Leverage and Short Leverage, not both")
        else:  # Hedged mode: both long and short must exist together
            long = self.long is not None
            short = self.long is not None
            if long != short:
                raise ValidationError(message="Both Long Leverage and Short Leverage must be provided in Hedged mode")
            if not (long and short):
                raise ValidationError(message="Must provide One-Way Leverage OR Long Leverage + Short Leverage")
        return self


class RiskUnitResponse(PhemexModel):
    user_id: Annotated[int, *f.User.ID("userId")]
    symbol: Annotated[str, *f.Symbol("symbol")]
    currency_code: Annotated[int, *f.Product.Code("valuationCcy")]
    pos_side: Annotated[str, *f.Position.Side("posSide")]
    riskMode: Annotated[str, *f.PositionRisk.RiskMode("riskMode")]

    equity: Annotated[PhemexDecimal, *f.PositionBalance.Equity("totalEquityRv")]
    used_balance: Annotated[PhemexDecimal, *f.PositionBalance.Locked("totalOrdUsedBalanceRv")]
    total_balance: Annotated[PhemexDecimal, *f.PositionBalance.Current("totalBalanceRv")]
    estimated_balance: Annotated[PhemexDecimal, *f.PositionBalance.Estimated("estAvailableBalanceRv")]
    free_balance: Annotated[PhemexDecimal | None, *f.PositionBalance.Free("totalFreeRv")] = None
    fixed_balance: Annotated[PhemexDecimal, *f.PositionBalance.Fixed("fixedUsedRv")]

    margin_ratio: Annotated[PhemexDecimal, *f.PositionMargin.Ratio("marginRatioRr")]
    total_position_pnl: Annotated[PhemexDecimal, *f.PNL.PositionTotal("totalPosUnpnlRv")]
    total_position_cost: Annotated[PhemexDecimal, *f.PositionCost.TotalPositionCost("totalPosCostRv")]
    total_position_mm: Annotated[PhemexDecimal, *f.PositionRisk.TotalPositionMM("totalPosMMRv")]
    total_open_loss: Annotated[PhemexDecimal, *f.PositionLoss.Open("totalOrdOpenLossRv")]


# --------------------------------------
# Market Data related models
# --------------------------------------


class OrderBookEntry(PhemexModel):
    price: Annotated[PhemexDecimal, *f.Order.Price("priceRp")]
    size: Annotated[PhemexDecimal, *f.Position.Size("sizeRp")]


class OrderBookData(PhemexModel):
    asks: Annotated[list[OrderBookEntry], f.NestedModel("asks")]
    bids: Annotated[list[OrderBookEntry], f.NestedModel("bids")]

    @field_validator("asks", "bids", mode="before")
    @classmethod
    def _convert_nested_lists(cls, v):
        """Convert [[price, size], ...] to list[OrderBookEntry]."""
        if isinstance(v, list) and v and isinstance(v[0], list):
            return [{"price": price, "size": size} for price, size in v]
        return v


class OrderBookResponse(PhemexModel):
    orderbook: Annotated["OrderBookData", f.NestedModel("orderbook_p")]

    symbol: Annotated[str, *f.Symbol("symbol")]
    depth: Annotated[int, *f.OrderBook.Depth("depth")]
    kind: Annotated[str, *f.OrderBook.Kind("type")]
    sequence: Annotated[int, *f.OrderBook.Sequence("sequence")]
    timestamp: Annotated[int, *f.Time.Timestamp("timestamp")]
    data_ts: Annotated[int, *f.Time.Data("dts")]
    match_ts: Annotated[int, *f.Time.Match("mts")]


class KlineRequest(PhemexModel):
    symbol: Annotated[str, *f.Symbol("symbol")]
    resolution: Annotated[int, *f.Request.Resolution("resolution")]
    limit: Annotated[int | None, *f.Request.Limit("limit")] = None


class Kline(PhemexModel):
    timestamp: Annotated[int, *f.Time.Timestamp("timestamp")]
    last_close: Annotated[PhemexDecimal, *f.Price.Close("closePrice")]
    open: Annotated[PhemexDecimal, *f.Price.Open("openRp")]
    high: Annotated[PhemexDecimal, *f.Price.High("highRp")]
    low: Annotated[PhemexDecimal, *f.Price.Low("lowRp")]
    close: Annotated[PhemexDecimal, *f.Price.Close("closePrice")]
    volume: Annotated[PhemexDecimal, *f.Price.Volume("volumeRq")]
    turnover: Annotated[PhemexDecimal, *f.Price.Turnover("turnoverRv")]

    @classmethod
    def model_validate(cls, obj, *args, **kwargs) -> Self:
        """Convert [timestamp, open, high, low, close, volume, turnover] to Kline."""
        if isinstance(obj, list):
            data = {
                "timestamp": obj[0],
                "last_close": obj[1],
                "open": obj[2],
                "high": obj[3],
                "low": obj[4],
                "close": obj[5],
                "volume": obj[6],
                "turnover": obj[7],
            }
            return super().model_validate(data, *args, **kwargs)
        raise ValueError("Wrong input passed to build klines")


class Ticker(PhemexModel):
    symbol: Annotated[str, *f.Symbol("symbol")]
    timestamp: Annotated[int, *f.Time.Timestamp("timestamp")]

    ask: Annotated[PhemexDecimal, *f.Price.Ask("askRp")]
    bid: Annotated[PhemexDecimal, *f.Price.Bid("bidRp")]
    mark: Annotated[PhemexDecimal, *f.Price.Mark("markRp")]
    last: Annotated[PhemexDecimal, *f.Price.Last("lastRp")]
    open: Annotated[PhemexDecimal, *f.Price.Open("openRp")]
    high: Annotated[PhemexDecimal, *f.Price.High("highRp")]
    low: Annotated[PhemexDecimal, *f.Price.Low("lowRp")]

    index: Annotated[PhemexDecimal, *f.Price.Index("indexRp")]
    open_interest: Annotated[PhemexDecimal, *f.Price.OpenInterest("openInterestRv")]
    turnover: Annotated[PhemexDecimal, *f.Price.Turnover("turnoverRv")]
    volume: Annotated[PhemexDecimal, *f.Price.Volume("volumeRq")]

    funding_rate: Annotated[PhemexDecimal, *f.Funding.Rate("fundingRateRr")]
    pred_funding_rate: Annotated[PhemexDecimal, *f.Funding.PredictedFundingRate("predFundingRateRr")]

    @property
    def mid(self) -> PhemexDecimal:
        """Midpoint between best bid and best ask."""
        return (self.bid + self.ask) / 2


# --------------------------------------
# Trade related models
# --------------------------------------

class Trade(PhemexModel):
    timestamp: Annotated[int, *f.Time.Timestamp("timestamp")]
    side: Annotated[str, *f.Order.Side("side")]
    price: Annotated[PhemexDecimal, *f.Order.Price("priceRp")]
    size: Annotated[PhemexDecimal, *f.Position.Size("sizeRq")]


class TradeResponse(PhemexModel):
    trades: Annotated[list[Trade], f.NestedModel("trades_p")]

    symbol: Annotated[str, *f.Symbol("symbol")]
    kind: Annotated[str, *f.OrderBook.Kind("type")]
    sequence: Annotated[int, *f.OrderBook.Sequence("sequence")]
    data_ts: Annotated[int, *f.Time.Data("dts")]
    match_ts: Annotated[int, *f.Time.Match("mts")]

    @field_validator("trades", "sequence", mode="before")
    @classmethod
    def _convert_nested_lists(cls, v):
        """Convert [[timestamp, side, price, size], ...] to list[Trade]."""
        if isinstance(v, list) and v and isinstance(v[0], list):
            return [{"timestamp": ts, "side": side, "price": price, "size": size} for ts, side, price, size in v]
        return v


class TradeRequestCore(PhemexModel, ABC):
    symbol: Annotated[str | None, *f.Symbol("symbol")] = None
    currency: Annotated[str | None, *f.Currency("currency")] = None
    offset: Annotated[int | None, *f.Request.Offset("offset")] = None
    limit: Annotated[int | None, *f.Request.Limit("limit")] = None


class TradeResponseCore(PhemexModel, ABC):
    symbol: Annotated[str, *f.Symbol("symbol")]
    currency: Annotated[str, *f.Currency("currency")]
    quantity: Annotated[PhemexDecimal, *f.Order.Quantity("orderQtyRq")]
    price: Annotated[PhemexDecimal, *f.Order.Price("priceRp")]
    fee_rate: Annotated[PhemexDecimal, *f.Funding.FeeRate("feeRateRr")]

    execution_quantity: Annotated[PhemexDecimal, *f.OrderExecution.Quantity("execQtyRq")]
    execution_price: Annotated[PhemexDecimal, *f.OrderExecution.Price("execPriceRp")]
    execution_value: Annotated[PhemexDecimal, *f.OrderExecution.Value("execValueRv")]
    execution_fee: Annotated[PhemexDecimal, *f.OrderExecution.Fee("execFeeRv")]


class UserTradeRequest(TradeRequestCore):
    execution_type: Annotated[int | None, *f.OrderCode.ExecutionType("execType")] = None
    with_count: Annotated[bool | None, *f.Request.IncludeCount("withCount")]

    @classmethod
    def default(cls, symbol: str, currency: str = "USDT") -> Self:
        return cls(
            symbol=symbol,
            currency=currency,
            offset=0,
            limit=200,
            with_count=False
        )


class UserTrade(TradeResponseCore):
    action: Annotated[int, *f.Action.Code("action")]
    created_at: Annotated[int, *f.Time.CreatedAt("createdAt")]

    trade_type: Annotated[int, *f.OrderCode.TradeType("tradeType")]
    order_type: Annotated[int, *f.OrderCode.OrderType("ordType")]
    side: Annotated[int, *f.OrderCode.Side("side")]
    pos_side: Annotated[int, *f.OrderCode.PositionSide("posSide")]

    execution_id: Annotated[str, *f.OrderExecution.ID("execId")]
    execution_status: Annotated[int, *f.OrderCode.ExecutionStatus("execStatus")]
    position_fee: Annotated[PhemexDecimal, *f.PositionFee.Current("ptFeeRv")]
    position_price: Annotated[PhemexDecimal, *f.PositionPrice.Current("ptPriceRp")]
    peg_type: Annotated[int, *f.OrderCode.PegType("pegPriceType")]
    peg_offset: Annotated[PhemexDecimal | None, *f.OrderCondition.PegOffsetValue("pegOffsetValueRp")] = None


class TradeHistoryRequest(TradeRequestCore):
    start: Annotated[int | None, *f.Request.StartTime("start")] = None
    end: Annotated[int | None, *f.Request.EndTime("end")] = None

    @model_validator(mode="after")
    def validate_symbol(self):
        if not (self.symbol or self.currency):
            raise ValidationError(message="Either Symbol or Currency must be provided")
        if self.symbol and self.currency:
            raise ValidationError(message="Provide only one of Symbol or Currency, not both")
        return self


class TradeHistoryItem(TradeResponseCore):
    order_id: Annotated[str, *f.Order.ID("orderID")]
    client_id: Annotated[str, *f.Order.ClientID("clOrdID")]
    action: Annotated[str, *f.Action.Name("action")]
    transaction_time: Annotated[int, *f.Time.Transaction("transactTimeNs")]

    trade_type: Annotated[str, *f.Order.TradeType("tradeType")]
    order_type: Annotated[str, *f.Order.OrderType("ordType")]
    side: Annotated[str, *f.Order.Side("side")]
    pos_side: Annotated[str, *f.Position.Side("posSide")]

    execution_id: Annotated[str, *f.OrderExecution.ID("execID")]
    execution_status: Annotated[str, *f.OrderExecution.Status("execStatus")]
    closed_size: Annotated[PhemexDecimal, *f.Position.ClosedSize("closedSizeRq")]
    closed_pnl: Annotated[PhemexDecimal, *f.PNL.Closed("closedPnlRv")]


# --------------------------------------
# Funding related models
# --------------------------------------


class FundingFeeRequest(PhemexModel):
    symbol: Annotated[str, *f.Symbol("symbol")]
    offset: Annotated[int | None, *f.Request.Offset("offset")] = None
    limit: Annotated[int | None, *f.Request.Limit("limit")] = None


class FundingFeeItem(PhemexModel):
    symbol: Annotated[str, *f.Symbol("symbol")]
    currency: Annotated[str, *f.Currency("currency")]
    side: Annotated[str, *f.Order.Side("side")]
    created_at: Annotated[int, *f.Time.CreatedAt("createTime")]

    execution_quantity: Annotated[PhemexDecimal, *f.OrderExecution.Quantity("execQtyRq")]
    execution_price: Annotated[PhemexDecimal, *f.OrderExecution.Price("execPriceRp")]
    execution_value: Annotated[PhemexDecimal, *f.OrderExecution.Value("execValueRv")]
    execution_fee: Annotated[PhemexDecimal, *f.OrderExecution.Fee("execFeeRv")]

    funding_rate: Annotated[PhemexDecimal, *f.Funding.Rate("fundingRateRr")]
    fee_rate: Annotated[PhemexDecimal, *f.Funding.FeeRate("feeRateRr")]


class FundingRateRequest(PhemexModel):
    symbol: Annotated[str | None, *f.Symbol("symbol")] = None
    order_by_column: Annotated[str | None, *f.Request.OrderBy("orderByColumn")] = None
    order_by: Annotated[str | None, *f.Request.Order("orderBy")] = None
    page_num: Annotated[int | None, *f.Request.PageNumber("pageNum")] = None
    page_size: Annotated[int | None, *f.Request.PageSize("pageSize")] = None


class FundingRateItem(PhemexModel):
    symbol: Annotated[str, *f.Symbol("symbol")]

    funding_interval: Annotated[int, *f.Funding.Interval("fundingInterval")]
    remaining_funding_time: Annotated[int, *f.Funding.RemainingFundingTime("toNextfundingInterval")]
    next_funding_time: Annotated[int, *f.Funding.NextFundingTime("nextfundingTime")]

    funding_rate: Annotated[PhemexDecimal, *f.Funding.Rate("fundingRate")]
    interest_rate: Annotated[PhemexDecimal, *f.Funding.InterestRate("interestRate")]
    rate_cap: Annotated[PhemexDecimal, *f.Funding.RateCap("fundingRateCap")]
    rate_floor: Annotated[PhemexDecimal, *f.Funding.RateFloor("fundingRateFloor")]

from abc import ABC
from pydantic import Field

from .models import options, PhemexScale


class FieldInfo(ABC):
    """
    Base class for defining Phemex API fields with metadata.
    Used to help reduce boilerplate when defining many fields.
    """
    field: dict  # pydantic field info as dict
    options: list[str] | None = None  # optional options for str fields
    scale: PhemexScale | None = None

    def __new__(cls, alias: str, scaled: bool = False, alt: bool = False) -> tuple:
        """When called, return the tuple of metadata instead of an instance."""
        info = {**cls.field}
        if alt:
            info["title"] = f"Alternative {info.get('title', alias)}"
            info["description"] = f"{info.get('description', alias)} (alternative provided by Phemex)"
        field = Field(serialization_alias=alias, validation_alias=alias, **info)
        parts = [field]
        if cls.options:
            defaults = [None, "", "UNSPECIFIED"]
            opts = options(*defaults, *cls.options)
            parts.append(opts)
        if cls.scale and scaled:
            parts.append(cls.scale)
        return tuple(parts)


class NestedModel:
    def __new__(cls, alias: str) -> type[Field]:
        """When called, return the tuple of metadata instead of an instance."""
        return Field(
            serialization_alias=alias,
            validation_alias=alias,
            title=f"Nested {alias}",
            description=f"Nested model for {alias}"
        )


class ErrorCode(FieldInfo):
    field = dict(
        title="Error code",
        description="Phemex error code, 0 if no error"
    )


class User:
    """
    User information
    """

    class ID(FieldInfo):
        field = dict(
            title="User ID",
            description="Phemex user ID"
        )

    class Mode(FieldInfo):
        field = dict(
            title="User Mode",
            description="User mode: Normal or Liquidation"
        )


class Account:
    """
    Fields relating to Phemex account and subaccount information.
    """

    class ID(FieldInfo):
        field = dict(
            title="Account ID",
            description="Phemex sub-account ID"
        )

    class Status(FieldInfo):
        field = dict(
            title="Account Status",
            description="Status of the account"
        )


class AccountBalance:
    """
    Fields relating to balance information at the account level.
    """

    class Bonus(FieldInfo):
        field = dict(
            title="Bonus Balance",
            description="Bonus balance that can be used for trading but not withdrawn"
        )

    class Used(FieldInfo):
        field = dict(
            title="Used Balance",
            description="Total balance currently used as margin for open positions and orders"
        )

    class Total(FieldInfo):
        field = dict(
            title="Total Balance",
            description="Total account balance including used margin"
        )


class Action:
    """
    Fields relating to actions taken on orders as defined by Phemex.
    """

    class Name(FieldInfo):
        field = dict(
            title="Action",
            description="Action taken on the order"
        )

    class Code(FieldInfo):
        """
        New(1), Cancel(2), Replace(3), CancelAll(4),SettleFundingFee(13)
        """
        field = dict(
            title="Action Code",
            description="Numeric code representing the action taken"
        )

    class User(FieldInfo):
        """
        ByUser(1)
        """
        field = dict(
            title="Action By Code",
            description="Numeric code representing who initiated the action"
        )


class Currency(FieldInfo):
    """
    Fields relating to currency information. To use "standard" currency, just invoke the base of this class.
    """
    field = dict(
        title="Currency Symbol",
        description="Symbol code of the currency (e.g., BTC, ETH)"
    )

    class Display(FieldInfo):
        field = dict(
            title="Display Currency",
            description="Currency symbol used for display, often same as main currency symbol"
        )

    class Base(FieldInfo):
        field = dict(
            title="Base Currency",
            description="Base currency of the trading pair"
        )

    class Quote(FieldInfo):
        field = dict(
            title="Quote Currency",
            description="Currency in which the contract is quoted"
        )

    class Settle(FieldInfo):
        field = dict(
            title="Settlement Currency",
            description="Currency in which the contract is settled"
        )

    class PerpetualFlag(FieldInfo):
        field = dict(
            title="Perpetual Contract Flag",
            description="Flag indicating whether the currency is associated with perpetual contracts (1 = yes)"
        )

    class StableCoinFlag(FieldInfo):
        field = dict(
            title="Stablecoin Flag",
            description="Flag indicating whether the currency is a stablecoin (1 = stablecoin)"
        )


class Funding:
    class Fee(FieldInfo):
        field = dict(
            title="Funding Fee",
            description="Funding fee paid or received at the last funding timestamp"
        )

    class FeeRate(FieldInfo):
        field = dict(
            title="Fee Rate",
            description="Fee rate applied to this order"
        )

    class Rate(FieldInfo):
        field = dict(
            title="Funding Rate",
            description="Current funding rate"
        )

    class RateCap(FieldInfo):
        field = dict(
            title="Funding Rate Cap",
            description="Maximum allowable funding rate"
        )

    class RateFloor(FieldInfo):
        field = dict(
            title="Funding Rate Floor",
            description="Minimum allowable funding rate"
        )

    class InterestRate(FieldInfo):
        field = dict(
            title="Interest Rate",
            description="Interest rate applied to the position"
        )

    class Interval(FieldInfo):
        field = dict(
            title="Funding Interval",
            description="Interval in seconds between funding payments"
        )

    class NextFundingTime(FieldInfo):
        field = dict(
            title="Next Funding Time",
            description="Timestamp in milliseconds for the next funding event"
        )

    class RemainingFundingTime(FieldInfo):
        field = dict(
            title="Time Remaining Until Next Funding",
            description="Time in seconds until the next funding event"
        )

    class PredictedFundingRate(FieldInfo):
        field = dict(
            title="Predicted Funding Rate",
            description="Predicted next funding rate"
        )


class Order:
    """
    Fields relating to core order information.
    """

    class ID(FieldInfo):
        field = dict(
            title="Order ID",
            description="Exchange assigned order ID"
        )

    class ClientID(FieldInfo):
        field = dict(
            title="Client ID",
            description="Client assigned order ID"
        )

    class Details(FieldInfo):
        field = dict(
            title="Order Details",
            description="Additional details about the order"
        )

    class Status(FieldInfo):
        field = dict(
            title="Order Status",
            description="Current order status"
        )
        options = [
            "Created",  # Order acked from order request, a transient state
            "Init",  # Same as Created, order acked from order request, a transient state
            "Untriggered",  # Conditional order waiting to be triggered
            "Triggered",  # Conditional order being triggered
            "Deactivated",  # Untriggered conditional order being removed
            "Rejected",  # Order rejected
            "New",  # Order placed into orderbook
            "PartiallyFilled",  # Order partially filled
            "Filled",  # Order fully filled
            "Canceled"  # Order canceled
        ]

    class OrderType(FieldInfo):
        field = dict(
            title="Order Type",
            description="Order type, e.g. Limit, Market, Stop."
        )
        options = [
            "Limit",
            "LimitIfTouched",
            "Market",
            "MarketAsLimit",
            "MarketIfTouched",
            "MarketIfTouchedAsLimit",
            "Stop",
            "StopAsLimit",
            "StopLimit",
            "ProtectedMarket",
            "Bracket",
            "BoTpLimit",
            "BoSlLimit",
            "BoSlMarket"
        ]

    class TradeType(FieldInfo):
        field = dict(
            title="Trade Type",
            description="Type of trade execution"
        )

    class Side(FieldInfo):
        field = dict(
            title="Side",
            description="Direction of the order i.e. Buy or Sell"
        )
        options = ["Buy", "Sell"]

    class Quantity(FieldInfo):
        field = dict(
            title="Quantity",
            description="Order quantity in contracts"
        )

    class Price(FieldInfo):
        field = dict(
            title="Price",
            description="Order price for conditional orders"
        )


class OrderCode:
    """
    Phemex expresses some of the other order fields as numeric codes, which are all defined together below.
    """

    class Side(FieldInfo):
        """
        Buy(1), Sell(2)
        """
        field = dict(
            title="Order Side Code",
            description="Numeric code representing the side of the order"
        )

    class PositionSide(FieldInfo):
        """
        Merged(0), Long(1), Short(2)
        """
        field = dict(
            title="Position Side Code",
            description="Numeric code representing the position side in hedge mode"
        )

    class Status(FieldInfo):
        """
        Created(0),Untriggered(1),Deactivated(2),Triggered(3),Rejected(4),New(5),PartiallyFilled(6),Filled(7),Canceled(8)
        """
        field = dict(
            title="Order Status Code",
            description="Numeric code representing the current order status"
        )

    class OrderType(FieldInfo):
        """
        Market (1), Limit (2), Stop (3), StopLimit (4), MarketIfTouched (5),
        LimitIfTouched (6), ProtectedMarket (7), MarketAsLimit (8), StopAsLimit (9),
        MarketIfTouchedAsLimit (10), Bracket (11), BoTpLimit (12), BoSlLimit (13),
        BoSlMarket (14)
        """
        field = dict(
            title="Order Type Code",
            description="Numeric code representing the order type"
        )

    class TradeType(FieldInfo):
        """
        Trade(1), Funding(4), LiqTrade(6), AdlTrade(7)
        """
        field = dict(
            title="Trade Type",
            description="Type of trade execution"
        )

    class StopDirection(FieldInfo):
        """
        Rising (1), Falling (2)
        """
        field = dict(
            title="Stop Direction Code",
            description="Numeric code representing the direction of the stop order"
        )

    class TriggerType(FieldInfo):
        """
        UNSPECIFIED(0), ByMarkPrice(1), ByLastPrice(3)
        """
        field = dict(
            title="Trigger Type Code",
            description="Numeric code representing the trigger type for conditional orders"
        )

    class PegType(FieldInfo):
        """
        UNSPECIFIED(0), LastPeg(1), MidPricePeg(2), MarketPeg(3),
        PrimaryPeg(4), TrailingStopPeg(5), TrailingTakeProfitPeg(6)
        """
        field = dict(
            title="Peg Price Type Code",
            description="Numeric code representing the type of pegged order"
        )

    class ExecutionStatus(FieldInfo):
        """
        Aborted(2), MakerFill(6), TakerFill(7), Expired(8), Canceled(11), CreateRejected(19)
        """
        field = dict(
            title="Execution Status Code",
            description="Numeric code representing the execution status of the order"
        )

    class ExecutionType(FieldInfo):
        """
        Trade(1),LiqTrade(6),AdlTrade(7)
        """
        field = dict(
            title="Execution Type Code",
            description="Numeric code representing the type of execution"
        )


class OrderCondition:
    """
    Extended set of order fields as they relate to conditionals in requests and responses.
    """

    class TriggerType(FieldInfo):
        field = dict(
            title="Trigger Type",
            description="Trigger for conditional orders"
        )

    class STPInstruction(FieldInfo):
        field = dict(
            title="STP Instruction",
            description="Self-trade prevention (STP) instruction"
        )
        options = ["None", "CancelMaker", "CancelTaker", "CancelBoth"]

    class ReduceOnly(FieldInfo):
        field = dict(
            title="Reduce Only",
            description="Whether the order should only reduce an existing position"
        )

    class TimeInForce(FieldInfo):
        field = dict(
            title="Time In Force",
            description="How long the order remains active before it is executed or expires"
        )
        options = ["GoodTillCancel", "ImmediateOrCancel", "FillOrKill", "PostOnly"]

    class CloseOnTrigger(FieldInfo):
        field = dict(
            title="Close on Trigger",
            description="If true, closes position when trigger condition is met."
        )

    class StopDirection(FieldInfo):
        field = dict(
            title="Stop Direction",
            description="Direction of the stop order"
        )
        options = ["Rising", "Falling"]

    class StopPrice(FieldInfo):
        field = dict(
            title="Stop Price",
            description="Stop order trigger price"
        )

    class StopLossPrice(FieldInfo):
        field = dict(
            title="Stop Loss Price",
            description="Stop loss trigger price"
        )
        scale = PhemexScale.price()

    class StopLossTrigger(FieldInfo):
        field = dict(
            title="Stop Loss Trigger Type",
            description="Trigger for stop loss orders."
        )
        options = [
            "ByMarkPrice",
            "ByIndexPrice",
            "ByLastPrice",
            "ByAskPrice",
            "ByBidPrice",
            "ByMarkPriceLimit",
            "ByLastPriceLimit"
        ]

    class TakeProfitPrice(FieldInfo):
        field = dict(
            title="Take Profit Price",
            description="Take profit trigger price"
        )
        scale = PhemexScale.price()

    class TakeProfitTrigger(FieldInfo):
        field = dict(
            title="Take Profit Trigger Type",
            description="Trigger for take profit orders."
        )
        options = [
            "ByMarkPrice",
            "ByIndexPrice",
            "ByLastPrice",
            "ByAskPrice",
            "ByBidPrice",
            "ByMarkPriceLimit",
            "ByLastPriceLimit"
        ]

    class PegOffsetProportion(FieldInfo):
        field = dict(
            title="Peg Price",
            description="Calculated peg price for pegged orders"
        )

    class PegOffsetValue(FieldInfo):
        field = dict(
            title="Peg Offset Value",
            description="Offset from reference price for pegged orders"
        )

    class PegPrice(FieldInfo):
        field = dict(
            title="Peg Price",
            description="Calculated peg price for pegged orders"
        )

    class PegType(FieldInfo):
        field = dict(
            title="Peg Price Type",
            description="Type of pegged order"
        )
        options = [
            "LastPeg",
            "MidPricePeg",
            "MarketPeg",
            "PrimaryPeg",
            "TrailingStopPeg",
            "TrailingTakeProfitPeg"
        ]


class OrderExecution:
    """
    Order fields relating to executions and fills, typically explicitly marked
    by the Phemex API with "exec"
    """

    class ID(FieldInfo):
        field = dict(
            title="Execution ID",
            description="Unique identifier for the execution"
        )

    class Status(FieldInfo):
        field = dict(
            title="Execution Status",
            description="Execution status of the order"
        )
        options = [
            "Init",
            "New",
            "Aborted",
            "MakerFill",
            "TakerFill",
            "Expired",
            "PendingNew",
            "PendingCancel",
            "PendingReplace",
            "Canceled",
            "CreateRejected"
        ]

    class Instructions(FieldInfo):
        field = dict(
            title="Execution Instructions",
            description="Special execution instructions. Used for special order types"
        )
        options = ["ReduceOnly", "CloseOnTrigger"]

    class Quantity(FieldInfo):
        field = dict(
            title="Execution Quantity",
            description="Quantity executed in this fill"
        )

    class Price(FieldInfo):
        field = dict(
            title="Execution Price",
            description="Price at which the execution occurred"
        )

    class Value(FieldInfo):
        field = dict(
            title="Execution Value",
            description="Nominal value of the execution"
        )

    class Fee(FieldInfo):
        field = dict(
            title="Execution Fee",
            description="Fee charged for this execution"
        )


class OrderQuantity:
    """
    Orders have many different representations of quantity, defined below.
    """

    class Display(FieldInfo):
        field = dict(
            title="Display Quantity",
            description="Display Quantity for iceberg orders visible to the book"
        )

    class Cumulative(FieldInfo):
        field = dict(
            title="Cumulative Quantity",
            description="Quantity of the order that has been filled"
        )

    class Leaves(FieldInfo):
        field = dict(
            title="Leaves Quantity",
            description="Remaining quantity of the order that is yet to be filled"
        )

    class BuyLeaves(FieldInfo):
        field = dict(
            title="Buy Leaves Quantity",
            description="Remaining buy quantity of the order that is yet to be filled"
        )

    class SellLeaves(FieldInfo):
        field = dict(
            title="Sell Leaves Quantity",
            description="Remaining quantity of the sell order that is yet to be filled"
        )


class OrderValue:
    """
    Orders have many different representations of value, defined below.
    """

    class AverageTransactionPrice(FieldInfo):
        field = dict(
            title="Average Transaction Price",
            description="Average price of all fills for the order"
        )

    class Nominal(FieldInfo):
        field = dict(
            title="Order Value",
            description="Nominal value of the order"
        )

    class Cumulative(FieldInfo):
        field = dict(
            title="Cumulative Value",
            description="Cumulative nominal value of the filled portion of the order"
        )

    class Leaves(FieldInfo):
        field = dict(
            title="Leaves Value",
            description="Remaining nominal value of the order that is yet to be filled"
        )

    class BuyLeaves(FieldInfo):
        field = dict(
            title="Buy Leaves Value",
            description="Remaining buy nominal value of the order that is yet to be filled"
        )

    class SellLeaves(FieldInfo):
        field = dict(
            title="Sell Leaves Value",
            description="Remaining nominal value of the sell order that is yet to be filled"
        )


class OrderBook:
    """
    Fields relating to orderbook information.
    """

    class Depth(FieldInfo):
        field = dict(
            title="Orderbook Depth",
            description="Depth of the orderbook data"
        )

    class Kind(FieldInfo):
        field = dict(
            title="Orderbook Type",
            description="Type of the orderbook data"
        )

    class Sequence(FieldInfo):
        field = dict(
            title="Orderbook Sequence",
            description="Sequence number of the orderbook update"
        )


class PNL:
    """
    Fields relating to profit and loss (PnL) information.
    """

    class Closed(FieldInfo):
        field = dict(
            title="Closed PnL",
            description="Realized PnL for closed portion of the order"
        )

    class CumulativeClosed(FieldInfo):
        field = dict(
            title="Cumulative Closed PnL",
            description="Cumulative closed profit and loss"
        )

    class Realized(FieldInfo):
        field = dict(
            title="Realized PnL",
            description="Realized profit and loss"
        )
        scale = PhemexScale.value()

    class CumulativeRealized(FieldInfo):
        field = dict(
            title="Cumulative Realized PnL",
            description="Cumulative realized profit and loss"
        )
        scale = PhemexScale.value()

    class CurrentRealized(FieldInfo):
        field = dict(
            title="Current Term Realized PnL",
            description="Realized profit and loss for the current term"
        )

    class Total(FieldInfo):
        field = dict(
            title="Total PnL",
            description="Total profit and loss including realized and unrealized amounts."
        )

    class PositionTotal(FieldInfo):
        field = dict(
            title="Total Unrealized PnL",
            description="Total unrealized profit and loss across all open positions."
        )

    class Unrealized(FieldInfo):
        field = dict(
            title="Unrealized PnL",
            description="Unrealized profit and loss"
        )


class Position:
    """
    Fields relating to position information.
    """

    class Mode(FieldInfo):
        field = dict(
            title="Position Mode",
            description="Position mode: One-way or Hedged"
        )
        options = ["OneWay", "Hedged"]

    class Side(FieldInfo):
        field = dict(
            title="Position Side",
            description="Position side in hedge mode: Long or Short."
        )
        options = ["Merged", "Long", "Short"]

    class Size(FieldInfo):
        field = dict(
            title="Size",
            description="Position size in contracts"
        )

    class ClosedSize(FieldInfo):
        field = dict(
            title="Closed Size",
            description="Quantity of the order that has been closed"
        )

    class OpenTime(FieldInfo):
        field = dict(
            title="Open Time NS",
            description="Timestamp in which the position was opened on the exchange in nanoseconds"
        )

    class Status(FieldInfo):
        field = dict(
            title="Position Status",
            description="Current status of the position"
        )

    class ExecutionSequence(FieldInfo):
        field = dict(
            title="Execution Sequence",
            description="Execution sequence number"
        )

    class FinishedFlag(FieldInfo):
        field = dict(
            title="Finished",
            description="Indicates if the order is finished (completely filled or canceled)"
        )

    class ROI(FieldInfo):
        field = dict(
            title="Return on Investment (ROI)",
            description="Return on investment ratio"
        )


class PositionBalance:
    """
    Position balance fields.
    """

    class Equity(FieldInfo):
        field = dict(
            title="Total Equity",
            description="Total equity including unrealized profit and loss."
        )

    class Used(FieldInfo):
        field = dict(
            title="Used Balance",
            description="Balance used for this position"
        )

    class Assigned(FieldInfo):
        field = dict(
            title="Assigned Balance",
            description="Assigned position balance"
        )

    class Current(FieldInfo):
        field = dict(
            title="Position Balance",
            description="Current balance of the position"
        )

    class Estimated(FieldInfo):
        field = dict(
            title="Estimated Available Balance",
            description="Estimated available balance for trading after accounting for margin and open orders."
        )

    class Fixed(FieldInfo):
        field = dict(
            title="Fixed Used Balance",
            description="Fixed portion of the balance currently allocated to margin or reserved usage."
        )

    class Locked(FieldInfo):
        field = dict(
            title="Total Order Used Balance",
            description="Total balance currently locked by open orders."
        )

    class Free(FieldInfo):
        field = dict(
            title="Total Free Balance",
            description="Total free balance available for trading."
        )


class PositionCost:
    """
    TBD
    """

    class TotalPositionCost(FieldInfo):
        field = dict(
            title="Total Position Cost",
            description="Total cost basis of all open positions."
        )

    class BuySideCost(FieldInfo):
        field = dict(
            title="Buy to Cost Ratio",
            description="Buy-side value-to-cost ratio"
        )

    class SellSideCost(FieldInfo):
        field = dict(
            title="Sell to Cost Ratio",
            description="Sell-side value-to-cost ratio"
        )

    class CostBasis(FieldInfo):
        field = dict(
            title="Cost Basis",
            description="Cost basis of the position"
        )


class PositionFee:
    """
    TBD
    """

    class CumulativeFunding(FieldInfo):
        field = dict(
            title="Cumulative Funding Fee",
            description="Cumulative funding fees paid"
        )

    class CumulativeTransaction(FieldInfo):
        field = dict(
            title="Cumulative Transaction Fee",
            description="Cumulative transaction fees paid"
        )

    class Current(FieldInfo):
        field = dict(
            title="Position Fee",
            description="Fee associated with the position"
        )

    class Exchange(FieldInfo):
        field = dict(
            title="Exchange Fee",
            description="Fee charged by the exchange for this execution"
        )
        scale = PhemexScale.ratio()

    class Maker(FieldInfo):
        field = dict(
            title="Maker Fee",
            description="Maker fee rate for the contract"
        )

    class Taker(FieldInfo):
        field = dict(
            title="Taker Fee",
            description="Taker fee rate for the contract"
        )


class PositionLeverage:
    """
    Options relating to position information.
    """

    class Leverage(FieldInfo):
        field = dict(
            title="One-Way Leverage",
            description="Leverage ratio applied to this position (OneWay mode only)"
        )

    class LongLeverage(FieldInfo):
        field = dict(
            title="Long Leverage",
            description="Leverage ratio for long positions (Hedged mode only)"
        )

    class ShortLeverage(FieldInfo):
        field = dict(
            title="Short Leverage",
            description="Leverage ratio for short positions (Hedged mode only)"
        )

    class Ratio(FieldInfo):
        field = dict(
            title="Leverage Ratio",
            description="Leverage ratio applied to this position"
        )

    class Current(FieldInfo):
        field = dict(
            title="Position Leverage",
            description="Leverage ratio applied to this position"
        )


class PositionLoss:
    """
    PositionReturn fields.
    """

    class Estimated(FieldInfo):
        field = dict(
            title="Estimated Order Loss",
            description="Estimated order loss"
        )

    class Open(FieldInfo):
        field = dict(
            title="Total Order Open Loss",
            description="Total unrealized loss from open orders."
        )

    class Unrealized(FieldInfo):
        field = dict(
            title="Unrealized Position Loss",
            description="Unrealized position loss (scaled)"
        )
        scale = PhemexScale.value()


class PositionMargin:
    """
    PositionMargin fields.
    """

    class Allocated(FieldInfo):
        field = dict(
            title="Margin",
            description="Margin allocated to this position"
        )

    class Ratio(FieldInfo):
        field = dict(
            title="Margin Ratio",
            description="Current margin ratio representing used margin versus total equity."
        )

    class Cross(FieldInfo):
        field = dict(
            title="Cross Margin",
            description="Cross margin mode status"
        )


class PositionPrice:
    """
    TBD
    """

    class Current(FieldInfo):
        field = dict(
            title="Position Price",
            description="Average entry price for the position"
        )

    class Entry(FieldInfo):
        field = dict(
            title="Avg Entry Price",
            description="Average entry price for the position"
        )

    class Open(FieldInfo):
        field = dict(
            title="Open Price",
            description="Opening price for the trade"
        )

    class Bankrupt(FieldInfo):
        field = dict(
            title="Bankrupt Price",
            description="Estimated bankruptcy price"
        )

    class Liquidation(FieldInfo):
        field = dict(
            title="Liquidation Price",
            description="Estimated liquidation price"
        )


class PositionRisk:
    """
    PositionRisk fields.
    """

    class TotalPositionMM(FieldInfo):
        field = dict(
            title="Total Maintenance Margin",
            description="Total maintenance margin required for all open positions."
        )

    class RiskLimit(FieldInfo):
        field = dict(
            title="Risk Limit",
            description="Risk limit for this position"
        )

    class RiskMode(FieldInfo):
        field = dict(
            title="Risk Mode",
            description="Account risk management mode (e.g., CrossAsset or Isolated)."
        )

    class DeleveragePercentile(FieldInfo):
        field = dict(
            title="Deleverage Percentile",
            description="ADL (auto-deleveraging) priority percentile"
        )

    class BankruptCommission(FieldInfo):
        field = dict(
            title="Bankrupt Commission",
            description="Commission lost at bankruptcy"
        )


class PositionTerm:
    """
    TBD
    """

    class LastFundingTime(FieldInfo):
        field = dict(
            title="Last Funding Time",
            description="Last funding timestamp (nanoseconds)"
        )

    class LastTermEndTime(FieldInfo):
        field = dict(
            title="Last Term End Time",
            description="End time of the last settlement term (nanoseconds)"
        )

    class Index(FieldInfo):
        field = dict(
            title="Settlement Term Index",
            description="Current settlement term index"
        )


class PositionValue:
    """
    TBD
    """

    class Nominal(FieldInfo):
        field = dict(
            title="Value",
            description="Nominal value of the position"
        )

    class Mark(FieldInfo):
        field = dict(
            title="Mark Value",
            description="Mark value (scaled)"
        )
        scale = PhemexScale.value()

    class CumulativeEntry(FieldInfo):
        field = dict(
            title="Cumulative Entry Value",
            description="Cumulative entry value of the position"
        )


class Price:
    """
    Fields relating to price information strictly as it relates to market data.
    """

    class Ask(FieldInfo):
        field = dict(
            title="Ask Price",
            description="Current best ask price."
        )

    class Bid(FieldInfo):
        field = dict(
            title="Bid Price",
            description="Current best bid price"
        )

    class Close(FieldInfo):
        field = dict(
            title="Close Price",
            description="Average price for the closed portion of the order"
        )

    class High(FieldInfo):
        field = dict(
            title="High Price",
            description="High price in the last 24h."
        )

    class Index(FieldInfo):
        field = dict(
            title="Index Price",
            description="Underlying index price"
        )

    class Last(FieldInfo):
        field = dict(
            title="Last Price",
            description="Last traded price"
        )

    class Low(FieldInfo):
        field = dict(
            title="Low Price",
            description="Low price in the last 24h"
        )

    class Mark(FieldInfo):
        field = dict(
            title="Mark Price",
            description="Mark price"
        )

    class Open(FieldInfo):
        field = dict(
            title="Open Price",
            description="Opening price in the last 24h"
        )

    class OpenInterest(FieldInfo):
        field = dict(
            title="Open Interest",
            description="Open interest"
        )

    class Turnover(FieldInfo):
        field = dict(
            title="Turnover",
            description="24h notional turnover"
        )

    class Volume(FieldInfo):
        field = dict(
            title="Volume",
            description="24h trading volume in contracts"
        )


class Product:
    """
    Fields relating to product information.
    """

    class ProductType(FieldInfo):
        field = dict(
            title="Product Type",
            description="Type of product (e.g., Perpetual, Futures)"
        )

    class ProductSubType(FieldInfo):
        field = dict(
            title="Perpetual Product Subtype",
            description="Subtype of the perpetual contract (e.g., Normal, Linear, Inverse)"
        )

    class Code(FieldInfo):
        field = dict(
            title="Product Code",
            description="Internal numeric code identifying the product"
        )

    class Name(FieldInfo):
        field = dict(
            title="Product Name",
            description="Full name of the product/currency (e.g., Bitcoin)"
        )

    class Description(FieldInfo):
        field = dict(
            title="Instrument Description",
            description="Detailed description of the contract, including funding and settlement rules"
        )

    class Status(FieldInfo):
        field = dict(
            title="Listing Status",
            description="Listing status of the currency (e.g., Listed, Delisted)"
        )

    class ListTime(FieldInfo):
        field = dict(
            title="Listing Time",
            description="Timestamp (ms) when the contract was listed on the exchange"
        )

    class AssetsDisplay(FieldInfo):
        field = dict(
            title="In Assets Display",
            description="Flag indicating whether this currency is displayed in the assets list (1 = visible)"
        )

    class NeedAddressTag(FieldInfo):
        field = dict(
            title="Need Address Tag",
            description="Flag indicating whether this currency requires an address tag or memo when depositing or withdrawing"
        )

    class MaxOI(FieldInfo):
        field = dict(
            title="Maximum Open Interest",
            description="Maximum allowable open interest for this contract (-1 = unlimited)"
        )

    class PilotTrading(FieldInfo):
        field = dict(
            title="Is Pilot Trading",
            description="Flag indicating whether the product is in pilot trading mode (1 = yes, 0 = no)"
        )

    class Checksum(FieldInfo):
        field = dict(
            title="Checksum",
            description="Checksum value for data integrity verification"
        )


class ProductLimit:
    """
    TBD
    """

    class MinValue(FieldInfo):
        field = dict(
            title="Minimum Value",
            description="Minimum allowable value for transfers or balances, expressed in exchange value units"
        )
        scale = PhemexScale.value()

    class MaxValue(FieldInfo):
        field = dict(
            title="Maximum Value",
            description="Maximum allowable value for transfers or balances, expressed in exchange value units"
        )

    class MinPrice(FieldInfo):
        field = dict(
            title="Minimum Price",
            description="Minimum allowed price for orders, expressed in quote price units"
        )
        scale = PhemexScale.price()

    class MaxPrice(FieldInfo):
        field = dict(
            title="Maximum Price",
            description="Maximum allowed price for orders, expressed in quote price units"
        )
        scale = PhemexScale.price()

    class ContractSize(FieldInfo):
        field = dict(
            title="Contract Size",
            description="Nominal value of one contract in quote currency units"
        )

    class LotSize(FieldInfo):
        field = dict(
            title="Lot Size",
            description="Minimum tradable quantity increment for orders"
        )

    class QuantityStepSize(FieldInfo):
        field = dict(
            title="Quantity Step Size",
            description="Minimum increment for order quantities"
        )

    class MinOrderValue(FieldInfo):
        field = dict(
            title="Minimum Order Value",
            description="Minimum order value in real terms"
        )
        scale = PhemexScale.value()

    class MaxOrderValue(FieldInfo):
        field = dict(
            title="Maximum Order Value",
            description="Maximum order value for the product"
        )
        scale = PhemexScale.value()

    class MaxOrderQuantity(FieldInfo):
        field = dict(
            title="Maximum Order Quantity",
            description="Maximum order quantity allowed, expressed in requested quantity units"
        )

    class MaxBaseOrderSize(FieldInfo):
        field = dict(
            title="Maximum Base Order Size",
            description="Maximum order size in base currency units (scaled)"
        )
        scale = PhemexScale.value()

    class TipOrderQuantity(FieldInfo):
        field = dict(
            title="Tip Order Quantity",
            description="Recommended tip quantity size in requested quantity units"
        )

    class BuyUpperLimit(FieldInfo):
        field = dict(
            title="Buy Price Upper Limit Percent",
            description="Maximum allowable buy price as a percentage above the reference price"
        )

    class SellLowerLimit(FieldInfo):
        field = dict(
            title="Sell Lower Limit Percentage",
            description="Percentage below the reference price that defines the lower limit for sell orders"
        )

    class DefaultMakerFee(FieldInfo):
        field = dict(
            title="Default Maker Fee",
            description="Default maker fee rate"
        )
        scale = PhemexScale.ratio()

    class DefaultTakerFee(FieldInfo):
        field = dict(
            title="Default Taker Fee",
            description="Default taker fee rate"
        )
        scale = PhemexScale.ratio()


class ProductPrecision:
    """
    TBD
    """

    class Asset(FieldInfo):
        field = dict(
            title="Assets Precision",
            description="Number of decimal places supported for this asset's display and calculation precision"
        )

    class Price(FieldInfo):
        field = dict(
            title="Price Precision",
            description="Number of decimal places shown for displayed price values"
        )

    class Quantity(FieldInfo):
        field = dict(
            title="Quantity Precision",
            description="Number of decimal places supported for quantity values"
        )

    class BaseQuantity(FieldInfo):
        field = dict(
            title="Base Quantity Precision",
            description="Number of decimal places supported for quantity values"
        )

    class QuoteQuantity(FieldInfo):
        field = dict(
            title="Quote Quantity Precision",
            description="Number of decimal places supported for quantity values"
        )


class ProductRisk:
    """
    Fields relating to product risk information.
    """

    class IndexID(FieldInfo):
        field = dict(
            title="Index ID",
            description="Identifier for the leverage margin group"
        )

    class NotionalValue(FieldInfo):
        field = dict(
            title="Notional Value",
            description="Notional value of the position"
        )

    class RiskSteps(FieldInfo):
        field = dict(
            title="Risk Steps",
            description="Array of risk limit steps in exchange value units"
        )

    class MaxRiskLimit(FieldInfo):
        field = dict(
            title="Maximum Risk Limit",
            description="Maximum risk limit tier for the product"
        )

    class InitialMargin(FieldInfo):
        field = dict(
            title="Initial Margin Ratio",
            description="Initial margin requirement ratio"
        )
        scale = PhemexScale.ratio()

    class MaintenanceMargin(FieldInfo):
        field = dict(
            title="Maintenance Margin Ratio",
            description="Maintenance margin requirement ratio for this position"
        )
        scale = PhemexScale.ratio()

    class MaintenanceAmount(FieldInfo):
        field = dict(
            title="Maintenance Amount",
            description="Maintenance amount required for the position"
        )


class ProductLeverage:
    """
    TBD
    """

    class Default(FieldInfo):
        field = dict(
            title="Default Leverage",
            description="Default leverage value applied when opening new positions"
        )

    class Max(FieldInfo):
        field = dict(
            title="Maximum Leverage",
            description="Maximum leverage allowed for the contract"
        )

    class MaxMargin(FieldInfo):
        field = dict(
            title="Leverage Margin",
            description="Margin requirement factor associated with maximum leverage"
        )

    class MaxOpen(FieldInfo):
        field = dict(
            title="Maximum Open Position Leverage",
            description="Maximum leverage allowed for open positions on this instrument"
        )

    class Options(FieldInfo):
        field = dict(
            title="Leverage Options",
            description="List of available leverage options for the contract"
        )


class ProductScale:
    """
    TBD
    """

    class Price(FieldInfo):
        field = dict(
            title="Price Scale",
            description="Scaling factor for converting between display and exchange price units"
        )

    class Ratio(FieldInfo):
        field = dict(
            title="Ratio Scale",
            description="Scaling factor for ratio-based quantities such as funding rates"
        )

    class Value(FieldInfo):
        field = dict(
            title="Value Scale",
            description="Number of decimal places used for the currency's value scale on the exchange"
        )


class ProductTick:
    """
    TBD
    """

    class Size(FieldInfo):
        field = dict(
            title="Tick Size",
            description="Minimum price increment allowed between order prices"
        )

    class BaseSize(FieldInfo):
        field = dict(
            title="Base Tick Size",
            description="Standard price increment for orders in raw format (scaled by 1e8)"
        )
        scale = PhemexScale.value()

    class QuoteSize(FieldInfo):
        field = dict(
            title="Quote Tick Size",
            description="Standard price increment for orders in raw format (scaled by 1e8)"
        )
        scale = PhemexScale.value()


class Request:
    """
    Fields relating to request information.
    """

    class StartTime(FieldInfo):
        field = dict(
            title="Start Time",
            description="Timestamp (ms) when the contract becomes active"
        )

    class EndTime(FieldInfo):
        field = dict(
            title="End Time",
            description="End timestamp (ms) for the contract's validity period"
        )

    class Limit(FieldInfo):
        field = dict(
            title="Result Limit",
            description="Maximum number of results to return"
        )

    class Order(FieldInfo):
        field = dict(
            title="Order By",
            description="Order direction, e.g., Asc or Desc"
        )
        options = ["asc", "desc"]

    class OrderBy(FieldInfo):
        field = dict(
            title="Order By Column",
            description="Column to order the results by"
        )

    class Offset(FieldInfo):
        field = dict(
            title="Result Offset",
            description="Offset for paginated results"
        )

    class PageNumber(FieldInfo):
        field = dict(
            title="Page Number",
            description="Page number for paginated results"
        )

    class PageSize(FieldInfo):
        field = dict(
            title="Page Size",
            description="Number of items per page for paginated results"
        )

    class IncludeCount(FieldInfo):
        field = dict(
            title="Result Count",
            description="Whether to include the total count of results in the response"
        )

    class Untriggered(FieldInfo):
        field = dict(
            title="Untriggered Only",
            description="Flag to filter and return only untriggered conditional orders"
        )

    class Resolution(FieldInfo):
        field = dict(
            title="Resolution",
            description="Time resolution for the data in seconds"
        )

    class Text(FieldInfo):
        field = dict(
            title="Optional Text",
            description="Optional annotation or free text for the order."
        )


class Symbol(FieldInfo):
    """
    Fields relating to trading symbol information.
    For standard symbol, use this class directly as Symbol.
    """
    field = dict(
        title="Symbol",
        description="Trading symbol, e.g. BTCUSDT"
    )

    class Display(FieldInfo):
        field = dict(
            title="Display Symbol",
            description="Display-friendly representation of the trading pair (e.g., BTC / USD)"
        )

    class FundingRate(FieldInfo):
        field = dict(
            title="Funding Rate Symbol",
            description="Symbol for the funding rate index"
        )

    class FundingRateShort(FieldInfo):
        field = dict(
            title="Funding Rate 8h Symbol",
            description="Symbol for the 8-hour funding rate index"
        )

    class Index(FieldInfo):
        field = dict(
            title="Index Symbol",
            description="Symbol representing the index price source for the contract"
        )

    class Major(FieldInfo):
        field = dict(
            title="Major Symbol",
            description="Boolean flag indicating if this is a major trading pair"
        )

    class Mark(FieldInfo):
        field = dict(
            title="Mark Symbol",
            description="Symbol representing the mark price index"
        )

    class Underlying(FieldInfo):
        field = dict(
            title="Contract Underlying Assets",
            description="Underlying assets of the contract (e.g., USD for BTCUSD)"
        )


class Time:
    """
    Fields relating to time information.
    """

    # MILLISECONDS

    class Timestamp(FieldInfo):
        field = dict(
            title="Timestamp",
            description="Snapshot timestamp in milliseconds"
        )

    class CreatedAt(FieldInfo):
        field = dict(
            title="Created At Timestamp",
            description="Timestamp in which the order was created on the exchange in milliseconds"
        )

    class UpdatedAt(FieldInfo):
        field = dict(
            title="Updated At",
            description="Timestamp (ms) of the last update to the order or position"
        )

    class Data(FieldInfo):
        field = dict(
            title="Data Timestamp",
            description="Timestamp (ms) when the data was generated"
        )

    class Match(FieldInfo):
        field = dict(
            title="Match Timestamp",
            description="Timestamp for validating order book matching"
        )

    # NANOSECONDS

    class Action(FieldInfo):
        field = dict(
            title="Action Time",
            description="Timestamp in which the order was registered on the exchange in nanoseconds"
        )

    class Transaction(FieldInfo):
        field = dict(
            title="Transaction Time",
            description="Timestamp in which the order was fulfilled on the exchange in nanoseconds"
        )

    class LastUpdated(FieldInfo):
        field = dict(
            title="Updated Time NS",
            description="Timestamp in which the order was last updated on the exchange in nanoseconds"
        )



"""
Phemex business error codes returned in HTTP-200 responses (code != 0).

All ~150 documented error codes are mapped one-to-one to typed exception classes.
Use `raise_for_biz_error(data)` as the single entry-point.
"""
import logging

from .exceptions import PhemexError

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------


class PhemexBizError(PhemexError):
    """Base class for all HTTP-200 business errors from Phemex (code != 0)."""

    def __init__(self, code: int, msg: str, data: dict | None = None):
        self.code = code
        self.msg = msg
        self.data = data
        super().__init__(
            message=f"[{code}] {msg}",
            context={"code": code, "msg": msg, "data": data},
        )

    def __str__(self) -> str:
        parts = [f"{self.__class__.__name__}[{self.code}]: {self.msg}"]
        if self.data:
            parts.append(f"data={self.data}")
        return " | ".join(parts)


# ---------------------------------------------------------------------------
# Domain subclasses
# ---------------------------------------------------------------------------


class DuplicateRequestError(PhemexBizError):
    """Duplicate request ID (19999)."""


class DuplicateOrderError(PhemexBizError):
    """Duplicate order ID or clOrdId (10001, 11033, 11085)."""


class OrderNotFoundError(PhemexBizError):
    """Order not found (10002)."""


class OrderStateError(PhemexBizError):
    """Order state machine violations — cancel/replace rejected due to order state."""


class InsufficientBalanceError(PhemexBizError):
    """Insufficient available balance or margin for the requested operation."""


class LeverageRiskLimitError(PhemexBizError):
    """Invalid leverage value or risk limit exceeded."""


class PositionMarginError(PhemexBizError):
    """Margin add/remove on position rejected."""


class ReduceOnlyError(PhemexBizError):
    """Reduce-only order rejected."""


class InvalidOrderParamError(PhemexBizError):
    """Invalid order parameter (side, type, TIF, qty, price range, etc.)."""


class ConditionalOrderError(PhemexBizError):
    """Conditional/stop order creation or trigger errors."""


class TakeProfitStopLossError(PhemexBizError):
    """TP/SL attachment or duplicate TP/SL errors."""


class TrailingOrderError(PhemexBizError):
    """Trailing stop order errors."""


class BracketOrderError(PhemexBizError):
    """Bracket order errors."""


class AccountStatusError(PhemexBizError):
    """Account banned, in liquidation, or in ADL process."""


class RoutingError(PhemexBizError):
    """Request routed to wrong trading engine or account/symbol mismatch."""


class WalletError(PhemexBizError):
    """Wallet operation errors (find, action, balance, deposit, withdraw)."""


class FeeRangeError(PhemexBizError):
    """Fee value out of valid range."""


class MarketDataUnavailableError(PhemexBizError):
    """Mark, index, or last price unavailable for conditional order creation."""


class RpiError(PhemexBizError):
    """Market maker / open-interest restriction errors."""


# ---------------------------------------------------------------------------
# Full code → class mapping (~150 codes from Phemex docs)
# ---------------------------------------------------------------------------

_BIZ_ERROR_MAP: dict[int, type[PhemexBizError]] = {
    # --- Duplicate request ---
    19999: DuplicateRequestError,

    # --- Order management (OM) ---
    10001: DuplicateOrderError,       # OM_DUPLICATE_ORDERID
    10002: OrderNotFoundError,        # OM_ORDER_NOT_FOUND
    10003: OrderStateError,           # OM_ORDER_PENDING_CANCEL
    10004: OrderStateError,           # OM_ORDER_PENDING_REPLACE
    10005: OrderStateError,           # OM_ORDER_PENDING

    # --- Balance / margin ---
    11001: InsufficientBalanceError,  # TE_NO_ENOUGH_AVAILABLE_BALANCE
    11002: LeverageRiskLimitError,    # TE_INVALID_RISK_LIMIT
    11003: InsufficientBalanceError,  # TE_NO_ENOUGH_BALANCE_FOR_NEW_RISK_LIMIT
    11004: LeverageRiskLimitError,    # TE_INVALID_LEVERAGE
    11005: InsufficientBalanceError,  # TE_NO_ENOUGH_BALANCE_FOR_NEW_LEVERAGE

    # --- Position margin ---
    11006: PositionMarginError,       # TE_CANNOT_CHANGE_POSITION_MARGIN_WITHOUT_POSITION
    11007: PositionMarginError,       # TE_CANNOT_CHANGE_POSITION_MARGIN_FOR_CROSS_MARGIN
    11008: PositionMarginError,       # TE_CANNOT_REMOVE_POSITION_MARGIN_MORE_THAN_ADDED
    11009: PositionMarginError,       # TE_CANNOT_REMOVE_POSITION_MARGIN_DUE_TO_UNREALIZED_PNL

    # --- Balance (continued) ---
    11010: InsufficientBalanceError,  # TE_CANNOT_ADD_POSITION_MARGIN_DUE_TO_NO_ENOUGH_AVAILABLE_BALANCE

    # --- Reduce only ---
    11011: ReduceOnlyError,           # TE_REDUCE_ONLY_ABORT

    # --- Invalid param ---
    11012: InvalidOrderParamError,    # TE_REPLACE_TO_INVALID_QTY

    # --- Conditional orders ---
    11013: ConditionalOrderError,     # TE_CONDITIONAL_NO_POSITION
    11014: ConditionalOrderError,     # TE_CONDITIONAL_CLOSE_POSITION_WRONG_SIDE
    11015: ConditionalOrderError,     # TE_CONDITIONAL_TRIGGERED_OR_CANCELED

    # --- Routing ---
    11016: RoutingError,              # TE_ADL_NOT_TRADING_REQUESTED_ACCOUNT
    11017: RoutingError,              # TE_ADL_CANNOT_FIND_POSITION

    # --- Misc funding/bonus (no dedicated subclass) ---
    11018: PhemexBizError,            # TE_NO_NEED_TO_SETTLE_FUNDING
    11019: PhemexBizError,            # TE_FUNDING_ALREADY_SETTLED
    11020: PhemexBizError,            # TE_CANNOT_TRANSFER_OUT_DUE_TO_BONUS
    11021: PhemexBizError,            # TE_INVALID_BONOUS_AMOUNT

    # --- Account status ---
    11022: AccountStatusError,        # TE_REJECT_DUE_TO_BANNED
    11023: AccountStatusError,        # TE_REJECT_DUE_TO_IN_PROCESS_OF_LIQ
    11024: AccountStatusError,        # TE_REJECT_DUE_TO_IN_PROCESS_OF_ADL

    # --- Routing (continued) ---
    11025: RoutingError,              # TE_ROUTE_ERROR
    11026: RoutingError,              # TE_UID_ACCOUNT_MISMATCH

    # --- Invalid param (continued) ---
    11027: InvalidOrderParamError,    # TE_SYMBOL_INVALID
    11028: InvalidOrderParamError,    # TE_CURRENCY_INVALID
    11029: InvalidOrderParamError,    # TE_ACTION_INVALID
    11030: InvalidOrderParamError,    # TE_ACTION_BY_INVALID

    # --- Conditional orders (continued) ---
    11031: ConditionalOrderError,     # TE_SO_NUM_EXCEEDS

    # --- Invalid param (continued) ---
    11032: InvalidOrderParamError,    # TE_AO_NUM_EXCEEDS

    # --- Duplicate order (continued) ---
    11033: DuplicateOrderError,       # TE_ORDER_ID_DUPLICATE

    # --- Invalid param (continued) ---
    11034: InvalidOrderParamError,    # TE_SIDE_INVALID
    11035: InvalidOrderParamError,    # TE_ORD_TYPE_INVALID
    11036: InvalidOrderParamError,    # TE_TIME_IN_FORCE_INVALID
    11037: InvalidOrderParamError,    # TE_EXEC_INST_INVALID
    11038: InvalidOrderParamError,    # TE_TRIGGER_INVALID
    11039: InvalidOrderParamError,    # TE_STOP_DIRECTION_INVALID

    # --- Market data unavailable ---
    11040: MarketDataUnavailableError,  # TE_NO_MARK_PRICE
    11041: MarketDataUnavailableError,  # TE_NO_INDEX_PRICE
    11042: MarketDataUnavailableError,  # TE_NO_LAST_PRICE

    # --- Conditional orders (continued) ---
    11043: ConditionalOrderError,     # TE_RISING_TRIGGER_DIRECTLY
    11044: ConditionalOrderError,     # TE_FALLING_TRIGGER_DIRECTLY
    11045: ConditionalOrderError,     # TE_TRIGGER_PRICE_TOO_LARGE
    11046: ConditionalOrderError,     # TE_TRIGGER_PRICE_TOO_SMALL
    11047: ConditionalOrderError,     # TE_BUY_TP_SHOULD_GT_BASE
    11048: ConditionalOrderError,     # TE_BUY_SL_SHOULD_LT_BASE
    11049: ConditionalOrderError,     # TE_BUY_SL_SHOULD_GT_LIQ
    11050: ConditionalOrderError,     # TE_SELL_TP_SHOULD_LT_BASE
    11051: ConditionalOrderError,     # TE_SELL_SL_SHOULD_LT_LIQ
    11052: ConditionalOrderError,     # TE_SELL_SL_SHOULD_GT_BASE

    # --- Invalid param (continued) ---
    11053: InvalidOrderParamError,    # TE_PRICE_TOO_LARGE
    11054: InvalidOrderParamError,    # TE_PRICE_WORSE_THAN_BANKRUPT
    11055: InvalidOrderParamError,    # TE_PRICE_TOO_SMALL
    11056: InvalidOrderParamError,    # TE_QTY_TOO_LARGE

    # --- Reduce only (continued) ---
    11057: ReduceOnlyError,           # TE_QTY_NOT_MATCH_REDUCE_ONLY

    # --- Invalid param (continued) ---
    11058: InvalidOrderParamError,    # TE_QTY_TOO_SMALL

    # --- TP/SL ---
    11059: TakeProfitStopLossError,   # TE_TP_SL_QTY_NOT_MATCH_POS
    11060: TakeProfitStopLossError,   # TE_SIDE_NOT_CLOSE_POS

    # --- Order state (continued) ---
    11061: OrderStateError,           # TE_ORD_ALREADY_PENDING_CANCEL
    11062: OrderStateError,           # TE_ORD_ALREADY_CANCELED
    11063: OrderStateError,           # TE_ORD_STATUS_CANNOT_CANCEL
    11064: OrderStateError,           # TE_ORD_ALREADY_PENDING_REPLACE
    11065: OrderStateError,           # TE_ORD_REPLACE_NOT_MODIFIED
    11066: OrderStateError,           # TE_ORD_STATUS_CANNOT_REPLACE

    # --- Invalid param (continued) ---
    11067: InvalidOrderParamError,    # TE_CANNOT_REPLACE_PRICE
    11068: InvalidOrderParamError,    # TE_CANNOT_REPLACE_QTY

    # --- Routing (continued) ---
    11069: RoutingError,              # TE_ACCOUNT_NOT_IN_RANGE
    11070: RoutingError,              # TE_SYMBOL_NOT_IN_RANGE

    # --- Order state (continued) ---
    11071: OrderStateError,           # TE_ORD_STATUS_CANNOT_TRIGGER

    # --- Fee range ---
    11072: FeeRangeError,             # TE_TKFR_NOT_IN_RANGE
    11073: FeeRangeError,             # TE_MKFR_NOT_IN_RANGE

    # --- TP/SL (continued) ---
    11074: TakeProfitStopLossError,   # TE_CANNOT_ATTACH_TP_SL
    11075: TakeProfitStopLossError,   # TE_TP_TOO_LARGE
    11076: TakeProfitStopLossError,   # TE_TP_TOO_SMALL
    11077: TakeProfitStopLossError,   # TE_TP_TRIGGER_INVALID
    11078: TakeProfitStopLossError,   # TE_SL_TOO_LARGE
    11079: TakeProfitStopLossError,   # TE_SL_TOO_SMALL
    11080: TakeProfitStopLossError,   # TE_SL_TRIGGER_INVALID

    # --- Leverage / risk limit (continued) ---
    11081: LeverageRiskLimitError,    # TE_RISK_LIMIT_EXCEEDS

    # --- Balance (continued) ---
    11082: InsufficientBalanceError,  # TE_CANNOT_COVER_ESTIMATE_ORDER_LOSS

    # --- TP/SL (continued) ---
    11083: TakeProfitStopLossError,   # TE_TAKE_PROFIT_ORDER_DUPLICATED
    11084: TakeProfitStopLossError,   # TE_STOP_LOSS_ORDER_DUPLICATED

    # --- Duplicate order (continued) ---
    11085: DuplicateOrderError,       # TE_CL_ORD_ID_DUPLICATE

    # --- Trailing orders ---
    11086: TrailingOrderError,        # TE_PEG_PRICE_TYPE_INVALID
    11087: TrailingOrderError,        # TE_BUY_TS_SHOULD_LT_BASE
    11088: TrailingOrderError,        # TE_BUY_TS_SHOULD_GT_LIQ
    11089: TrailingOrderError,        # TE_SELL_TS_SHOULD_LT_LIQ
    11090: TrailingOrderError,        # TE_SELL_TS_SHOULD_GT_BASE
    11091: TrailingOrderError,        # TE_BUY_REVERT_VALUE_SHOULD_LT_ZERO
    11092: TrailingOrderError,        # TE_SELL_REVERT_VALUE_SHOULD_GT_ZERO
    11093: TrailingOrderError,        # TE_BUY_TTP_SHOULD_ACTIVATE_ABOVE_BASE
    11094: TrailingOrderError,        # TE_SELL_TTP_SHOULD_ACTIVATE_BELOW_BASE
    11095: TrailingOrderError,        # TE_TRAILING_ORDER_DUPLICATED

    # --- TP/SL (close order) ---
    11096: TakeProfitStopLossError,   # TE_CLOSE_ORDER_CANNOT_ATTACH_TP_SL

    # --- Wallet ---
    11097: WalletError,               # TE_CANNOT_FIND_WALLET_OF_THIS_CURRENCY
    11098: WalletError,               # TE_WALLET_INVALID_ACTION
    11099: WalletError,               # TE_WALLET_VID_UNMATCHED
    11100: WalletError,               # TE_WALLET_INSUFFICIENT_BALANCE
    11101: WalletError,               # TE_WALLET_INSUFFICIENT_LOCKED_BALANCE
    11102: WalletError,               # TE_WALLET_INVALID_DEPOSIT_AMOUNT
    11103: WalletError,               # TE_WALLET_INVALID_WITHDRAW_AMOUNT
    11104: WalletError,               # TE_WALLET_REACHED_MAX_AMOUNT

    # --- Balance (place order) ---
    11105: InsufficientBalanceError,  # TE_PLACE_ORDER_INSUFFICIENT_BASE_BALANCE
    11106: InsufficientBalanceError,  # TE_PLACE_ORDER_INSUFFICIENT_QUOTE_BALANCE

    # --- Routing (continued) ---
    11107: RoutingError,              # TE_CANNOT_CONNECT_TO_REQUEST_SEQ

    # --- Invalid param (order type restrictions) ---
    11108: InvalidOrderParamError,    # TE_CANNOT_REPLACE_OR_CANCEL_MARKET_ORDER
    11109: InvalidOrderParamError,    # TE_CANNOT_REPLACE_OR_CANCEL_IOC_ORDER
    11110: InvalidOrderParamError,    # TE_CANNOT_REPLACE_OR_CANCEL_FOK_ORDER
    11111: InvalidOrderParamError,    # TE_MISSING_ORDER_ID
    11112: InvalidOrderParamError,    # TE_QTY_TYPE_INVALID
    11113: InvalidOrderParamError,    # TE_USER_ID_INVALID
    11114: InvalidOrderParamError,    # TE_ORDER_VALUE_TOO_LARGE
    11115: InvalidOrderParamError,    # TE_ORDER_VALUE_TOO_SMALL

    # --- Bracket orders ---
    11116: BracketOrderError,         # TE_BO_NUM_EXCEEDS
    11117: BracketOrderError,         # TE_BO_CANNOT_HAVE_BO_WITH_DIFF_SIDE
    11118: BracketOrderError,         # TE_BO_TP_PRICE_INVALID
    11119: BracketOrderError,         # TE_BO_SL_PRICE_INVALID
    11120: BracketOrderError,         # TE_BO_SL_TRIGGER_PRICE_INVALID
    11121: BracketOrderError,         # TE_BO_CANNOT_REPLACE
    11122: BracketOrderError,         # TE_BO_BOTP_STATUS_INVALID
    11123: BracketOrderError,         # TE_BO_CANNOT_PLACE_BOTP_OR_BOSL_ORDER
    11124: BracketOrderError,         # TE_BO_CANNOT_REPLACE_BOTP_OR_BOSL_ORDER
    11125: BracketOrderError,         # TE_BO_CANNOT_CANCEL_BOTP_OR_BOSL_ORDER
    11126: BracketOrderError,         # TE_BO_DONOT_SUPPORT_API
    11128: BracketOrderError,         # TE_BO_INVALID_EXECINST
    11129: BracketOrderError,         # TE_BO_MUST_BE_SAME_SIDE_AS_POS
    11130: BracketOrderError,         # TE_BO_WRONG_SL_TRIGGER_TYPE
    11131: BracketOrderError,         # TE_BO_WRONG_TP_TRIGGER_TYPE
    11132: BracketOrderError,         # TE_BO_ABORT_BOSL_DUE_BOTP_CREATE_FAILED
    11133: BracketOrderError,         # TE_BO_ABORT_BOSL_DUE_BOPO_CANCELED
    11134: BracketOrderError,         # TE_BO_ABORT_BOTP_DUE_BOPO_CANCELED

    # --- RPI / OI restrict ---
    11143: RpiError,                  # TE_RPI_NOT_APPROVED_MARKET_MAKER
    11150: RpiError,                  # TE_OI_LIMIT_REDUCE_ONLY
}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def raise_for_biz_error(data: dict) -> None:
    """Raise a typed PhemexBizError if the response envelope contains a non-zero code.

    No-ops for code == 0, missing code field, or non-dict input.
    Logs a structured WARNING before raising.
    """
    if not isinstance(data, dict) or "code" not in data:
        return
    code = data["code"]
    if code == 0:
        return
    msg = data.get("msg", "Unknown error")
    exc_cls = _BIZ_ERROR_MAP.get(code, PhemexBizError)
    _logger.warning(
        "Phemex business error [%d] %s (%s)", code, msg, exc_cls.__name__,
    )
    raise exc_cls(code=code, msg=msg, data=data.get("data"))

"""Integration tests for signed_size in OneWay (Merged) position mode.

Run with:
    uv run pytest tests/__integration__/usdm/test_merged_diagnostic.py -v -s

Requires PHEMEX_KEY and PHEMEX_SECRET env vars pointing at testnet.
"""
import time

import pytest

from phemex_py.biz_errors import PhemexBizError as PhemexAPIError
from phemex_py.usdm_rest.models import (
    PlaceOrderRequest,
    PositionResponse,
    PositionWithPnLResponse,
    SwitchModeRequest,
)

SYMBOL = "BTCUSDT"
_ACCEPTABLE = {11001, 11004, 11006, 11082, 20004, 21002}


class TestMergedModeSignedSize:
    """Verify signed_size returns correct sign for OneWay (Merged) positions on testnet."""

    def test_merged_short_signed_size_negative(self, client):
        """A short position in Merged mode must have negative signed_size."""
        # Cancel open orders so mode switch succeeds
        try:
            client.usdm_rest.cancel_all(symbol=SYMBOL)
        except PhemexAPIError:
            pass
        time.sleep(0.5)

        # Switch to OneWay
        try:
            client.usdm_rest.switch_position_mode(SwitchModeRequest.make(symbol=SYMBOL, mode="OneWay"))
        except PhemexAPIError as e:
            if e.code in _ACCEPTABLE:
                pytest.skip(f"Cannot switch to OneWay: [{e.code}] {e.msg}")
            raise
        time.sleep(0.5)

        try:
            # Place a small short market order
            order = PlaceOrderRequest(
                symbol=SYMBOL,
                side="Sell",
                pos_side="Merged",
                order_type="Market",
                quantity="0.01",
                time_in_force="ImmediateOrCancel",
            )
            try:
                client.usdm_rest.place_order(order)
            except PhemexAPIError as e:
                if e.code in _ACCEPTABLE:
                    pytest.skip(f"Cannot place short order: [{e.code}] {e.msg}")
                raise
            time.sleep(1)

            # Verify positions() signed_size
            pos_resp: PositionResponse = client.usdm_rest.positions()
            for pos in pos_resp.positions:
                if pos.symbol == SYMBOL and pos.pos_side == "Merged" and pos.side == "Sell":
                    assert pos.signed_size < 0, (
                        f"Expected negative signed_size for Merged short, got {pos.signed_size}"
                    )
                    break
            else:
                pytest.skip("No Merged short position found in positions()")

            # Verify positions_with_pnl() signed_size
            pnl_resp: PositionWithPnLResponse = client.usdm_rest.positions_with_pnl()
            for pos in pnl_resp.positions:
                if pos.symbol == SYMBOL and pos.pos_side == "Merged" and pos.side == "Sell":
                    assert pos.signed_size < 0, (
                        f"Expected negative signed_size for Merged short, got {pos.signed_size}"
                    )
                    break
            else:
                pytest.skip("No Merged short position found in positions_with_pnl()")

        finally:
            # Cleanup: close position, switch back
            try:
                close_order = PlaceOrderRequest(
                    symbol=SYMBOL,
                    side="Buy",
                    pos_side="Merged",
                    order_type="Market",
                    quantity="0.01",
                    time_in_force="ImmediateOrCancel",
                    reduce_only=True,
                )
                client.usdm_rest.place_order(close_order)
            except PhemexAPIError:
                pass
            time.sleep(0.5)

            try:
                client.usdm_rest.switch_position_mode(SwitchModeRequest.make(symbol=SYMBOL, mode="Hedged"))
            except PhemexAPIError:
                pass

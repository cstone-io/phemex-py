import pytest
from decimal import Decimal
from typing import Annotated

import phemex_py.core.models as core
from phemex_py.exceptions import ValidationError
from phemex_py.usdm_rest.models import PlaceOrderRequest


class TestPhemexDecimal:
    def test_phemex_decimal_validate_accepts_str_int_float_decimal(self):
        d1 = core.PhemexDecimal.validate("123")
        d2 = core.PhemexDecimal.validate(123)
        d3 = core.PhemexDecimal.validate(123.0)
        d4 = core.PhemexDecimal.validate(Decimal("123"))

        assert isinstance(d1, core.PhemexDecimal)
        assert isinstance(d2, core.PhemexDecimal)
        assert isinstance(d3, core.PhemexDecimal)
        assert isinstance(d4, core.PhemexDecimal)


class TestPhemexModel:
    def test_model_with_fixed_decimal_field(self):
        class Dummy(core.PhemexModel):
            value: core.PhemexDecimal

        m = Dummy.model_validate({"value": "12345"})
        assert isinstance(m.value, Decimal)
        assert m.value == Decimal("12345")

        dumped = m.model_dump()
        # no scaling metadata → should dump raw string
        assert dumped["value"] == "12345"

    def test_model_with_scaled_field(self, monkeypatch):
        monkeypatch.setitem(core.PhemexModel.__products__, "futures", {"BTCUSDT": {"priceScale": 2}})

        class Dummy(core.PhemexModel):
            symbol: str
            price: Annotated[core.PhemexDecimal, core.PhemexScale.price()]

        # API gives scaled string
        m = Dummy.model_validate({"symbol": "BTCUSDT", "price": "12345"})
        # should be descaled (divide by 10^2)
        assert m.price == Decimal("123.45")

        dumped = m.model_dump()
        # should rescale back to int-string
        assert dumped["price"] == "12345.00"

    def test_actual_model(self):
        # semi-integration test with actual model
        m = PlaceOrderRequest.builder("BTCUSDT").increase_long(1).limit(12345).build()
        assert m.price == Decimal("12345")

        dumped = m.model_dump(by_alias=False)
        assert dumped["price"] == "12345"

    def test_scaled_field_without_symbol_raises(self, monkeypatch):
        monkeypatch.setitem(core.PhemexModel.__products__, "futures", {"BTCUSDT": {"priceScale": 2}})

        class Dummy(core.PhemexModel):
            price: Annotated[core.PhemexDecimal, core.PhemexScale.price()]

        # Validation without symbol → raises
        with pytest.raises(ValidationError):
            Dummy.model_validate({"price": "12345"})

    def test_serializer_with_none_and_exclude_none(self):
        class Dummy(core.PhemexModel):
            symbol: str
            price: core.PhemexDecimal
            comment: str | None = None

        m = Dummy.model_validate({"symbol": "BTCUSDT", "price": "1000"})
        dumped = m.model_dump(exclude_none=True)
        assert "comment" not in dumped

        dumped = m.model_dump(exclude_none=False)
        assert "comment" in dumped
        assert dumped["comment"] is None

    def test_base_model_ignores_extra_fields(self):
        class Dummy(core.PhemexModel):
            pass

        # PhemexModel uses extra="ignore" — extra fields are silently dropped
        d = Dummy(foo="bar")  # type: ignore
        assert not hasattr(d, "foo")

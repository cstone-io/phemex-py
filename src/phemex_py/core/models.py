from decimal import Decimal
from functools import reduce
import logging
from typing import Any, ClassVar, Self, TypeAlias, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    ModelWrapValidatorHandler,
    SerializerFunctionWrapHandler,
    SerializationInfo,
    model_serializer,
    model_validator,
)
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue

from .products import get_products
from ..exceptions import ValidationError

logger = logging.getLogger(__name__)


def options(*allowed: str | None):
    def _validator(v: str | None):
        if isinstance(v, str) and v.lower() == "none":
            v = None
        if v not in allowed:
            raise ValueError(f"Must be one of {allowed}")
        return v

    return AfterValidator(_validator)


"""
Typed scalar helpers for Phemex API models. For more information see:
https://phemex-docs.github.io/#price-ratio-value-scales

- Input (API → Python): raw strings like "123450000" are descaled automatically
  into human-readable floats/Decimals.

- Output (Python → API): values are automatically scaled back up and serialized
  as strings, exactly in the format Phemex expects.
"""


class PhemexScale:
    """Marker for fields that scale dynamically from PRODUCTS."""

    def __init__(self, key: str):
        self.key = key

    @classmethod
    def value(cls):
        return cls("valueScale")

    @classmethod
    def price(cls):
        return cls("priceScale")

    @classmethod
    def ratio(cls):
        return cls("ratioScale")


class PhemexDecimal(Decimal):
    @classmethod
    def validate(cls, v) -> Self:
        if isinstance(v, cls):
            return v
        return cls(str(v))

    @classmethod
    def sum(cls, values: list[Self]) -> Self:
        return reduce(lambda x, y: x + y, values, cls(0))

    # managed by pydantic

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        def _serialize(instance: Any, _: Any) -> Any: # second param info unused
            return cls._str(instance) if instance is not None else None

        # accept str, int, float, Decimal
        from_any_schema = core_schema.chain_schema([
            core_schema.union_schema([
                core_schema.str_schema(),
                core_schema.float_schema(),
                core_schema.int_schema(),
                core_schema.decimal_schema(),
            ]),
            core_schema.no_info_plain_validator_function(cls.validate),
        ])

        return core_schema.json_or_python_schema(
            json_schema=from_any_schema,
            python_schema=core_schema.union_schema(
                [
                    from_any_schema,
                    core_schema.is_instance_schema(cls),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                _serialize,
                info_arg=True,
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())

    @staticmethod
    def _str(v: Decimal) -> str:
        # avoid scientific notation, match Phemex API expectations
        return format(v, "f")

    # force strong internal override of Decimal

    def __new__(cls, value: int | float | str | Decimal = "0", *args, **kwargs):
        return super().__new__(cls, str(value))

    def __repr__(self):
        return f"PhemexDecimal('{self.__str__()}')"

    # preserve type on operations

    @classmethod
    def _convert(cls, result):
        if isinstance(result, Decimal) and not isinstance(result, cls):
            return cls(result)
        return result

    @classmethod
    def _coerce_operand(cls, other):
        if isinstance(other, float):
            other = Decimal(str(other))
        elif isinstance(other, str):
            other = Decimal(other)
        return other

    def __add__(self, other) -> Self:
        operation = super().__add__
        operand = self._coerce_operand(other)
        return self._convert(operation(operand))

    def __radd__(self, other) -> Self:
        if other == 0:
            return self
        return self.__add__(other)

    def __sub__(self, other) -> Self:
        operation = super().__sub__
        operand = self._coerce_operand(other)
        return self._convert(operation(operand))

    def __rsub__(self, other) -> Self:
        operand = self._coerce_operand(other)
        output = operand.__sub__(self)  # reverse operation
        return self._convert(output)

    def __mul__(self, other) -> Self:
        operation = super().__mul__
        operand = self._coerce_operand(other)
        return self._convert(operation(operand))

    def __rmul__(self, other) -> Self:
        return self.__mul__(other)

    def __truediv__(self, other) -> Self:
        operation = super().__truediv__
        operand = self._coerce_operand(other)
        return self._convert(operation(operand))

    def __rtruediv__(self, other) -> Self:
        operand = self._coerce_operand(other)
        output = operand.__truediv__(self)  # reverse operation
        return self._convert(output)

    def __floordiv__(self, other) -> Self:
        operation = super().__floordiv__
        operand = self._coerce_operand(other)
        return self._convert(operation(operand))

    def __rfloordiv__(self, other) -> Self:
        operand = self._coerce_operand(other)
        output = operand.__floordiv__(self)  # reverse operation
        return self._convert(output)

    def __mod__(self, other) -> Self:
        operation = super().__mod__
        operand = self._coerce_operand(other)
        return self._convert(operation(operand))

    def __rmod__(self, other) -> Self:
        operand = self._coerce_operand(other)
        output = operand.__mod__(self)  # reverse operation
        return self._convert(output)

    def __divmod__(self, other) -> Self:
        operation = super().__divmod__
        operand = self._coerce_operand(other)
        q, r = operation(operand)  # returns tuple, convert both
        return self._convert(q), self._convert(r)

    def __rdivmod__(self, other) -> Self:
        operand = self._coerce_operand(other)
        q, r = operand.__divmod__(self)  # reverse operation
        return self._convert(q), self._convert(r)

    def __pow__(self, other, mod = None) -> Self:
        operation = super().__pow__
        operand = self._coerce_operand(other)
        return self._convert(operation(operand))

    def __rpow__(self, other, mod = None) -> Self:
        operand = self._coerce_operand(other)
        output = operand.__pow__(self)  # reverse operation
        return self._convert(output)

    def __neg__(self) -> Self:
        return self._convert(super().__neg__())

    def __pos__(self) -> Self:
        return self._convert(super().__pos__())

    def __abs__(self) -> Self:
        return self._convert(super().__abs__())

    def __eq__(self, other) -> Self:
        operand = self._coerce_operand(other)
        return super().__eq__(operand)


PhemexDecimalLike: TypeAlias = PhemexDecimal | Decimal | str | int | float


class PhemexModel(BaseModel):
    """
    Base model that all Phemex API models should inherit from. Phemex uses a custom number system which is powered by
    our PhemexDecimal model. This automatically handles serialization and deserialization (validation in pydantic terms)
    by scaling values dynamically based on the product's configuration. Meant to be used in strict conjunction with the
    Phemex API only.
    """
    __products__ = get_products()
    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        serialize_by_alias=True,
        validate_by_alias=True,
        validate_by_name=True,
    )

    def autoscale(self, mode: Literal["serialize", "validate"]):
        fields = self.__class__.model_fields
        for name, field in fields.items():
            value = getattr(self, name)
            if value is None:
                continue

            scale_meta = next((m for m in field.metadata if isinstance(m, PhemexScale)), None)
            if not scale_meta or not scale_meta.key:
                continue

            symbol = getattr(self, "symbol", None)
            futures = self.__products__.get("futures")
            if not symbol or symbol not in futures:
                raise ValidationError(
                    message=f"Cannot {mode} PhemexDecimal field {name} without valid symbol",
                    context={
                        "field": name,
                        "value": value,
                        "symbol": symbol,
                        "scale_key": scale_meta.key,
                        "available_symbols": list(futures.keys()) if futures else None,
                    }
                )

            scale = futures[symbol][scale_meta.key]
            factor = 10 ** scale if mode == "serialize" else 10 ** -scale
            new_value = PhemexDecimal.validate(value * factor)
            object.__setattr__(self, name, new_value)

    @model_validator(mode="wrap")
    @classmethod
    def _validate(cls, data: Any, handler: ModelWrapValidatorHandler) -> Self:
        """
        Run normal Pydantic validation first, then apply Phemex scaling.
        """
        model = handler(data)
        model.autoscale("validate")

        logger.debug(f"Final validated model: {model}")
        return model

    @model_serializer(mode="wrap", when_used="always")
    def _serialize(self, handler: SerializerFunctionWrapHandler, info: SerializationInfo) -> Any:
        """
        Wrap the default serializer so we inherit all of Pydantic's normal
        behavior (exclude_none, by_alias, include/exclude, nested models, etc.)
        and then apply Phemex-specific scaling adjustments.

        Scaling is applied to the output dict rather than mutating self, so
        model_dump() can be called multiple times without compounding the scale.
        """
        out = handler(self)

        fields = self.__class__.model_fields
        for name, field in fields.items():
            value = getattr(self, name)
            if value is None:
                continue

            scale_meta = next((m for m in field.metadata if isinstance(m, PhemexScale)), None)
            if not scale_meta or not scale_meta.key:
                continue

            symbol = getattr(self, "symbol", None)
            futures = self.__products__.get("futures")
            if not symbol or symbol not in futures:
                raise ValidationError(
                    message=f"Cannot serialize PhemexDecimal field {name} without valid symbol",
                    context={
                        "field": name,
                        "value": value,
                        "symbol": symbol,
                        "scale_key": scale_meta.key,
                        "available_symbols": list(futures.keys()) if futures else None,
                    }
                )

            scale = futures[symbol][scale_meta.key]
            scaled_value = PhemexDecimal._str(PhemexDecimal.validate(value * 10 ** scale))

            serialized_key = field.serialization_alias or field.alias or name
            if serialized_key in out:
                out[serialized_key] = scaled_value

        logger.debug(f"Serialization instructions: {info}")
        logger.debug(f"Final serialized output: {out}")
        return out

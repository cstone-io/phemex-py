from phemex_py.core.models import PhemexModel, PhemexDecimal
from phemex_py.core.requests import Request


class TestPhemexRequest:
    def test_request_dump_body_from_model(self):
        class Dummy(PhemexModel):
            symbol: str
            price: PhemexDecimal

        model = Dummy.model_validate(dict(symbol="BTCUSDT", price="12345"))
        req = Request.post("/test", body=model)

        # dump_body should give valid JSON string
        body_str = req.build_body_json()
        assert isinstance(body_str, str)
        assert '"price":"12345"' in body_str

    def test_request_dump_body_from_dict(self):
        req = Request.post("/test", body={"foo": "bar"})
        body_str = req.build_body_json()
        assert body_str == '{"foo":"bar"}'

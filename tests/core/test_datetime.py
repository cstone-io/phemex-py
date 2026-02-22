import datetime
import pytest

import phemex_py.core.datetime as dt


class TestUnixConversion:
    def test_unix_now(self, monkeypatch):
        fake_now = datetime.datetime(2025, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)

        # Patch .now() specifically
        class DummyDatetime(datetime.datetime):
            @classmethod
            def now(cls, tz=None):
                return fake_now

        # The module uses `import datetime` (the stdlib module), then `datetime.datetime.now(...)`.
        # We patch the `datetime` class attribute on the stdlib module as seen by the target module.
        import phemex_py.core.datetime as _dt_mod
        monkeypatch.setattr(_dt_mod.datetime, "datetime", DummyDatetime)

        result_ms = dt.unix_now(ms=True)
        result_s = dt.unix_now(ms=False)

        assert result_ms == int(fake_now.timestamp() * 1000)
        assert result_s == int(fake_now.timestamp())

    def test_unix_to_datetime_and_back(self):
        ts_ms = 1_700_000_000_000
        ts_s = ts_ms // 1000

        dt_obj_ms = dt.unix_to_datetime(ts_ms, ms=True)
        dt_obj_s = dt.unix_to_datetime(ts_s, ms=False)

        assert dt_obj_ms == dt_obj_s
        assert dt.datetime_to_unix(dt_obj_ms, ms=True) == ts_ms
        assert dt.datetime_to_unix(dt_obj_s, ms=False) == ts_s

    def test_unix_to_iso_and_back(self):
        ts_ms = 1_700_000_000_000
        iso_str = dt.unix_to_iso(ts_ms, ms=True)

        parsed = dt.iso_to_unix(iso_str, ms=True)
        assert parsed == ts_ms


class TestDatetimeConversion:
    def test_datetime_to_iso_and_back(self):
        aware_dt = datetime.datetime(2025, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
        iso_str = dt.datetime_to_iso(aware_dt)

        parsed_dt = dt.iso_to_datetime(iso_str)
        assert parsed_dt == aware_dt

    def test_datetime_to_iso_raises_on_naive(self):
        naive = datetime.datetime(2025, 1, 1, 12, 0)  # no tzinfo
        with pytest.raises(ValueError):
            dt.datetime_to_iso(naive)

    def test_datetime_to_unix_raises_on_naive(self):
        naive = datetime.datetime(2025, 1, 1, 12, 0)
        with pytest.raises(ValueError):
            dt.datetime_to_unix(naive)

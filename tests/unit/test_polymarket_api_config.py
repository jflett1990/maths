import os
from pathlib import Path

from polymarket_bot.app import run_once


class CaptureAdapter:
    def __init__(self):
        self.headers = None


def test_config_loads_polymarket_api_fields() -> None:
    from polymarket_bot.core.config import load_config

    cfg = load_config("configs/base.yaml")
    assert cfg.adapters.clob_base_url.startswith("https://")
    assert cfg.adapters.poly_api_key_env == "POLY_API_KEY"


def test_run_once_uses_configured_clob_url_and_env_headers(tmp_path: Path, monkeypatch) -> None:
    import polymarket_bot.app as app_mod

    captured = {}

    class StubMarketAdapter:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def fetch_active_markets(self):
            return []

    monkeypatch.setattr(app_mod, "PolymarketRESTAdapter", StubMarketAdapter)
    monkeypatch.setenv("POLY_ADDRESS", "0xabc")
    monkeypatch.setenv("POLY_API_KEY", "key")
    monkeypatch.setenv("POLY_PASSPHRASE", "pass")
    monkeypatch.setenv("POLY_SIGNATURE", "sig")
    monkeypatch.setenv("POLY_TIMESTAMP", "123")

    cfg = Path("configs/base.yaml").read_text().replace("output_dir: state", f"output_dir: {tmp_path / 'state'}")
    p = tmp_path / "c.yaml"
    p.write_text(cfg)
    run_once(str(p), wallet_adapter=type("W", (), {"fetch_wallet_trades": lambda self, wallet_id, limit=500: []})())

    assert captured["base_url"] == "https://clob.polymarket.com"
    assert captured["poly_headers"]["POLY_API_KEY"] == "key"

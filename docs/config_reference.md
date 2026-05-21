# Config Reference
See `configs/base.yaml` for full schema:
- mode / mode_controls
- kill_switch
- execution limits
- recorder reliability flags
- replay corruption handling

## adapters (Polymarket CLOB)
- `clob_base_url` (default `https://clob.polymarket.com`)
- `rate_limit_per_sec`, `timeout_sec`, `retries`
- L2 header env mappings:
  - `poly_address_env`
  - `poly_api_key_env`
  - `poly_passphrase_env`
  - `poly_signature_env`
  - `poly_timestamp_env`

Set the mapped env vars at runtime to pass `POLY_*` headers to authenticated
CLOB endpoints. Public read endpoints do not require these headers.

## wallet_validation
- `train_frac`, `val_frac`
- `min_samples`
- `latency_scenarios_sec`
- `baselines`
- `leakage_strict`
- `report_json_path`, `report_md_path`

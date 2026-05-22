# Secrets Setup

Environment-only secret policy:
- `KALSHI_API_KEY`
- `KALSHI_PRIVATE_KEY`
- `KALSHI_PASSPHRASE`
- `OPENAI_API_KEY` (optional reporting summaries)
- `ANTHROPIC_API_KEY` (optional reporting summaries)

Do not hardcode secrets in config or source.

Kalshi authenticated APIs use these headers:
- `KALSHI-ACCESS-KEY`
- `KALSHI-ACCESS-SIGNATURE`
- `KALSHI-ACCESS-TIMESTAMP`

See Kalshi API docs (`/trade-api/v2/api_keys`) for API key management and required authentication headers.

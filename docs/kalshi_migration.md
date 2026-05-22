# Kalshi Migration Summary

This repo is being migrated from Polymarket naming to a platform-neutral framework with Kalshi as first adapter.

- New neutral package: `prediction_market_bot`
- New adapter protocol + capabilities object
- New `prediction_market_bot.adapters.kalshi` adapter with fail-closed live methods
- Public wallet graph intelligence is unsupported on Kalshi and disabled by default

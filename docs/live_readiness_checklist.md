# Live Readiness Checklist
- `mode: live`
- `mode_controls.allow_live_orders: true`
- `mode_controls.live_confirmation: I_ACKNOWLEDGE_LIVE_TRADING`
- `kill_switch.global_enabled: true`
- Credentials configured out-of-band.
- Dry-run shadow mode passed with zero critical anomalies.
- Governance registry check must pass with no fingerprint mismatch.
- Live mode fails closed on unregistered or expired wallet signal governance.

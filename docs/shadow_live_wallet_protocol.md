# Shadow-live Wallet Experiment Protocol (1-2 weeks)
- Daily minimums: 100 observations, 20 resolved rows, data_quality_score >= 0.7, unavailable_row_rate <= 0.25.
- Allowed modes during shadow: `disabled`, `observe_only`, `risk_filter_only`.
- Kill criteria: leakage flag, latency edge <= 0 for 3 consecutive days, false_positive_rate > 0.6.
- Extension criteria: sample/resolution below minimums.
- Promotion gates:
  - paper influence allowed: `ranking_boost_allowed` for >=5 days stable.
  - live risk-filter only: `risk_filter_only` with stable block benefits.
  - wallet_alpha in live edge: only after `ranking_boost_allowed` or stronger plus OOS baseline outperformance and positive after-cost latency edge.
- Daily report fields: markets observed, wallet events, top signals, ignored signals, improved/harmed trades, blocked bad trades, false positives, latency decay, baseline comparison, recommendation, anomalies.

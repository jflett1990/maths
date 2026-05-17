# System Design Memo

## Objective
Trade only when post-cost, post-risk structural edge is positive and above threshold.

## Architecture
- **Adapters**: isolate Polymarket APIs/WS and portfolio interfaces.
- **Universe Builder**: ranks markets by liquidity, spread, OI, event timing, rewards, concentration proxy, volatility, clarity.
- **Resolution Risk Gate**: hard reject ambiguous markets.
- **Signal Engine**: combines forecast/cross-market/spread-reward alpha; subtracts execution, toxicity, and resolution penalties.
- **Risk Engine**: constraints and circuit-breakers.
- **Execution Engine**: passive laddered quoting + aggressive guarded taker mode.
- **Paper Broker + Recorder**: deterministic decision/fill/state logging for replay.

## MVP scope
- End-to-end paper mode loop
- Config-driven thresholds and risk limits
- Market ranking with expected_edge
- Hard gating by resolution and toxicity
- PnL decomposition placeholders driven by executed fills and marks

## Highest-risk assumptions
1. Polymarket endpoint shapes can change; adapter uses typed normalization + defensive parsing.
2. Public flow features are low-fidelity; toxicity model is conservative and can only penalize.
3. Reward economics vary by market; reward alpha is feature-flagged and haircut.
4. Backtests limited to recorded/replayable state only.

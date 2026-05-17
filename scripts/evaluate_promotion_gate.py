from __future__ import annotations

import argparse
import json

from polymarket_bot.governance.gate import evaluate_promotion_gate

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--report-json", required=True)
    p.add_argument("--requested-mode", required=True)
    p.add_argument("--allow-edge-contribution", action="store_true")
    a = p.parse_args()
    rep = json.loads(open(a.report_json).read())
    gate, exp = evaluate_promotion_gate(rep, a.requested_mode, a.allow_edge_contribution)
    print(json.dumps({"granted_mode": gate.granted_mode, "reasons": gate.reasons, "expires_at": exp}, sort_keys=True))

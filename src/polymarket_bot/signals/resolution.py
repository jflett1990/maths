from polymarket_bot.core.models import Market

AMBIGUITY_TERMS = {"likely", "expected", "major", "significant", "reportedly"}


def resolution_risk_score(market: Market) -> float:
    text = market.rules_text.lower() + " " + market.question.lower()
    vagueness = sum(1 for t in AMBIGUITY_TERMS if t in text) * 0.08
    missing_authority = 0.2 if "official" not in text else 0.0
    missing_cutoff = 0.15 if "et" not in text and "utc" not in text else 0.0
    return min(1.0, vagueness + missing_authority + missing_cutoff)

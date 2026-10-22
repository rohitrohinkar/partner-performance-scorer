"""Pure, explainable scoring rules. No Streamlit, no LLM, so it can be unit-tested and audited."""
import pandas as pd

METRICS = {  # key: (label, default weight, help)
    "attainment": ("Revenue attainment", 30, "Revenue vs target, capped at 150%"),
    "coverage": ("Pipeline coverage", 15, "Sourced pipeline vs target; 3x = full marks"),
    "win_rate": ("Win rate", 20, "Won / (won + lost)"),
    "velocity": ("Deal velocity", 10, "Average cycle; 30 days = full marks, 120 = zero"),
    "enablement": ("Certified reps", 10, "Certified reps; 5+ = full marks"),
    "engagement": ("Engagement", 15, "QBR attended + portal logins"),
}


def normalise(df):
    """Each metric to a 0..100 scale."""
    out = pd.DataFrame(index=df.index)
    out["attainment"] = (df.revenue_inr_lakh / df.target_inr_lakh).clip(0, 1.5) / 1.5 * 100
    out["coverage"] = (df.pipeline_inr_lakh / df.target_inr_lakh).clip(0, 3) / 3 * 100
    out["win_rate"] = df.deals_won / (df.deals_won + df.deals_lost).clip(lower=1) * 100
    out["velocity"] = ((120 - df.avg_cycle_days) / 90).clip(0, 1) * 100
    out["enablement"] = df.certified_reps.clip(0, 5) / 5 * 100
    out["engagement"] = df.qbr_attended * 50 + df.portal_logins.clip(0, 25) * 2
    return out.round(1)


def score(norm, weights):
    total = sum(weights.values()) or 1
    return sum(norm[m] * w for m, w in weights.items()) / total


def quadrant(s, trend, noise=3):
    """A dip within `noise` points is treated as flat, not as a slide."""
    if s >= 60:
        return "Invest" if trend >= -noise else "Protect"
    return "Fix" if trend >= -noise else "Exit"

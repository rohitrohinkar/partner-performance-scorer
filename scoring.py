"""Pure, explainable scoring rules. No Streamlit, no LLM, so it can be unit-tested and audited.

Vocabulary follows a Careem-style partner book: merchants (food, grocery, retail), fleet partners
(vehicle suppliers behind captains) and brand partners (perks, co-marketing, payments).
"""
import pandas as pd

METRICS = {  # key: (label, default weight, help)
    "attainment": ("GMV attainment", 30, "GMV vs target, capped at 150%"),
    "fulfilment": ("Fulfilment rate", 15, "Orders or trips completed vs received"),
    "repeat": ("Repeat rate", 20, "Share of customers who come back; 60% = full marks"),
    "on_time": ("On-time rate", 10, "Orders delivered or trips started within the promised window"),
    "tools": ("Tools adopted", 10, "Careem partner tools in use (menu sync, promos, API, payouts, insights); 5 = full marks"),
    "engagement": ("Engagement", 15, "Business review attended + partner portal logins"),
}


def normalise(df):
    """Each metric to a 0..100 scale."""
    out = pd.DataFrame(index=df.index)
    out["attainment"] = (df.gmv_aed_k / df.target_gmv_aed_k).clip(0, 1.5) / 1.5 * 100
    out["fulfilment"] = df.fulfilment_pct.clip(0, 100)
    out["repeat"] = (df.repeat_rate_pct / 60).clip(0, 1) * 100
    out["on_time"] = df.on_time_pct.clip(0, 100)
    out["tools"] = df.tools_adopted.clip(0, 5) / 5 * 100
    out["engagement"] = df.review_attended * 50 + df.portal_logins.clip(0, 25) * 2
    return out.round(1)


def score(norm, weights):
    total = sum(weights.values()) or 1
    return sum(norm[m] * w for m, w in weights.items()) / total


def quadrant(s, trend, noise=3):
    """A dip within `noise` points is treated as flat, not as a slide."""
    if s >= 60:
        return "Invest" if trend >= -noise else "Protect"
    return "Fix" if trend >= -noise else "Exit"

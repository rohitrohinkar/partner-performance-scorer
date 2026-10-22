"""Partner Performance Scorer: rule-based, explainable scoring + AI-written actions.
Vocabulary follows a Careem-style partner book: merchants, fleet partners, brand partners."""
import os
import pandas as pd
import streamlit as st

from scoring import METRICS, normalise, score, quadrant

st.set_page_config(page_title="Partner Performance Scorer", page_icon="📊", layout="wide")
HERE = os.path.dirname(os.path.abspath(__file__))
st.logo(os.path.join(HERE, "assets", "careem.png"), size="large")


@st.cache_data
def load():
    return pd.read_csv(os.path.join(HERE, "partners.csv"))


def rule_actions(norm_row):
    """Fallback when no API key: actions keyed to the two weakest metrics."""
    playbook = {
        "attainment": "Re-plan the quarter GMV target with the partner and attach two named campaigns to it.",
        "fulfilment": "Audit rejected and cancelled orders for two weeks; fix the top cause (stock, prep time, vehicle availability).",
        "repeat": "Launch a return-customer offer through Careem promos and review repeat rate after 30 days.",
        "on_time": "Reset prep-time or dispatch targets with the partner; review late orders weekly.",
        "tools": "Switch on two more partner tools (menu sync, insights, automated payouts) before the next review.",
        "engagement": "Book a 30-minute reset call and reinstate the monthly business review.",
    }
    weakest = norm_row.sort_values().index[:2]
    return "\n".join(f"- {playbook[m]}" for m in weakest) + "\n- Agree one measurable commitment and review it in 30 days."


def api_key():
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY")


@st.cache_data(show_spinner=False)
def ai_actions(name, ptype, region, quad, facts: str):
    key = api_key()
    if not key:
        return None
    import anthropic
    client = anthropic.Anthropic(api_key=key)
    prompt = (
        f"You are a Careem partner manager preparing a quarterly business review with {name}, a {ptype.lower()} "
        f"in {region}, currently in the '{quad}' quadrant of our partner portfolio.\n\nQuarter-on-quarter facts:\n{facts}\n\n"
        "Write: (1) three specific improvement actions, each tied to one of the weakest metrics, each with an owner "
        "and a 30-day measurable; (2) a four-sentence business-review brief in plain language. "
        "No flattery, no jargon, no em-dashes. Markdown with two headings: Actions, Business review brief."
    )
    resp = client.messages.create(model="claude-opus-5-5", max_tokens=1200,
                                  messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in resp.content if b.type == "text")


# ---------- UI ----------
st.title("Partner Performance Scorer")
st.caption("Rules score the partner so the number is explainable. AI writes the actions and the business-review brief. "
           "Dummy data: 30 merchants, fleet partners and brand partners across UAE, KSA, Egypt and Pakistan, two quarters.")

df = load()
with st.sidebar:
    st.header("Weights")
    st.caption("Move a slider and every score, quadrant and action recomputes.")
    weights = {m: st.slider(lbl, 0, 50, d, help=h) for m, (lbl, d, h) in METRICS.items()}
    st.divider()
    types = st.multiselect("Partner type", sorted(df.type.unique()), default=sorted(df.type.unique()))
    regions = st.multiselect("Market", sorted(df.region.unique()), default=sorted(df.region.unique()))

df = df[df.type.isin(types) & df.region.isin(regions)]
norm = normalise(df)
df = df.assign(score=score(norm, weights).round(1))
q1 = df[df.quarter == "2026-Q1"].set_index("partner_id")
q2 = df[df.quarter == "2026-Q2"].set_index("partner_id")
book = q2[["partner", "type", "region", "gmv_aed_k", "score"]].copy()
book = book.rename(columns={"region": "market", "gmv_aed_k": "GMV (AED k)"})
book["trend"] = (q2.score - q1.score.reindex(q2.index)).round(1)
book["quadrant"] = [quadrant(s, t) for s, t in zip(book.score, book.trend)]
book = book.sort_values("score", ascending=False)

c1, c2, c3, c4 = st.columns(4)
for col, q in zip((c1, c2, c3, c4), ("Invest", "Protect", "Fix", "Exit")):
    sub = book[book.quadrant == q]
    col.metric(q, f"{len(sub)} partner{'s' if len(sub) != 1 else ''}", f"AED {sub['GMV (AED k)'].sum() / 1000:.1f}M GMV")

left, right = st.columns([3, 2])
with left:
    st.subheader("Portfolio: score vs quarter-on-quarter trend")
    st.scatter_chart(book, x="trend", y="score", color="quadrant", size="GMV (AED k)",
                     x_label="Score change Q1 to Q2", y_label="Q2 score (0-100)")
    st.caption("Invest: strong and holding or rising. Protect: strong but slipping more than 3 points. "
               "Fix: weak but not sliding. Exit: weak and falling. Bubble size = Q2 GMV.")
with right:
    st.subheader("Leaderboard")
    st.dataframe(book, height=420, width='stretch', hide_index=True,
                 column_config={"score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f")})

st.divider()
st.subheader("Partner drill-down")
pid = st.selectbox("Partner", book.index,
                   format_func=lambda i: f"{book.loc[i, 'partner']} ({book.loc[i, 'quadrant']}, {book.loc[i, 'score']:.0f})")
row = book.loc[pid]
n1 = norm.loc[df.index[(df.partner_id == pid) & (df.quarter == "2026-Q1")][0]]
n2 = norm.loc[df.index[(df.partner_id == pid) & (df.quarter == "2026-Q2")][0]]
breakdown = pd.DataFrame({"Q1": n1, "Q2": n2, "weight": pd.Series(weights)})
breakdown.index = [METRICS[m][0] for m in breakdown.index]
breakdown["weighted Q2"] = (breakdown.Q2 * breakdown.weight / (sum(weights.values()) or 1)).round(1)

a, b = st.columns([2, 3])
with a:
    st.markdown(f"**{row.partner}** · {row.type} · {row.market} · **{row.quadrant}**")
    st.dataframe(breakdown.round(1), width='stretch')
    st.caption("Why this score: each metric on 0-100, times its weight. Nothing hidden.")
with b:
    facts = "\n".join(f"- {m}: Q1 {breakdown.loc[m, 'Q1']:.0f} -> Q2 {breakdown.loc[m, 'Q2']:.0f} (weight {breakdown.loc[m, 'weight']})"
                      for m in breakdown.index)
    raw = q2.loc[pid]
    facts += (f"\n- GMV AED {raw.gmv_aed_k}k vs target AED {raw.target_gmv_aed_k}k; {raw.orders} orders or trips; "
              f"fulfilment {raw.fulfilment_pct}%; repeat rate {raw.repeat_rate_pct}%; on-time {raw.on_time_pct}%; "
              f"{raw.tools_adopted} of 5 partner tools adopted; {raw.portal_logins} portal logins; "
              f"business review attended: {'yes' if raw.review_attended else 'no'}")
    st.markdown("**Recommended actions and business-review brief**")
    with st.spinner("Writing actions..."):
        text = ai_actions(row.partner, row.type, row.market, row.quadrant, facts)
    if text:
        st.markdown(text)
        st.caption("Written by Claude from the facts above. The score itself never touches an LLM.")
    else:
        st.markdown("**Actions**\n" + rule_actions(n2))
        st.caption("Rule-based fallback (no API key set). Add ANTHROPIC_API_KEY to secrets for AI-written actions and a review brief.")

with st.expander("How the scoring works"):
    st.markdown("""
| Metric | Scale | Why it matters |
|---|---|---|
| GMV attainment | GMV / target, capped at 150% | The number the business actually tracks |
| Fulfilment rate | completed / received | Rejected and cancelled orders cost the customer, not just the partner |
| Repeat rate | 60% returning customers = 100 | Separates busy partners from ones customers come back to |
| On-time rate | share within the promised window | Late is the fastest way to lose a Careem customer |
| Tools adopted | 5 partner tools = 100 | Adoption is the leading indicator of next quarter's GMV |
| Engagement | review attended (50) + portal logins (up to 50) | Disengagement shows up here two quarters before it shows in GMV |

Design choice: scoring is deterministic so a partner manager can argue with it and finance can audit it.
AI is used only where judgment and language add value: the actions and the business-review narrative.
""")

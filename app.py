"""Partner Performance Scorer: rule-based, explainable scoring + AI-written actions."""
import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Partner Performance Scorer", page_icon="📊", layout="wide")
HERE = os.path.dirname(os.path.abspath(__file__))
st.logo(os.path.join(HERE, "assets", "careem.png"), size="large")

from scoring import METRICS, normalise, score, quadrant


@st.cache_data
def load():
    return pd.read_csv(os.path.join(HERE, "partners.csv"))


def rule_actions(name, norm_row):
    """Fallback when no API key: actions keyed to the two weakest metrics."""
    playbook = {
        "attainment": "Re-plan the quarter target with the partner and attach two named deals to it.",
        "coverage": "Run a joint prospecting sprint; agree 10 new qualified opportunities in 30 days.",
        "win_rate": "Shadow their next three deals and fix the discovery step that loses them.",
        "velocity": "Introduce a mutual close plan template; review stalled deals weekly.",
        "enablement": "Book certification for two more reps before the next QBR.",
        "engagement": "Schedule a 30-minute reset call and reinstate the monthly check-in.",
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
        f"You are a partner manager preparing for a QBR with {name}, a {ptype} partner in {region}, "
        f"currently in the '{quad}' quadrant of our portfolio.\n\nQuarter-on-quarter facts:\n{facts}\n\n"
        "Write: (1) three specific improvement actions, each tied to one of the weakest metrics, each with an owner "
        "and a 30-day measurable; (2) a four-sentence QBR talking-points brief in plain language. "
        "No flattery, no jargon, no em-dashes. Markdown with two headings: Actions, QBR brief."
    )
    resp = client.messages.create(model="claude-opus-5-5", max_tokens=1200,
                                  messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in resp.content if b.type == "text")


# ---------- UI ----------
st.title("Partner Performance Scorer")
st.caption("Rules score the partner so the number is explainable. AI writes the actions and the QBR brief. Dummy data, 30 partners, two quarters.")

df = load()
with st.sidebar:
    st.header("Weights")
    st.caption("Move a slider and every score, quadrant and action recomputes.")
    weights = {m: st.slider(lbl, 0, 50, d, help=h) for m, (lbl, d, h) in METRICS.items()}
    st.divider()
    types = st.multiselect("Partner type", sorted(df.type.unique()), default=sorted(df.type.unique()))
    regions = st.multiselect("Region", sorted(df.region.unique()), default=sorted(df.region.unique()))

df = df[df.type.isin(types) & df.region.isin(regions)]
norm = normalise(df)
df = df.assign(score=score(norm, weights).round(1))
q1 = df[df.quarter == "2026-Q1"].set_index("partner_id")
q2 = df[df.quarter == "2026-Q2"].set_index("partner_id")
book = q2[["partner", "type", "region", "revenue_inr_lakh", "target_inr_lakh", "score"]].copy()
book = book.rename(columns={"revenue_inr_lakh": "revenue (L)", "target_inr_lakh": "target (L)"})
book["trend"] = (q2.score - q1.score.reindex(q2.index)).round(1)
book["quadrant"] = [quadrant(s, t) for s, t in zip(book.score, book.trend)]
book = book.sort_values("score", ascending=False)

c1, c2, c3, c4 = st.columns(4)
for col, q in zip((c1, c2, c3, c4), ("Invest", "Protect", "Fix", "Exit")):
    sub = book[book.quadrant == q]
    col.metric(q, f"{len(sub)} partners", f"Rs {sub['revenue (L)'].sum():.0f}L revenue")

left, right = st.columns([3, 2])
with left:
    st.subheader("Portfolio: score vs quarter-on-quarter trend")
    st.scatter_chart(book, x="trend", y="score", color="quadrant", size="revenue (L)",
                     x_label="Score change Q1 to Q2", y_label="Q2 score (0-100)")
    st.caption("Invest: strong and holding or rising. Protect: strong but slipping more than 3 points. Fix: weak but not sliding. Exit: weak and falling. Bubble size = Q2 revenue.")
with right:
    st.subheader("Leaderboard")
    st.dataframe(book, height=420, width='stretch', hide_index=True,
                 column_config={"score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f")})

st.divider()
st.subheader("Partner drill-down")
pid = st.selectbox("Partner", book.index, format_func=lambda i: f"{book.loc[i, 'partner']} ({book.loc[i, 'quadrant']}, {book.loc[i, 'score']:.0f})")
row = book.loc[pid]
n1 = norm.loc[df.index[(df.partner_id == pid) & (df.quarter == "2026-Q1")][0]]
n2 = norm.loc[df.index[(df.partner_id == pid) & (df.quarter == "2026-Q2")][0]]
breakdown = pd.DataFrame({"Q1": n1, "Q2": n2, "weight": pd.Series(weights)})
breakdown.index = [METRICS[m][0] for m in breakdown.index]
breakdown["weighted Q2"] = (breakdown.Q2 * breakdown.weight / (sum(weights.values()) or 1)).round(1)

a, b = st.columns([2, 3])
with a:
    st.markdown(f"**{row.partner}** · {row.type} · {row.region} · **{row.quadrant}**")
    st.dataframe(breakdown.round(1), width='stretch')
    st.caption("Why this score: each metric on 0-100, times its weight. Nothing hidden.")
with b:
    facts = "\n".join(f"- {m}: Q1 {breakdown.loc[m, 'Q1']:.0f} -> Q2 {breakdown.loc[m, 'Q2']:.0f} (weight {breakdown.loc[m, 'weight']})" for m in breakdown.index)
    raw = q2.loc[pid]
    facts += f"\n- Revenue Rs {raw.revenue_inr_lakh}L vs target Rs {raw.target_inr_lakh}L; {raw.deals_won} won, {raw.deals_lost} lost; cycle {raw.avg_cycle_days} days; {raw.certified_reps} certified reps; {raw.portal_logins} portal logins; QBR attended: {'yes' if raw.qbr_attended else 'no'}"
    st.markdown("**Recommended actions and QBR brief**")
    with st.spinner("Writing actions..."):
        text = ai_actions(row.partner, row.type, row.region, row.quadrant, facts)
    if text:
        st.markdown(text)
        st.caption("Written by Claude from the facts above. The score itself never touches an LLM.")
    else:
        st.markdown("**Actions**\n" + rule_actions(row.partner, n2))
        st.caption("Rule-based fallback (no API key set). Add ANTHROPIC_API_KEY to secrets for AI-written actions and a QBR brief.")

with st.expander("How the scoring works"):
    st.markdown("""
| Metric | Scale | Why it matters |
|---|---|---|
| Revenue attainment | revenue / target, capped at 150% | The number finance actually tracks |
| Pipeline coverage | pipeline / target, 3x = 100 | Predicts next quarter, not this one |
| Win rate | won / (won + lost) | Separates busy partners from effective ones |
| Deal velocity | 30 days = 100, 120 days = 0 | Slow cycles hide dead deals |
| Certified reps | 5+ = 100 | Enablement is the leading indicator of attainment |
| Engagement | QBR attended (50) + logins (up to 50) | Disengagement shows up here two quarters before it shows in revenue |

Design choice: scoring is deterministic so a partner manager can argue with it and finance can audit it.
AI is used only where judgment and language add value: the actions and the QBR narrative.
""")

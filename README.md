# Partner Performance Scorer

Scores a Careem-style partner book (merchants, fleet partners, brand partners) with explainable rules, places each partner in an Invest / Protect / Fix / Exit quadrant, and uses an LLM only to write improvement actions and a business-review brief.

**Idea in one line:** scoring should be deterministic so people can argue with it; AI should do the narrative.

**Live app:** https://partner-scorer.streamlit.app

## Run locally

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

Optional: set `ANTHROPIC_API_KEY` (env var or `.streamlit/secrets.toml`) to get AI-written actions and a business-review brief. Without it the app falls back to a rule-based playbook keyed to the two weakest metrics.

## Files

| File | What it is |
|---|---|
| `app.py` | Streamlit UI: weight sliders, portfolio quadrant, leaderboard, drill-down, AI actions |
| `scoring.py` | Pure scoring rules, no Streamlit, no LLM. Unit-tested in `test_scoring.py` |
| `gen_data.py` | Generates `partners.csv`: 30 partners across UAE, KSA, Egypt and Pakistan, two quarters, four planted stories (a big merchant going cold, a small brand partner accelerating, a merchant hitting numbers but disengaged, a busy fleet with falling fulfilment) |
| `partners.csv` | The dataset. Self-created, no real companies. GMV in AED thousands |
| `summary.md` | 100-word summary for the application form |

## Scoring

| Metric | Scale | Default weight |
|---|---|---|
| GMV attainment | GMV / target, capped at 150% | 30 |
| Fulfilment rate | completed / received orders or trips | 15 |
| Repeat rate | 60% returning customers = 100 | 20 |
| On-time rate | share within the promised window | 10 |
| Tools adopted | 5 partner tools = 100 | 10 |
| Engagement | business review attended (50) + portal logins (up to 50) | 15 |

Quadrant: score 60+ is strong. A quarter-on-quarter drop of more than 3 points counts as slipping; smaller moves are treated as noise.

## Deploy (Streamlit Community Cloud, free)

1. Push this folder to a public GitHub repo.
2. share.streamlit.io, New app, pick the repo, main file `app.py`.
3. Advanced settings, Secrets: `ANTHROPIC_API_KEY = "..."` (optional).

# Partner Performance Scorer

Scores partner performance with explainable rules, places each partner in an Invest / Protect / Fix / Exit quadrant, and uses an LLM only to write improvement actions and a QBR brief.

**Idea in one line:** scoring should be deterministic so people can argue with it; AI should do the narrative.

## Run locally

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

Optional: set `ANTHROPIC_API_KEY` (env var or `.streamlit/secrets.toml`) to get AI-written actions and a QBR brief. Without it the app falls back to a rule-based playbook keyed to the two weakest metrics.

## Files

| File | What it is |
|---|---|
| `app.py` | Streamlit UI: weight sliders, portfolio quadrant, leaderboard, drill-down, AI actions |
| `scoring.py` | Pure scoring rules, no Streamlit, no LLM. Unit-tested in `test_scoring.py` |
| `gen_data.py` | Generates `partners.csv`: 30 partners, two quarters, four planted stories (a big reseller going cold, a small referral partner accelerating, a partner hitting numbers but disengaged, a busy partner not closing) |
| `partners.csv` | The dataset. Self-created, no real companies |
| `summary.md` | 100-word summary for the application form |

## Scoring

| Metric | Scale | Default weight |
|---|---|---|
| Revenue attainment | revenue / target, capped at 150% | 30 |
| Pipeline coverage | pipeline / target, 3x = 100 | 15 |
| Win rate | won / (won + lost) | 20 |
| Deal velocity | 30-day cycle = 100, 120 days = 0 | 10 |
| Certified reps | 5+ = 100 | 10 |
| Engagement | QBR attended (50) + portal logins (up to 50) | 15 |

Quadrant: score 60+ is strong. A quarter-on-quarter drop of more than 3 points counts as slipping; smaller moves are treated as noise.

## Deploy (Streamlit Community Cloud, free)

1. Push this folder to a public GitHub repo.
2. share.streamlit.io, New app, pick the repo, main file `app.py`.
3. Advanced settings, Secrets: `ANTHROPIC_API_KEY = "..."` (optional).

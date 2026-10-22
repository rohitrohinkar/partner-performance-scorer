import pandas as pd
from scoring import normalise, score, quadrant, METRICS
df = pd.DataFrame([dict(revenue_inr_lakh=150, target_inr_lakh=100, pipeline_inr_lakh=300, deals_won=3, deals_lost=0,
                        avg_cycle_days=30, certified_reps=5, qbr_attended=1, portal_logins=25),
                   dict(revenue_inr_lakh=0, target_inr_lakh=100, pipeline_inr_lakh=0, deals_won=0, deals_lost=0,
                        avg_cycle_days=120, certified_reps=0, qbr_attended=0, portal_logins=0)])
n = normalise(df)
w = {m: v[1] for m, v in METRICS.items()}
s = score(n, w)
assert s.iloc[0] == 100 and s.iloc[1] == 0, s.tolist()
assert (quadrant(70, 1), quadrant(70, -5), quadrant(50, -2), quadrant(50, -5)) == ("Invest", "Protect", "Fix", "Exit")
print("scoring ok")

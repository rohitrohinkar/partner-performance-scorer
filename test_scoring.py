import pandas as pd
from scoring import normalise, score, quadrant, METRICS
df = pd.DataFrame([dict(gmv_aed_k=150, target_gmv_aed_k=100, fulfilment_pct=100, repeat_rate_pct=60, on_time_pct=100,
                        tools_adopted=5, review_attended=1, portal_logins=25),
                   dict(gmv_aed_k=0, target_gmv_aed_k=100, fulfilment_pct=0, repeat_rate_pct=0, on_time_pct=0,
                        tools_adopted=0, review_attended=0, portal_logins=0)])
n = normalise(df)
w = {m: v[1] for m, v in METRICS.items()}
s = score(n, w)
assert s.iloc[0] == 100 and s.iloc[1] == 0, s.tolist()
assert (quadrant(70, 1), quadrant(70, -5), quadrant(50, -2), quadrant(50, -5)) == ("Invest", "Protect", "Fix", "Exit")
print("scoring ok")

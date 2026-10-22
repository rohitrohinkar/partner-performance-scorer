"""Self-generated dummy partner data: 30 partners x 2 quarters. No real companies."""
import csv, random

random.seed(7)
TYPES = ["Reseller", "Referral", "ISV"]
REGIONS = ["India", "UAE", "SEA"]
NAMES = ["Arcline", "Bluefin", "Cedar Systems", "Delta Edge", "Everspring", "Fortis", "Greywave", "Helix Tech",
         "Ironbark", "Juniper Cloud", "Kestrel", "Lumen Works", "Meridian", "Northgate", "Orbit Labs", "Pinnacle",
         "Quartz", "Riverstone", "Solaris", "Tidewater", "Umbra", "Vantage", "Westbrook", "Xenon", "Yardley", "Zephyr",
         "Altura", "Brightpath", "Crestline", "Dunmore"]

# Planted stories (index: multiplier for Q2 revenue, win rate shift, logins shift)
STORIES = {
    0: dict(rev=0.45, win=-0.15, logins=-25, note="big reseller going cold", type="Reseller", target=118.0),
    5: dict(rev=2.4, win=0.12, logins=20, note="small referral partner accelerating", type="Referral", target=12.0),
    12: dict(rev=1.0, win=0.0, logins=-30, note="hitting numbers but disengaged"),
    20: dict(rev=0.7, win=-0.05, logins=5, note="busy but not closing"),
}

def row(i, name, q, base):
    s = STORIES.get(i, dict(rev=random.uniform(0.85, 1.25), win=random.uniform(-0.05, 0.05), logins=random.randint(-8, 8)))
    target = base["target"]
    revenue = base["revenue"] * (1 if q == "2026-Q1" else s["rev"])
    win = min(0.9, max(0.05, base["win"] + (0 if q == "2026-Q1" else s["win"])))
    deals = max(1, int(revenue / base["deal_size"]))
    lost = max(0, int(deals / win - deals))
    logins = max(0, base["logins"] + (0 if q == "2026-Q1" else s["logins"]))
    return dict(
        partner_id=f"P{i+1:03d}", partner=name, type=base["type"], region=base["region"], quarter=q,
        target_inr_lakh=round(target, 1), revenue_inr_lakh=round(revenue, 1),
        pipeline_inr_lakh=round(revenue * random.uniform(1.5, 4.0), 1),
        deals_won=deals, deals_lost=lost,
        avg_cycle_days=int(base["cycle"] * random.uniform(0.9, 1.15)),
        certified_reps=base["reps"], qbr_attended=1 if logins > 12 or random.random() > 0.3 else 0,
        portal_logins=logins,
    )

rows = []
for i, name in enumerate(NAMES):
    t = STORIES.get(i, {}).get("type", random.choice(TYPES))
    target = {"Reseller": random.uniform(40, 120), "Referral": random.uniform(8, 30), "ISV": random.uniform(20, 60)}[t]
    target = STORIES.get(i, {}).get("target", target)
    base = dict(type=t, region=random.choice(REGIONS), target=target,
                revenue=target * random.uniform(0.5, 1.3), deal_size=random.uniform(2, 9),
                win=random.uniform(0.2, 0.6), cycle=random.randint(35, 120), reps=random.randint(0, 6),
                logins=random.randint(3, 45))
    for q in ("2026-Q1", "2026-Q2"):
        rows.append(row(i, name, q, base))

with open("partners.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(len(rows), "rows written")

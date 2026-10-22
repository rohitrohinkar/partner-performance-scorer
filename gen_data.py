"""Self-generated dummy partner data: 30 partners x 2 quarters. No real companies.
Careem-style book: merchants, fleet partners, brand partners across UAE, KSA, Egypt, Pakistan."""
import csv, random

random.seed(7)
REGIONS = ["UAE", "KSA", "Egypt", "Pakistan"]
M, F, B = "Merchant", "Fleet partner", "Brand partner"
NAMES = [("Al Noor Kitchen", M), ("Bluefin Fleet", F), ("Cedar Grocers", M), ("Delta Motors", F), ("Everspring Cafe", M),
         ("Fortis Perks", B), ("Greywave Logistics", F), ("Helix Pharmacy", M), ("Ironbark Burgers", M), ("Juniper Rides", F),
         ("Kestrel Bakery", M), ("Lumen Telecom", B), ("Meridian Mart", M), ("Northgate Fleet", F), ("Orbit Sweets", M),
         ("Pinnacle Cars", F), ("Quartz Bank", B), ("Riverstone Foods", M), ("Solaris Fitness", B), ("Tidewater Fleet", F),
         ("Umbra Flowers", M), ("Vantage Pay", B), ("Westbrook Grill", M), ("Xenon Electronics", M), ("Yardley Fleet", F),
         ("Zephyr Cinemas", B), ("Altura Shawarma", M), ("Brightpath Rentals", F), ("Crestline Pizza", M), ("Dunmore Pets", M)]

# Planted stories: Q2 multipliers / shifts vs Q1
STORIES = {
    "Al Noor Kitchen": dict(gmv=0.45, repeat=-12, logins=-25, note="big merchant going cold", target=1800.0),
    "Fortis Perks": dict(gmv=2.4, repeat=10, logins=20, note="small brand partner accelerating", target=120.0),
    "Meridian Mart": dict(gmv=1.0, repeat=0, logins=-30, note="hitting numbers but disengaged"),
    "Tidewater Fleet": dict(gmv=0.95, repeat=-3, logins=5, note="busy fleet, poor fulfilment", fulfil=-18),
}

def row(i, name, q, base):
    s = STORIES.get(name, dict(gmv=random.uniform(0.85, 1.25), repeat=random.uniform(-4, 4), logins=random.randint(-8, 8)))
    q2 = q == "2026-Q2"
    gmv = base["gmv"] * (s["gmv"] if q2 else 1)
    repeat = min(75, max(5, base["repeat"] + (s["repeat"] if q2 else 0)))
    fulfil = min(99, max(40, base["fulfil"] + (s.get("fulfil", random.uniform(-3, 3)) if q2 else 0)))
    logins = max(0, base["logins"] + (s["logins"] if q2 else 0))
    return dict(
        partner_id=f"P{i+1:03d}", partner=name, type=base["type"], region=base["region"], quarter=q,
        target_gmv_aed_k=round(base["target"], 1), gmv_aed_k=round(gmv, 1),
        orders=int(gmv * 1000 / base["ticket"]),
        fulfilment_pct=round(fulfil, 1), repeat_rate_pct=round(repeat, 1),
        on_time_pct=round(min(99, max(50, base["on_time"] + random.uniform(-4, 4))), 1),
        tools_adopted=base["tools"], review_attended=1 if logins > 12 or random.random() > 0.3 else 0,
        portal_logins=logins,
    )

rows = []
for i, (name, t) in enumerate(NAMES):
    target = {"Merchant": random.uniform(300, 1500), "Fleet partner": random.uniform(400, 2000), "Brand partner": random.uniform(80, 400)}[t]
    target = STORIES.get(name, {}).get("target", target)
    base = dict(type=t, region=random.choice(REGIONS), target=target,
                gmv=target * random.uniform(0.5, 1.3), ticket={"Merchant": 45, "Fleet partner": 28, "Brand partner": 90}[t],
                repeat=random.uniform(15, 55), fulfil=random.uniform(70, 97), on_time=random.uniform(65, 95),
                tools=random.randint(0, 5), logins=random.randint(3, 45))
    for q in ("2026-Q1", "2026-Q2"):
        rows.append(row(i, name, q, base))

with open("partners.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(len(rows), "rows written")

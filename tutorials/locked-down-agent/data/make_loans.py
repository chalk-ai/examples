"""Generate data/loans.csv: 2,000 fictional loan applications with a known default pattern.

Run from the tutorial folder with `uv run python data/make_loans.py`. The output is the same on
every run, so the agent's answers in the tutorial match yours.
"""

import csv
import random
from pathlib import Path

PURPOSES = {
    # purpose: (share of applications, base default rate)
    "debt_consolidation": (0.34, 0.11),
    "home_improvement": (0.18, 0.07),
    "car": (0.16, 0.06),
    "small_business": (0.10, 0.24),
    "education": (0.08, 0.13),
    "medical": (0.08, 0.15),
    "vacation": (0.06, 0.09),
}

rng = random.Random(7)
rows = []
for i in range(1, 2001):
    purpose = rng.choices(list(PURPOSES), weights=[w for w, _ in PURPOSES.values()])[0]
    credit_score = max(520, min(840, int(rng.gauss(690, 55))))
    annual_income = max(18_000, int(rng.lognormvariate(11.0, 0.45)) // 500 * 500)
    loan_amount = max(1_000, int(annual_income * rng.uniform(0.05, 0.45)) // 250 * 250)
    term_months = rng.choice([36, 36, 36, 60])

    rate = PURPOSES[purpose][1]
    rate *= 1.0 + (690 - credit_score) / 120  # lower scores default more
    rate *= 1.0 + (loan_amount / annual_income - 0.2)  # bigger loans relative to income too
    rate *= 1.25 if term_months == 60 else 1.0
    defaulted = int(rng.random() < max(0.01, min(0.9, rate)))

    rows.append({
        "application_id": f"A{i:05d}",
        "purpose": purpose,
        "loan_amount": loan_amount,
        "annual_income": annual_income,
        "credit_score": credit_score,
        "term_months": term_months,
        "defaulted": defaulted,
    })

out = Path(__file__).parent / "loans.csv"
with out.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote {len(rows)} applications to {out}")

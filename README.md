# Repayment Lab

A reproducible **Python + SQL collections analytics portfolio project** by Anup Dagala. It answers: *where is repayment deteriorating, how does it change with loan age, and can we reconcile every rupee?*

**Entirely synthetic. Independent project; no Navi affiliation, customer data, proprietary information, or claims about Navi's performance.**

## Run in under a minute

Python 3.10+; no third-party Python dependencies.

```sh
python lab.py
python -m unittest discover -s tests -v
```

Open `demo/index.html` directly in a browser. It is a self-contained interactive dashboard: no CDN, server, credentials, or network calls. Optionally serve it with `python -m http.server 8000 --directory demo`.

## What to inspect

- Snapshot and borrower-segment filters; KPI cards and loan-level drilldown.
- DPD distribution, Aug→Sep transition counts and row percentages.
- Origination cohorts compared at the same month-on-book, avoiding age confounding.
- Point-in-time payment filtering; split payment aggregation before joins.
- Integer-paise money, capped allocations, explicit overpayment flags and ledger reconciliation.
- Exported CSVs, SQLite database, reproducible raw tables and artifact hashes.

The committed `demo/` is ready to open. `sql/schema.sql` and `sql/snapshot.sql` expose the core analytical logic. The sample has 600 loans, 3,600 installments and reproducible split payments.

## Metric contract

`docs/technical-brief.md` defines every denominator, cutoff, accounting limitation and simulation assumption. Scheduled balances include installment amounts; they are **not principal exposure**, regulatory NPA or IFRS measures. This demo excludes interest decomposition, reversals, collections interventions and real-world ingestion. Collection rate is cumulative against installments due at the cutoff, not a cash-in-month measure.

## Verification

21 Python tests passed, including a hand-calculated ledger and temporal leakage checks. 12 date/segment combinations passed in a Node DOM harness (`node tests/check_dashboard.cjs`). The harness checks rendered content and filter behavior; it is not a browser screenshot or cross-browser test. See `docs/verification.md` for boundaries.

## BI handoff

Use `demo/loan_snapshot.csv` in Power BI/Tableau to rebuild the September snapshot. See `docs/bi-handoff.md` for measures and reconciliation. No PBIX or Tableau workbook is claimed.

## Publication

Intended repository name: `repayment-lab`. Once GitHub CLI is authenticated, run:

```sh
gh repo create repayment-lab --public --source=. --remote=origin --push
```

This command publishes the independent project; GitHub Pages deployment is optional and not included. A CI workflow is present, but a live GitHub Actions run is not yet verified.

MIT license.

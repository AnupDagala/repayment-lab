# Repayment Lab

**Python + SQL collections analytics by Anup Dagala.** Point-in-time repayment metrics, delinquency transitions, comparable origination cohorts, drilldown and integer-paise ledger reconciliation.

Entirely synthetic data. Independent portfolio project; no Navi affiliation, customer data or claims about Navi's performance.

## Run

The complete verified project is packaged in `Repayment_Lab.zip`, including the original SQL, 21 tests, docs, workflow, CSV exports, database and self-contained dashboard. Root Python and dashboard-template files are also exposed for code review. Restore the source tree once after cloning:

```sh
python bootstrap.py
python lab.py
python -m unittest discover -s tests -v
```

Python 3.10+; no third-party Python dependencies. Open `demo/index.html` in a browser. No server, login, CDN or network calls are needed.

Alternatively extract `Repayment_Lab.zip` and open `repayment-lab/demo/index.html` immediately.

## Evidence

21 Python tests passed. 12 date/segment combinations passed in a Node DOM harness, not a real browser test. All three snapshots reconciled with zero-paise delta and no foreign-key errors. Browser layout, live GitHub Actions and production deployment remain unverified.

Read [technical-brief.md](technical-brief.md) for metric definitions, synthetic assumptions and investigation reasoning, and [verification.md](verification.md) for verification boundaries.

## What it demonstrates

- Payments aggregated before joining to avoid multiplying installment dues.
- Historical cutoff filtering to prevent future repayments curing past delinquency.
- Partial repayment handling, capped allocation, explicit overpayment flags.
- Fixed month-on-book comparisons instead of mixing different loan ages.
- Loan drilldown, segment filters, cumulative collection rate and transition matrix.
- CSV/database handoff for Power BI or Tableau; no native BI workbook claimed.

Scheduled installment balances are not principal exposure or regulatory NPA measures. No borrower decisions, real collection actions or causal recovery-lift estimates are made.

MIT license. The repository was published using GitHub's web upload workflow; it does not preserve the original local commit ID.

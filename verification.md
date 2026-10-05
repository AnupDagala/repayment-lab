# Verification — 5 October 2026

Executed locally:

- `python lab.py`: deterministic demo generated successfully.
- `python -m unittest discover -s tests -v`: 21 tests passed.
- `node tests/check_dashboard.cjs`: 12 date/segment combinations passed in a minimal DOM harness.
- JavaScript syntax compiled successfully with Node VM.
- July, August and September snapshot reconciliation: zero-paise delta, zero foreign-key errors, zero excess payment amounts; all quality gates passed.

The Python tests include a hand-calculated partial repayment ledger, historical payment isolation, paid-oldest-installment DPD, due-today semantics, origination exclusion, zero denominator, overpayment flags/caps, reconciliation, duplicate/orphan/negative insertion rejection, bad snapshot date, transition counts/order, segment filtering, DPD boundaries, calendar month addition, payment chronology, deterministic seed, cohort age and exported artifacts.

The DOM harness runs the actual generated script and checks counts, status, labels, table row counts and absence of NaN across all 12 filter combinations. It does not prove real-browser rendering, accessibility, responsive layout or browser compatibility. No screenshot test was executed.

Unverified: live GitHub Actions, GitHub Pages, native BI workbook, warehouse integration, production deployment, real customer outcomes. Publication status must be confirmed separately; the presence of a local git commit or workflow file does not prove a GitHub push or CI pass.

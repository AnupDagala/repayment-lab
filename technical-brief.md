# Technical brief — Repayment Lab

## Business question

A collections analyst needs to distinguish actual payment deterioration from reporting errors and differences in loan age. This project combines a reconciled installment ledger with descriptive reporting and a concrete investigation plan.

## Data and assumptions

Seed 42 creates 600 anonymous synthetic loans originated Jan–Jun 2026, six monthly installments each, and two payment events for normally paying installments. All amounts are integer paise. Payments are explicitly assigned to installments; no inferred FIFO allocation occurs. Some simulated borrowers stop paying after the first installment; later New-to-credit cohorts deliberately have slower payment timing. These assumptions test whether the dashboard surfaces a known pattern. They are not estimates, trained risk predictions, or real business findings. Three month-end snapshots are July, August and September 2026. Raw exports intentionally include payments after earlier cutoffs to test point-in-time correctness.

## Definition decisions

- Loans enter a snapshot when originated on or before its cutoff; settled loans remain in the loan count.
- Dues on the cutoff are due but not yet overdue. Oldest unpaid installment strictly before cutoff determines DPD.
- `Current` means DPD 0; DPD ranges are 1–30, 31–60, 61–90, >90. The separately defined **30+ metric includes DPD 30**, which belongs to the 1–30 display bucket. Labels and threshold tests make this boundary explicit.
- Outstanding is the sum of all unpaid scheduled installments, including future installments; it is not principal outstanding.
- Overdue is the sum of unpaid installments strictly before cutoff.
- Collection rate is allocated payments against due installments divided by those dues; capped per installment, then aggregated. It is a cumulative scheduled-due measure, not a calendar-month cash collection rate.
- Excess payments are separately flagged and excluded from allocation. A flagged overpayment fails the demo quality gate even when reconciliation succeeds.
- 30+ balance share uses all scheduled outstanding for loans with DPD ≥30. This is a chosen demo metric, not a regulatory definition.
- Cohorts use month-end at a fixed month-on-book; each cohort has 100 loans. MOB 3 compares loans at the same cohort calendar age; it does not imply identical day-level age.
- Transition matrix counts matched originated loans at both cutoffs, with row denominators. No causal recovery-lift claim is made.

## Why the SQL is structured this way

Payments are aggregated to installment grain first. Joining raw payment events would multiply scheduled dues when an installment has two payments. Capping each installment before aggregating prevents one overpayment from masking another unpaid installment. Cutoff filtering happens in the payment CTE; a later repayment cannot cure a historical snapshot. Foreign keys, unique IDs and positive-amount checks enforce relational integrity. Quality checks additionally flag events before origination.

Reconciliation identity in paise:

`all scheduled dues = unpaid scheduled balance + observed payments - excess`

The export is deterministic for a fixed seed and has file-level SHA-256 hashes. SQLite keeps the project easy to reproduce offline; adapting it to a production warehouse would require incremental ingestion, ingestion-date history, reversal modeling, source reconciliation and access controls.

## Demonstrated synthetic investigation

At 30 September, the generated sample has ₹20,912,000 due, ₹16,997,000 collected, ₹3,915,000 overdue and ₹8,155,000 unpaid scheduled balance. Collection rate is 81.28%; the chosen 30+ balance share is 61.13%. These are computed simulation outputs, not lender benchmarks. Cohort and segment comparisons should lead to checking repayment timing, source quality and channel effects before making claims about borrower characteristics.

Proposed next step: collect acquisition-channel and reminder-consent evidence, validate the reporting pipeline, then test a consent-based reminder intervention with randomized holdout. Measure incremental on-time payment, opt-outs, complaints and operational cost. The present project does not estimate intervention effects or make lending/collection decisions.

## Honest boundaries

No real data, live warehouse, native Power BI/Tableau workbook, production deployment or model is used. No write-off, reversal, interest/principal split or actual reminder action is modeled. Only fixture-generated tables are ingested; this is not a general-purpose CSV validation product. Duplicate/orphan/negative values are blocked at database insertion. Dates are validated for snapshot input, and generator dates are Python date objects; the database schema does not independently validate arbitrary imported date strings.

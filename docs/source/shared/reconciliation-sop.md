---
doc_id: SOP-RECON-2025-01
gateway:
doc_type: reconciliation_sop
version: 2025-01
effective_from: 2025-01-01
effective_to:
---

# Reconciliation SOP (2025-01)

## Which fee version applies
This SOP is shared. It is not a gateway rate card. Rates stay in the gateway fee schedule and FX documents.

Store `occurred_at` as UTC. Choose the fee version with the Hong Kong civil date: `(occurred_at AT TIME ZONE 'Asia/Hong_Kong')::date`. The version must have started on or before that date, and must not have ended before that date. `effective_to` is inclusive.

2026-03-31 16:30 UTC is 2026-04-01 00:30 in Hong Kong. A NorthstarPay payment at that instant uses NSP-FEE-2026-04 and NSP-FX-2026-04, not the 2025-01 documents.

## Variance and short pay
expected_net = settlement_gross - total_fee
variance_amount = settled_amount - expected_net

`settled_amount` is what the gateway actually paid, with the same sign as `expected_net`. A negative variance means the merchant was paid less than the fee schedule allows.

When settled_amount is null, the transaction is not reconciled and mismatch_code is null. When settled_amount equals expected_net, mismatch_code is null. When they differ, mismatch_code is one of `short_pay`, `fee_drift`, or `fx_rate_drift`.

`short_pay` means the fee math is accepted and the gateway paid short. NSP-SHORT-0001 is a 100.00 USD NorthstarPay payment on 2026-03-20 under NSP-FEE-2025-01. total_fee = 3.2000. expected_net = 96.8000. settled_amount = 96.3000. variance_amount = 96.3000 - 96.8000 = -0.5000. mismatch_code = short_pay. The 0.50 gap is not a fee-schedule change.

`fee_drift` means the settled amount is consistent with a different fee than the effective schedule. `fx_rate_drift` means the settled amount is consistent with a different FX rate than the effective FX rule. Neither code changes the formula above.

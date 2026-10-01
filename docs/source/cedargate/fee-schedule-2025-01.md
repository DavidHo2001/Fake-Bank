---
doc_id: CDG-FEE-2025-01
gateway: CDG
doc_type: fee_schedule
version: 2025-01
effective_from: 2025-01-01
effective_to: 2026-05-31
---

# CedarGate fee schedule (2025-01)

## Payout terms and worked example
Applies to CedarGate payouts whose Hong Kong civil date is from 2025-01-01 through 2026-05-31 inclusive. Settlement currency is USD. CDG-FEE-2026-06 starts on 2026-06-01 and does not apply here. FX markup stays 100 bps in both versions; the conversion formula is in CDG-FX-2025-01. Markup is already inside `applied_fx_rate`. Do not add `fx_markup_amount` into `total_fee`.

Payout: percent 0.50% (`percent_rate` 0.005000), fixed fee 2.00 USD, minimum fee 2.00 USD. Round half-up to 4 decimal places.

percent_fee = round_half_up(abs(settlement_gross) * 0.005000, 4)
total_fee = max(percent_fee + 2.00, 2.00) + attempt_fee
expected_net = settlement_gross - total_fee

CDG-FEEHIKE-0001 is a 200.00 USD payout on 2026-05-20, same currency. percent_fee = 1.0000. percent plus fixed = 3.0000, which is above the minimum, so total_fee = 3.0000 and expected_net = 197.0000 USD.

## Refunds
A CedarGate refund in this version returns none of the original percent fee. Refund percent rate is 0. Fixed fee is 2.00 USD. Minimum fee is 0. The 0.25 USD failed-attempt fee does not apply to refunds. `gross_amount` is negative. `total_fee` stays positive and is subtracted from `settlement_gross`.

## Failed payouts
A failed CedarGate payout has settlement_gross 0, percent fee 0, fixed fee 0, and minimum fee 0. The failed-attempt fee is 0.25 USD, charged once.

CDG-FAIL-0001 is an 80.00 USD payout failure on 2026-05-21. total_fee = 0.2500. expected_net = 0 - 0.2500 = -0.2500 USD. This is different from a failed NorthstarPay payment, which has attempt fee 0.

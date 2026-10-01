---
doc_id: CDG-FEE-2026-06
gateway: CDG
doc_type: fee_schedule
version: 2026-06
effective_from: 2026-06-01
effective_to:
---

# CedarGate fee schedule (2026-06)

## Payout terms and worked example
Applies to CedarGate payouts whose Hong Kong civil date is on or after 2026-06-01. There is no end date. Settlement currency is USD. Do not use CDG-FEE-2025-01 for these dates.

What changed is the fixed fee and the minimum, not the FX markup. Markup remains 100 bps, and CDG-FX-2025-01 still states the conversion. Percent stays 0.50%.

Payout: percent 0.50% (`percent_rate` 0.005000), fixed fee 3.50 USD, minimum fee 3.50 USD. The previous version charged a fixed fee of 2.00 USD. Round half-up to 4 decimal places.

percent_fee = round_half_up(abs(settlement_gross) * 0.005000, 4)
total_fee = max(percent_fee + 3.50, 3.50) + attempt_fee
expected_net = settlement_gross - total_fee

CDG-FEEHIKE-0002 is the same 200.00 USD payout shape as CDG-FEEHIKE-0001, on 2026-06-02, same currency. percent_fee = 1.0000. percent plus fixed = 4.5000, which is above the minimum, so total_fee = 4.5000 and expected_net = 195.5000 USD. It costs 1.50 USD more than CDG-FEEHIKE-0001 because the fixed fee rose from 2.00 to 3.50. The percent fee did not change.

## Refunds
A CedarGate refund in this version returns none of the original percent fee. Refund percent rate is 0. Fixed fee is 3.50 USD. Minimum fee is 0. The 0.25 USD failed-attempt fee does not apply to refunds. `gross_amount` is negative. `total_fee` stays positive and is subtracted from `settlement_gross`.

## Failed payouts
A failed CedarGate payout has settlement_gross 0, percent fee 0, fixed fee 0, and minimum fee 0. The failed-attempt fee is still 0.25 USD. The June 2026 fixed-fee change does not change the attempt fee.

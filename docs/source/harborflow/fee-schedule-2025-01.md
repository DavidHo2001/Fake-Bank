---
doc_id: HFL-FEE-2025-01
gateway: HFL
doc_type: fee_schedule
version: 2025-01
effective_from: 2025-01-01
effective_to:
---

# HarborFlow fee schedule (2025-01)

## Payment terms and worked example
Applies to HarborFlow payments whose Hong Kong civil date is on or after 2025-01-01. There is no end date and no second HarborFlow fee version. Settlement currency is HKD.

Payment: percent 1.80% (`percent_rate` 0.018000), fixed fee 0.00 HKD, minimum fee 0.00 HKD. FX markup for this version is 80 bps. The conversion formula is in HFL-FX-2025-01. Markup is already inside `applied_fx_rate`. Do not add `fx_markup_amount` into `total_fee`.

Round half-up to 4 decimal places.

percent_fee = round_half_up(abs(settlement_gross) * 0.018000, 4)
total_fee = percent_fee + attempt_fee
expected_net = settlement_gross - total_fee

There is no minimum uplift. Failed-attempt fee is 0.

HFL-PAY-0001 is 500.00 HKD on 2026-02-01, same currency, so settlement_gross = 500.0000. percent_fee = 9.0000. total_fee = 9.0000. expected_net = 491.0000 HKD.

## Refunds and HFL-REFUND-0001
A HarborFlow refund returns none of the original percent fee. The 9.0000 HKD percent fee on HFL-PAY-0001 is not given back. Refund percent rate is 0. HarborFlow charges an extra fixed fee of 1.00 HKD. Minimum fee is 0. `gross_amount` is negative.

HFL-REFUND-0001 refunds that 500.00 HKD payment. settlement_gross = -500.0000. percent_fee = 0. total_fee = 1.0000. expected_net = -500.0000 - 1.0000 = -501.0000 HKD.

## Failed payments
A failed HarborFlow payment has settlement_gross 0 and every fee at 0, including the failed-attempt fee.

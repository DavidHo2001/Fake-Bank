---
doc_id: NSP-FEE-2025-01
gateway: NSP
doc_type: fee_schedule
version: 2025-01
effective_from: 2025-01-01
effective_to: 2026-03-31
---

# NorthstarPay fee schedule (2025-01)

## Payment terms and worked examples
Applies to NorthstarPay payments whose Hong Kong civil date is from 2025-01-01 through 2026-03-31 inclusive. Settlement currency is USD. The next version, NSP-FEE-2026-04, starts on 2026-04-01 and does not apply here.

A Hong Kong civil date is `(occurred_at AT TIME ZONE 'Asia/Hong_Kong')::date`. 2026-03-31 16:30 UTC is 2026-04-01 00:30 in Hong Kong, so this document does not apply to that timestamp.

Payment: percent 2.90% (`percent_rate` 0.029000), fixed fee 0.30 USD, minimum fee 0.50 USD. FX markup for this version is 150 bps. The conversion formula is in NSP-FX-2025-01. Markup is already inside `applied_fx_rate`. Do not add `fx_markup_amount` into `total_fee`.

Round half-up to 4 decimal places.

percent_fee = round_half_up(abs(settlement_gross) * 0.029000, 4)
total_fee = max(percent_fee + 0.30, 0.50) + attempt_fee
expected_net = settlement_gross - total_fee

The minimum replaces percent plus fixed only when that sum is below 0.50. It is not added on top.

NSP-MINFEE-0001 is 1.00 USD on 2026-03-15, same currency. percent_fee = 0.0290. percent plus fixed = 0.3290, which is below 0.50, so total_fee = 0.5000 and expected_net = 0.5000.

NSP-FX-0001 is 100.00 EUR on 2026-03-15. NSP-FX-2025-01 converts it to settlement_gross 106.3800 USD. percent_fee = 3.0850. percent plus fixed = 3.3850, which is above the minimum, so total_fee = 3.3850 and expected_net = 102.9950 USD.

## Refunds
A NorthstarPay refund in this version returns none of the original percent fee. Refund percent rate is 0. Fixed fee is 0.30 USD. Minimum fee is 0. `gross_amount` is negative. `total_fee` stays positive and is subtracted from `settlement_gross`.

## Failed payments
A failed NorthstarPay payment has settlement_gross 0, percent fee 0, fixed fee 0, and minimum fee 0. The failed-attempt fee in this version is 0. NSP-FAIL-0001 is an 80.00 USD failure on 2026-03-16: total_fee = 0 and expected_net = 0.

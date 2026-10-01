---
doc_id: NSP-FEE-2026-04
gateway: NSP
doc_type: fee_schedule
version: 2026-04
effective_from: 2026-04-01
effective_to:
---

# NorthstarPay fee schedule (2026-04)

## Payment terms and worked example
Applies to NorthstarPay payments whose Hong Kong civil date is on or after 2026-04-01. There is no end date. Settlement currency is USD. Do not use NSP-FEE-2025-01 for these dates.

A Hong Kong civil date is `(occurred_at AT TIME ZONE 'Asia/Hong_Kong')::date`. 2026-03-31 16:30 UTC is 2026-04-01 00:30 in Hong Kong, so this document applies to that timestamp.

Payment: percent 2.60% (`percent_rate` 0.026000), fixed fee 0.30 USD, minimum fee 0.50 USD. FX markup for this version is 200 bps, not the old 150 bps. The conversion formula is in NSP-FX-2026-04. Markup is already inside `applied_fx_rate`. Do not add `fx_markup_amount` into `total_fee`.

Round half-up to 4 decimal places.

percent_fee = round_half_up(abs(settlement_gross) * 0.026000, 4)
total_fee = max(percent_fee + 0.30, 0.50) + attempt_fee
expected_net = settlement_gross - total_fee

NSP-VER-0002 is the same 100.00 EUR payment shape as NSP-FX-0001, with the same mid 1.08, but on 2026-04-02. NSP-FX-2026-04 converts it to settlement_gross 105.8400 USD. percent_fee = round_half_up(105.8400 * 0.026000, 4) = 2.7518. percent plus fixed = 3.0518, which is above the minimum, so total_fee = 3.0518 and expected_net = 102.7882 USD.

The percent rate is lower than 2025-01 (2.90%), but the merchant receives less than NSP-FX-0001 (102.9950 USD) because markup rose from 150 bps to 200 bps and the settlement gross fell.

## Refunds
A NorthstarPay refund in this version returns none of the original percent fee. Refund percent rate is 0. Fixed fee is 0.30 USD. Minimum fee is 0. `gross_amount` is negative. `total_fee` stays positive and is subtracted from `settlement_gross`.

## Failed payments
A failed NorthstarPay payment has settlement_gross 0, percent fee 0, fixed fee 0, and minimum fee 0. The failed-attempt fee in this version is 0.

---
doc_id: HFL-FX-2025-01
gateway: HFL
doc_type: fx_rules
version: 2025-01
effective_from: 2025-01-01
effective_to:
---

# HarborFlow FX rules (2025-01)

## When FX applies and the formula
Applies to HarborFlow transactions whose Hong Kong civil date is on or after 2025-01-01. There is no later HarborFlow FX version. FX applies when gross_currency is not HKD. Same-currency payments use mid_rate 1 and markup 0. HFL-PAY-0001 is 500.00 HKD settled in HKD, so its mid_rate is 1 and its markup is 0.

Markup is 80 bps. 100 bps = 1.00%, so 80 bps = 0.80%. Mid comes from fx_mid_rate_tb for that directed pair. Do not invert the pair.

applied_fx_rate = mid_rate * (1 - 80 / 10000)
settlement_gross = round_half_up(gross_amount * applied_fx_rate, 4)

The markup is already inside applied_fx_rate. Do not add fx_markup_amount into total_fee. Percent and the refund fixed fee are in HFL-FEE-2025-01.

## Failure
A failed HarborFlow payment has settlement_gross 0 and attempt fee 0. FX markup is not charged on top of a failure.

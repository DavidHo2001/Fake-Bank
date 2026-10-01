---
doc_id: NSP-FX-2026-04
gateway: NSP
doc_type: fx_rules
version: 2026-04
effective_from: 2026-04-01
effective_to:
---

# NorthstarPay FX rules (2026-04)

## When FX applies, the formula, and NSP-VER-0002
Applies when the Hong Kong civil date is on or after 2026-04-01. NSP-FX-2025-01 (150 bps, through 2026-03-31) does not apply. FX applies when gross_currency is not USD. Same-currency payments use mid_rate 1 and markup 0.

Markup is 200 bps. 100 bps = 1.00%, so 200 bps = 2.00%. Mid comes from fx_mid_rate_tb for that directed pair. Do not invert the pair.

applied_fx_rate = mid_rate * (1 - 200 / 10000)
settlement_gross = round_half_up(gross_amount * applied_fx_rate, 4)
fx_markup_amount = round_half_up(gross_amount * mid_rate, 4) - settlement_gross

The markup is already inside applied_fx_rate. Do not add fx_markup_amount into total_fee. Percent, fixed, and minimum fees are in NSP-FEE-2026-04.

NSP-VER-0002 is 100.00 EUR on 2026-04-02. mid EURUSD = 1.08000000. applied = 1.08 * 0.98 = 1.05840000. settlement_gross = 105.8400 USD. fx_markup_amount = 108.0000 - 105.8400 = 2.1600 USD, informational only. Fee math is in NSP-FEE-2026-04. expected_net on this trade is 102.7882 USD.

## Failure
A failed Northstar payment has settlement_gross 0 and attempt fee 0. FX markup is not charged on top of a failure.

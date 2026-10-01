---
doc_id: NSP-FX-2025-01
gateway: NSP
doc_type: fx_rules
version: 2025-01
effective_from: 2025-01-01
effective_to: 2026-03-31
---

# NorthstarPay FX rules (2025-01)

## When FX applies, the formula, and NSP-FX-0001
FX applies when gross_currency is not USD.
Same-currency payments use mid_rate 1 and markup 0.
Markup is 150 bps. 100 bps = 1.00%.
Mid comes from fx_mid_rate_tb for that directed pair.
applied_fx_rate = mid_rate * (1 - 150 / 10000)
settlement_gross = round_half_up(gross_amount * applied_fx_rate, 4)
The markup is already inside applied_fx_rate.
Do not add fx_markup_amount into total_fee.
Percent, fixed, and minimum fees are in NSP-FEE-2025-01.
100.00 EUR on 2026-03-15.
mid EURUSD = 1.08000000
applied = 1.06380000
settlement_gross = 106.3800 USD
fx_markup_amount = 1.6200 USD (informational)
Fee math is in the fee schedule. expected_net on this trade is 102.9950 USD.

## Failure
A failed Northstar payment has settlement_gross 0 and attempt fee 0.
---
doc_id: CDG-FX-2025-01
gateway: CDG
doc_type: fx_rules
version: 2025-01
effective_from: 2025-01-01
effective_to:
---

# CedarGate FX rules (2025-01)

## When FX applies and the formula
Applies to CedarGate payouts on or after 2025-01-01. There is no second CedarGate FX document. CDG-FEE-2026-06 changes the fixed fee from 2.00 USD to 3.50 USD and does not change this markup.

FX applies when gross_currency is not USD. Same-currency payouts use mid_rate 1 and markup 0. CDG-FEEHIKE-0001 and CDG-FEEHIKE-0002 are both 200.00 USD settled in USD, so markup does not explain why the later payout nets less.

Markup is 100 bps. 100 bps = 1.00%. Mid comes from fx_mid_rate_tb for that directed pair. Do not invert the pair.

applied_fx_rate = mid_rate * (1 - 100 / 10000)
settlement_gross = round_half_up(gross_amount * applied_fx_rate, 4)

The markup is already inside applied_fx_rate. Do not add fx_markup_amount into total_fee. Percent, fixed, and minimum fees are in the CedarGate fee schedule that is effective on the Hong Kong civil date.

## Failure
A failed CedarGate payout has settlement_gross 0. The 0.25 USD attempt fee comes from the fee schedule, not from this markup. FX markup is not added again on a failure.

-- Versioned commercial terms. This table is the numeric source of truth.
-- Markdown policy files must quote these same numbers. Do not invent a second rate card.
--
-- Lookup for a transaction, using the Hong Kong civil date of occurred_at:
--   txn_date = (occurred_at AT TIME ZONE 'Asia/Hong_Kong')::date
--   effective_from <= txn_date
--   AND (effective_to IS NULL OR effective_to >= txn_date)
--   AND gateway_id / txn_type match
-- Versions must not overlap. effective_to is inclusive.
--
-- fx_markup_bps: 100 bps = 1.00%. Applied only when gross_currency <> settlement_currency.
-- Markup is inside the FX rate. It is not added again on top of percent_fee.

CREATE TABLE IF NOT EXISTS fee_schedule_tb (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gateway_id BIGINT NOT NULL REFERENCES payment_gateway_tb (id),
    version_code TEXT NOT NULL,
    txn_type TEXT NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE,
    settlement_currency CHAR(3) NOT NULL,
    percent_rate NUMERIC(9, 6) NOT NULL,
    fixed_fee NUMERIC(19, 4) NOT NULL,
    min_fee NUMERIC(19, 4) NOT NULL,
    fx_markup_bps INTEGER NOT NULL,
    failed_attempt_fee NUMERIC(19, 4) NOT NULL,
    refund_returns_percent_fee BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fee_schedule_version_txn_uq UNIQUE (gateway_id, version_code, txn_type),
    CONSTRAINT fee_schedule_dates_chk CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT fee_schedule_percent_chk CHECK (percent_rate >= 0 AND percent_rate < 1),
    CONSTRAINT fee_schedule_money_chk CHECK (
        fixed_fee >= 0 AND min_fee >= 0 AND failed_attempt_fee >= 0
    ),
    CONSTRAINT fee_schedule_bps_chk CHECK (fx_markup_bps BETWEEN 0 AND 1000),
    CONSTRAINT fee_schedule_type_chk CHECK (txn_type IN ('payment', 'refund', 'payout')),
    CONSTRAINT fee_schedule_ccy_chk CHECK (settlement_currency ~ '^[A-Z]{3}$')
);

CREATE INDEX IF NOT EXISTS fee_schedule_lookup_idx
    ON fee_schedule_tb (gateway_id, txn_type, effective_from);

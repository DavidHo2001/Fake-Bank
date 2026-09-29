-- Money is NUMERIC, never float.
-- Amounts are signed from the merchant's point of view. Refund gross_amount is negative.
-- Fees are always >= 0.
--
-- Success:
--   applied_fx_rate = mid_rate * (1 - fx_markup_bps / 10000)
--   settlement_gross = round_half_up(gross_amount * applied_fx_rate, 4)
--   percent_fee = round_half_up(abs(settlement_gross) * percent_rate, 4)
--   total_fee = greatest(percent_fee + fixed_fee, min_fee) + attempt_fee
--   expected_net = settlement_gross - total_fee
-- Same currency: mid_rate = 1, fx_markup_bps = 0, fx_markup_amount = 0.
-- fx_markup_amount is informational (mid conversion minus applied conversion).
-- It is already removed by applied_fx_rate. Do not add it into total_fee.
--
-- Failure:
--   settlement_gross = 0
--   percent_fee = 0, fixed_fee = 0, min_fee = 0
--   attempt_fee = fee_schedule_tb.failed_attempt_fee
--   expected_net = -attempt_fee
--
-- Schedule lookup uses Asia/Hong_Kong civil date. Storage stays timestamptz UTC.
-- percent_rate / fees on this row are the snapshot used for that transaction.
-- fee_schedule_id points at the policy version. Later edits to the schedule must not rewrite history.

CREATE TABLE IF NOT EXISTS transaction_tb (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    txn_ref TEXT NOT NULL UNIQUE,
    gateway_id BIGINT NOT NULL REFERENCES payment_gateway_tb (id),
    fee_schedule_id BIGINT NOT NULL REFERENCES fee_schedule_tb (id),
    owner_user_id BIGINT NOT NULL REFERENCES user_tb (id),
    parent_txn_id BIGINT REFERENCES transaction_tb (id),
    settlement_id BIGINT REFERENCES gateway_settlement_tb (id),
    txn_type TEXT NOT NULL,
    status TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    gross_amount NUMERIC(19, 4) NOT NULL,
    gross_currency CHAR(3) NOT NULL,
    settlement_currency CHAR(3) NOT NULL,
    settlement_gross NUMERIC(19, 4) NOT NULL,
    mid_rate NUMERIC(18, 8) NOT NULL,
    fx_markup_bps INTEGER NOT NULL,
    applied_fx_rate NUMERIC(18, 8) NOT NULL,
    fx_markup_amount NUMERIC(19, 4) NOT NULL,
    percent_rate NUMERIC(9, 6) NOT NULL,
    percent_fee NUMERIC(19, 4) NOT NULL,
    fixed_fee NUMERIC(19, 4) NOT NULL,
    min_fee NUMERIC(19, 4) NOT NULL,
    attempt_fee NUMERIC(19, 4) NOT NULL DEFAULT 0,
    min_fee_applied BOOLEAN NOT NULL,
    total_fee NUMERIC(19, 4) NOT NULL,
    expected_net NUMERIC(19, 4) NOT NULL,
    settled_amount NUMERIC(19, 4),
    variance_amount NUMERIC(19, 4) GENERATED ALWAYS AS (settled_amount - expected_net) STORED,
    mismatch_flag BOOLEAN GENERATED ALWAYS AS (
        settled_amount IS NOT NULL AND settled_amount IS DISTINCT FROM expected_net
    ) STORED,
    mismatch_code TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT transaction_type_chk CHECK (txn_type IN ('payment', 'refund', 'payout')),
    CONSTRAINT transaction_status_chk CHECK (status IN ('pending', 'settled', 'failed')),
    CONSTRAINT transaction_ccy_chk CHECK (
        gross_currency ~ '^[A-Z]{3}$' AND settlement_currency ~ '^[A-Z]{3}$'
    ),
    CONSTRAINT transaction_gross_nonzero_chk CHECK (gross_amount <> 0),
    CONSTRAINT transaction_refund_parent_chk CHECK (
        (txn_type = 'refund' AND parent_txn_id IS NOT NULL)
        OR (txn_type <> 'refund' AND parent_txn_id IS NULL)
    ),
    CONSTRAINT transaction_money_nonneg_chk CHECK (
        percent_fee >= 0
        AND fixed_fee >= 0
        AND min_fee >= 0
        AND attempt_fee >= 0
        AND total_fee >= 0
        AND fx_markup_amount >= 0
        AND percent_rate >= 0
        AND fx_markup_bps >= 0
        AND mid_rate > 0
        AND applied_fx_rate > 0
    ),
    CONSTRAINT transaction_total_fee_chk CHECK (
        total_fee = GREATEST(percent_fee + fixed_fee, min_fee) + attempt_fee
    ),
    CONSTRAINT transaction_expected_net_chk CHECK (
        expected_net = settlement_gross - total_fee
    ),
    CONSTRAINT transaction_min_flag_chk CHECK (
        min_fee_applied = ((percent_fee + fixed_fee) < min_fee)
    ),
    CONSTRAINT transaction_same_ccy_chk CHECK (
        status = 'failed'
        OR gross_currency <> settlement_currency
        OR (
            mid_rate = 1
            AND applied_fx_rate = 1
            AND fx_markup_bps = 0
            AND fx_markup_amount = 0
            AND settlement_gross = gross_amount
        )
    ),
    CONSTRAINT transaction_mismatch_code_chk CHECK (
        mismatch_code IS NULL
        OR mismatch_code IN ('short_pay', 'fee_drift', 'fx_rate_drift')
    ),
    CONSTRAINT transaction_mismatch_pair_chk CHECK (
        (settled_amount IS NULL AND mismatch_code IS NULL)
        OR (
            settled_amount IS NOT NULL
            AND settled_amount = expected_net
            AND mismatch_code IS NULL
        )
        OR (
            settled_amount IS NOT NULL
            AND settled_amount <> expected_net
            AND mismatch_code IS NOT NULL
        )
    )
);

CREATE INDEX IF NOT EXISTS transaction_owner_time_idx
    ON transaction_tb (owner_user_id, occurred_at DESC);

CREATE INDEX IF NOT EXISTS transaction_gateway_time_idx
    ON transaction_tb (gateway_id, occurred_at DESC);

CREATE INDEX IF NOT EXISTS transaction_mismatch_idx
    ON transaction_tb (gateway_id, occurred_at)
    WHERE mismatch_flag;

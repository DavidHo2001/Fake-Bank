-- Optional batch that groups settled transactions. Golden seed rows leave settlement_id null.
-- The generator may attach a monthly batch after transactions exist.

CREATE TABLE IF NOT EXISTS gateway_settlement_tb (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gateway_id BIGINT NOT NULL REFERENCES payment_gateway_tb (id),
    settlement_ref TEXT NOT NULL UNIQUE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    currency CHAR(3) NOT NULL,
    settled_amount NUMERIC(19, 4) NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT gateway_settlement_period_chk CHECK (period_end >= period_start),
    CONSTRAINT gateway_settlement_ccy_chk CHECK (currency ~ '^[A-Z]{3}$'),
    CONSTRAINT gateway_settlement_status_chk CHECK (status IN ('open', 'paid'))
);

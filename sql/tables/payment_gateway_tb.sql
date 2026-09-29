-- Fictional acquirers. settlement_currency is the currency the gateway pays the merchant in.
-- Fixed fees on fee_schedule_tb are denominated in this currency.

CREATE TABLE IF NOT EXISTS payment_gateway_tb (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    settlement_currency CHAR(3) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT payment_gateway_code_chk CHECK (code ~ '^[A-Z0-9]{2,12}$'),
    CONSTRAINT payment_gateway_ccy_chk CHECK (settlement_currency ~ '^[A-Z]{3}$')
);

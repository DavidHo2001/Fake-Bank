-- Demo mid-market card. One directed pair: 1 base_currency = mid_rate quote_currency.
-- The generator looks up the row; it does not invert or triangulate.
-- Same-currency transactions do not use this table. Their mid_rate is 1.
--
--   SELECT mid_rate
--   FROM fx_mid_rate_tb
--   WHERE base_currency = :gross_currency
--     AND quote_currency = :settlement_currency
--     AND as_of_date <= :txn_hk_date
--   ORDER BY as_of_date DESC
--   LIMIT 1;

CREATE TABLE IF NOT EXISTS fx_mid_rate_tb (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    base_currency CHAR(3) NOT NULL,
    quote_currency CHAR(3) NOT NULL,
    as_of_date DATE NOT NULL,
    mid_rate NUMERIC(18, 8) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fx_mid_rate_pair_uq UNIQUE (base_currency, quote_currency, as_of_date),
    CONSTRAINT fx_mid_rate_ccy_chk CHECK (
        base_currency ~ '^[A-Z]{3}$'
        AND quote_currency ~ '^[A-Z]{3}$'
        AND base_currency <> quote_currency
    ),
    CONSTRAINT fx_mid_rate_positive_chk CHECK (mid_rate > 0)
);

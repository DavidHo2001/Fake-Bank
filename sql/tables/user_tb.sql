-- Local demo accounts only. Passwords are hashed in sql/seed/01_reference_seed.sql.
-- role is the authorization source. A JWT may carry role, but every query re-checks this table.

CREATE TABLE IF NOT EXISTS user_tb (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email CITEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT user_role_chk CHECK (role IN ('admin', 'user')),
    CONSTRAINT user_password_hash_chk CHECK (char_length(password_hash) >= 50)
);

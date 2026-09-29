-- Run first. PostgreSQL contrib extensions used by the schema and seed.
-- pgvector is intentionally not enabled here. Add it in the embedding step,
-- after an embedding model and vector dimension are chosen.

CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

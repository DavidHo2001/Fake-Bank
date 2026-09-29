-- Catalog of policy files the RAG pipeline will ingest.
-- Rows here do not contain the policy text. You write that as Markdown under docs/source/.
-- document_chunk_tb is filled by the ingestion program, not by the seed.
-- Add embedding vector(N) only after the embedding model is chosen.

CREATE TABLE IF NOT EXISTS document_tb (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    doc_code TEXT NOT NULL UNIQUE,
    gateway_id BIGINT REFERENCES payment_gateway_tb (id),
    doc_type TEXT NOT NULL,
    version_code TEXT NOT NULL,
    title TEXT NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE,
    source_path TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT document_type_chk CHECK (
        doc_type IN ('fee_schedule', 'fx_rules', 'reconciliation_sop')
    ),
    CONSTRAINT document_dates_chk CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT document_gateway_chk CHECK (
        (doc_type = 'reconciliation_sop' AND gateway_id IS NULL)
        OR (doc_type <> 'reconciliation_sop' AND gateway_id IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS document_chunk_tb (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES document_tb (id),
    chunk_index INTEGER NOT NULL,
    section_path TEXT NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER,
    content_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT document_chunk_index_uq UNIQUE (document_id, chunk_index),
    CONSTRAINT document_chunk_hash_uq UNIQUE (document_id, content_hash),
    CONSTRAINT document_chunk_index_chk CHECK (chunk_index >= 0)
);

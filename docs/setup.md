# Setup

Local setup for David Bank. Backend commands run from `backend/`.

## Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env`. Fill `DATABASE_URL`, `JWT_SECRET`, and `OPENROUTER_API_KEY`.

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

## Frontend

From `frontend/`:

```bash
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://localhost:8000`.

## Database

**0. Import every model in `backend/alembic/env.py`**

Alembic only sees imported classes. A missing new model is skipped. A missing old model becomes `drop_table`.

```python
from app.models.transaction import Transaction  # noqa: F401
```

**1. Generate a migration from the SQLAlchemy models**

PostgreSQL extensions need to be added manually.

```bash
alembic revision --autogenerate -m "describe the schema change"
```

**1.1 Add these below `def upgrade`:**

```python
def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # op.create_table(...) ...
```

**2. Apply migrations**

```bash
alembic upgrade head
```

**3. Check the applied revision**

```bash
alembic current
```

**4. An already applied migration file is not run again**

Run the new SQL yourself, or generate another migration and upgrade:

```bash
alembic revision --autogenerate -m "describe the schema change"
alembic upgrade head
```

**5. Seed reference data**

Connect with `psql` and run `sql/seed/01_reference_seed.sql`.

**6. Generate about 150 extra transactions**

Uses `fee_schedule_tb` and `fx_mid_rate_tb`. Does not change the 10 golden rows. Re-run deletes `%-GEN-%` and `NSP-BOUNDARY-0001`, then inserts the same rows again (`random.seed(42)`).

```bash
cd backend && source .venv/bin/activate && python ../scripts/generate_data.py
```

**7. Ingest Markdown into chunks**

Does not call an LLM. Reads each `document_tb.source_path`, splits on `##`, and replaces that document's rows in `document_chunk_tb`. Embeddings are a separate step (`scripts/embedding.py`).

```bash
cd backend && source .venv/bin/activate && python ../scripts/ingest_docs.py
```

# Fake-Bank

backend:
0. python3 -m venv .venv
1. source .venv/bin/activate
2. python -m pip install -r requirements.txt
3. copy .env.example as .env, fill DATABASE_URL and JWT_SECRET
4. alembic upgrade head
5. uvicorn app.main:app --reload

frontend:
npm install
npm run dev

DB:

**0. Import every model in `backend/alembic/env.py`**

Alembic only sees imported classes. A missing new model is skipped. A missing old model becomes `drop_table`.

e.g.

```python
from app.models.transaction import Transaction  # noqa: F401
```

**1. According to SQLAlchemy models, generate a Python migration file**

PostgreSQL extensions need to be added manually.

```bash
alembic revision --autogenerate -m "migration file title as u like"
```

**1.1 Add these below `def upgrade`:**

```python
def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # op.create_table(...) ...
```

**2. Update DB to latest migration** (e.g. `8948f9481278_create_user_tb.py`)

```bash
alembic upgrade head
```

**3. Check current applied migration version**

```bash
alembic current
```

**4. A change in an already upgraded migration will not be re-run**

You need to manually execute the query in the DB.

**OR generate another migration and upgrade it**

```bash
alembic revision --autogenerate -m "a new migration"
```

**5. Connect to the PostgreSQL DB and run seed**

```sql
sql/seed/01_reference_seed.sql
```

**6. Generate about 150 extra transactions**

Uses `fee_schedule_tb` and `fx_mid_rate_tb`. Does not change the 10 golden rows. Re-run deletes `%-GEN-%` and `NSP-BOUNDARY-0001`, then inserts the same rows again (`random.seed(42)`).

```bash
cd backend && source .venv/bin/activate && python ../scripts/generate_data.py
```

**7. Ingest Markdown into chunks. Do not call an LLM.**

Reads each `document_tb.source_path`, splits on `##`, and replaces that document's rows in `document_chunk_tb`.

```bash
cd backend && source .venv/bin/activate && python ../scripts/ingest_docs.py
```

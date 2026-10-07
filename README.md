# David Bank

A merchant asks why a payout is short. The API answers from that merchant's transactions and the fee document in force on that date, and says when the evidence is not enough.

Fictional gateways only: NorthstarPay, HarborFlow, CedarGate. No live card data.

![Fee enquiry](https://github.com/user-attachments/assets/ee627704-299d-449d-8115-19080b40f10d)

## How an answer is built

`POST /api/v1/documents/answer`

1. Read transaction references and dates from the question. A date in the question wins. Otherwise the API uses `effective_at`, then each transaction's Hong Kong civil date, then today.
2. Load transactions in SQL. A merchant sees only their own rows. One reference that is missing or belongs to someone else rejects the whole question.
3. Search fee-schedule chunks in pgvector, limited to that transaction's gateway, fee version, and effective date.
4. Send those rows, the gateway settlement currencies, and the chunks to the model. The prompt treats them as evidence. The answer cites `doc_code` and `section_path`.

The model does not run SQL and does not choose which rows to read.

## What the cases check

53 manual cases, 0 fail, run on 7 October 2026 against `qwen/qwen3.8-flash`. Figures are recomputed from the seed, not from the model. Full record: [docs/qa](docs/qa/QA-ANS-001-fee-enquiry-test-cases.md).

| Case | Check | Result |
|---|---|---|
| CedarGate fee hike | `CDG-FEEHIKE-0002` costs more because the fixed fee rose from 2.00 USD to 3.50 USD. Totals 3.0000 and 4.5000. | Pass |
| Two NorthstarPay versions | `NSP-VER-0002` net 102.7882 USD versus `NSP-FX-0001` net 102.9950 USD. Markup 200 bps versus 150 bps. | Pass |
| Another merchant's rows | North asks about East's CedarGate pair. | HTTP 400. No fee figures. |
| Incomplete reference | `NSP-FX-001` is too short. The answer asks for the full reference and does not state 3.3850. | Pass |
| Unsupported currency | Bitcoin settlement. | Cannot confirm. HarborFlow stays HKD. |
| Embedded instruction | A simplified-Chinese order to ignore the rules. | Traditional Chinese. Bitcoin stays unconfirmed. |

## Try this

Log in as East Merchant and ask why `CDG-FEEHIKE-0002` cost more than `CDG-FEEHIKE-0001`. The two payments sit on different fee-schedule versions.

North Merchant can ask the same style of question about `NSP-VER-0002` and `NSP-FX-0001`. East cannot see those references.

| Email | Password | Role |
|---|---|---|
| `merchant.east@fakebank.local` | `LocalEast#2026` | user |
| `merchant.north@fakebank.local` | `LocalNorth#2026` | user |
| `admin@fakebank.local` | `LocalAdmin#2026` | admin |

Local demo passwords. Do not reuse them.

## Run

[Setup](docs/setup.md)

- UI: http://localhost:5173
- API docs: http://localhost:8000/docs

Fee-enquiry cases are in [docs/qa](docs/qa/QA-ANS-001-fee-enquiry-test-cases.md). Access checks:

```bash
cd backend && source .venv/bin/activate && pytest ../docs/qa/test_access.py
```

## Stack

FastAPI, SQLAlchemy, Alembic, PostgreSQL, pgvector. JWT in the `Authorization` header. The role is read from the database on each request. Embeddings use `paraphrase-multilingual-MiniLM-L12-v2`. The answer call goes through OpenRouter. The UI is React, Vite, and MUI.

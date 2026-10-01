# David Bank — list APIs and first UI

Locked before implementation. List screens show business fields. Surrogate primary keys and foreign keys stay in the database and in the JWT `sub` claim. They are not list-response fields.

## Envelope

Every `/api/v1` JSON body uses one shape:

```json
{ "status": "success", "data": {} }
{ "status": "error", "data": { "message": "..." } }
```

`status` is the string `success` or `error`. The HTTP status code stays the real protocol status (200, 400, 401, 403, 422).

`GET /health` stays `{ "status": "ok" }`. It is not a business API.

A page sits inside `data`. The row list is `items`, so the JSON is not `data.data`.

```json
{
  "status": "success",
  "data": { "items": [], "total": 0, "page": 1, "page_size": 20 }
}
```

`page` is 1-based. `page_size` default 20, min 1, max 100.

## Who can call what

All list routes require `Authorization: Bearer <jwt>`.

| Route | Caller |
|---|---|
| `POST /api/v1/auth/login` | public |
| `GET /api/v1/users/me` | logged-in user |
| `GET /api/v1/users` | admin only, else 403 |
| `GET /api/v1/fee-schedules` | any logged-in user |
| `GET /api/v1/documents` | any logged-in user |
| `GET /api/v1/transactions` | any logged-in user, rows scoped below |

Role is read from `user_tb` on each request. The JWT only carries `sub`.

## List fields

Joins replace foreign keys with names or business refs. Nullable foreign keys use an outer join.

**Fee schedule:** `gateway_name`, `version_code`, `txn_type`, `effective_from`, `effective_to`, `settlement_currency`, `percent_rate`, `fixed_fee`, `min_fee`, `fx_markup_bps`, `failed_attempt_fee`, `refund_returns_percent_fee`, `created_at`.

**Document:** `doc_code`, `gateway_name` (null for a reconciliation SOP), `doc_type`, `version_code`, `title`, `effective_from`, `effective_to`, `source_path`, `created_at`. Chunks are not part of this API.

**User (admin list):** `email`, `display_name`, `role`, `is_active`, `created_at`. Never `password_hash`.

**Transaction:** `txn_ref`, `gateway_name`, `fee_version_code`, `owner_display_name`, `parent_txn_ref`, `settlement_ref`, `txn_type`, `status`, `occurred_at`, `gross_amount`, `gross_currency`, `settlement_currency`, `settlement_gross`, `total_fee`, `expected_net`, `settled_amount`, `variance_amount`, `mismatch_flag`, `mismatch_code`.

`parent_txn_ref` and `settlement_ref` are null when the foreign key is null.

Login and `GET /users/me` return `email`, `display_name`, `role`. The user id stays on the server principal (`CurrentUser`) so transaction filtering can use it. The UI does not render it.

## Transactions

`owner_user_id` is applied in SQL.

- role `user`: `WHERE owner_user_id = current user id`
- role `admin`: no owner filter

A user cannot pass another user id to widen the query.

Date filter is optional. Query params `occurred_from` and `occurred_to` are civil dates. Omitted means no bound. Both omitted is the default and returns the whole allowed set (still paged).

A date is an Asia/Hong_Kong civil day. `occurred_from` is inclusive at 00:00 HK. `occurred_to` is inclusive through the end of that HK day (`occurred_at < next HK midnight`). Storage stays `timestamptz`. If both dates are set and `occurred_from > occurred_to`, respond 400.

Sort: `occurred_at DESC`, then `id DESC`.

The count query uses the same owner and date filters, without `LIMIT`.

## Code shape

Same layers as fee schedules: repository builds the SQL, service copies fields into the DTO, router is thin and wraps `GenericResponse`.

## Frontend

Add Axios, MUI, and React Router. Vite proxies `/api` to `http://localhost:8000`.

Axios `baseURL` is `/api/v1`. A request interceptor sets `Authorization: Bearer <token>` from the saved session. A 401 on a request that sent a token clears the session and sends the browser to `/`.

Session stores the token plus `display_name`, `email`, and `role` from `data.user_dto`.

| Path | Screen |
|---|---|
| `/` | Login box only. No menu. Already logged in goes to `/home`. |
| `/home` | Short description of David Bank |
| `/fee-schedules` | Paged table |
| `/transactions` | Paged table plus optional date range |

Logged-in shell, top bar, left to right:

1. Home control: `DavidBank.png`, links to `/home`
2. Fee Schedule
3. Transaction
4. Profile icon + `display_name`
5. Logout icon button

Document and user list APIs have no menu item in this pass.

Home copy: David Bank is a demo merchant bank. It shows how a payment gateway prices a charge — percent fee, fixed fee, minimum fee, FX markup — and where the expected net differs from the settled amount.

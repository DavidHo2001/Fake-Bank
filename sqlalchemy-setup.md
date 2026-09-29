# Auth 先：SQLAlchemy ORM + JWT + GET current user

Neon 已經連到。庫仍然係空。下一步唔係跑完整 seed，亦唔係先寫 login。

Auth 要讀 `user_tb`。表未存在，login 冇位查。約 5,000 筆交易、gateway、費率，login 用唔到。

而家只做呢條線：

```text
User model（對住 sql/tables/user_tb.sql）
        ↓
Alembic migration：只建 user_tb
        ↓
alembic upgrade head
        ↓
ORM seed 3 個 demo user
        ↓
POST /api/v1/auth/login
        ↓
GET  /api/v1/users/me
```

`sql/seed/01_reference_seed.sql` 同 `scripts/generate_data.py` 留到交易表都經 Alembic 建好之後。

所有指令喺 `backend/` 跑，虛擬環境要開住。`DATABASE_URL` 已經喺 `backend/.env`。

```bash
cd backend
source .venv/bin/activate
```

---

## 你識嘅 SQL，對住 ORM

ORM 仍然出 SQL。分別係：表同查詢寫成 Python class，參數由 SQLAlchemy bind。唔好再用 f-string 砌 SQL。

| 你慣 | 呢度 |
|---|---|
| connection string | `Engine`（`app/db/session.py` 已有，連線池） |
| 一次請求一個 transaction | `Session`。`get_db()` 開，請求完關 |
| `CREATE TABLE user_tb` | `class User`。建表仍然靠 Alembic，唔好 `create_all()` |
| `SELECT * FROM user_tb WHERE email = $1` | `db.scalar(select(User).where(User.email == email))` |
| `SELECT * FROM user_tb WHERE id = $1` | `db.get(User, user_id)` |
| `INSERT` 然後 `COMMIT` | `db.add(user)` 然後 `db.commit()` |
| stored procedure 參數 | `where(...)` 入面嘅 Python 值。驅動自己變成 `$1` |
| 一個 result row | 一個 `User` object。`user.email` 即係嗰欄 |
| `password_hash` 只放 DB | response schema 唔包含呢個欄 |

`app/db/base.py` 而家啱，保留 `DeclarativeBase`。所有 model 繼承 `Base`，Alembic 先睇到表。

`app/db/session.py` 都唔使改。每個 request：

```text
get_db() → 開 Session → route 用佢查 / 寫 → 冇 exception 就 commit → 關 Session
```

Login 只讀，唔使自己 `commit()`。Seed script 係寫入，要自己 `commit()`。

---

## Step 1 — 裝 JWT 同 bcrypt

```bash
python -m pip install pyjwt bcrypt
python -m pip freeze | grep -E '^(PyJWT|bcrypt)=='
```

將 freeze 出嚟嗰兩行加落 `backend/requirements.txt`。

Hash 喺 Python 計，唔經 Postgres `pgcrypto`。Login 用 `bcrypt.checkpw`。bcrypt 字串長 60，過到 `user_tb` 嘅 `char_length(password_hash) >= 50`。

---

## Step 2 — `.env` 加簽名密鑰

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

`backend/.env` 加一行（值用上面印出嚟嗰串，唔好 commit）：

```text
JWT_SECRET=貼上剛才嗰串
```

`backend/.env.example` 只加鍵名同假值：

```text
JWT_SECRET=change-me
```

`backend/app/core/config.py` 改成：

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
```

Pydantic 會把 `JWT_SECRET` 讀入 `jwt_secret`。未設呢個鍵，import `app` 會直接失敗。

---

## Step 3 — User model

對住 `sql/tables/user_tb.sql` 逐欄寫。Python class 係之後所有查詢嘅表。Alembic 負責真正 `CREATE TABLE`。兩邊要一致。

新檔 `backend/app/models/__init__.py`：

```python
from app.models.user import User

__all__ = ["User"]
```

新檔 `backend/app/models/user.py`：

```python
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, Identity, Text, func
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "user_tb"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    email: Mapped[str] = mapped_column(CITEXT, unique=True)
    display_name: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text)
    password_hash: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'user')", name="user_role_chk"),
        CheckConstraint(
            "char_length(password_hash) >= 50",
            name="user_password_hash_chk",
        ),
    )
```

欄位對照：

| SQL | Model |
|---|---|
| `BIGINT GENERATED ALWAYS AS IDENTITY` | `BigInteger` + `Identity(always=True)` |
| `CITEXT` email | `CITEXT`。大細階當同一個 email |
| `TIMESTAMPTZ DEFAULT now()` | `DateTime(timezone=True)` + `server_default=func.now()` |
| `CHECK (role IN ...)` | `CheckConstraint`，constraint 名保持 `user_role_chk` |

`DateTime(timezone=True)` 先至係 `TIMESTAMPTZ`。只寫 `Mapped[datetime]` 會變成冇時區嘅 `TIMESTAMP`。

`password_hash` 永遠唔好出現喺 API response。

---

## Step 4 — Alembic 只建 `user_tb`

Repo 未有 `backend/alembic/`。而家先 init。

```bash
alembic init alembic
```

### 4.1 `alembic/env.py`

檔案開頭 import 區加上。令 migration 用 `.env` 嘅 URL，同 autogenerate 睇到 `User`：

```python
from app.core.config import settings
from app.db.base import Base
from app.models.user import User  # noqa: F401

config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))
target_metadata = Base.metadata
```

`alembic init` 原本有 `target_metadata = None`，換成上面最後一行。`replace("%", "%%")` 係因為 Neon 密碼 url-encode 之後含 `%`，Alembic 嘅 config 會當佢係插值。

`User` 嘅 import 唔好刪。冇呢行，之後 autogenerate 會當個表唔存在。

Online 那段保持 `alembic init` 嘅樣：`connectable = engine_from_config(...)` 會用你剛 set 嘅 URL。

### 4.2 手寫第一個 migration

第一張表用手寫，唔好 `--autogenerate`。`CITEXT` extension、`IDENTITY`、兩條 `CHECK` 嘅名，autogenerate 容易同 `user_tb.sql` 唔一致。

```bash
alembic revision -m "create user_tb"
```

打開 `alembic/versions/` 入面新檔，換成：

```python
"""create user_tb

Revision ID: <留返檔案自己生成嗰個>
Revises:
Create Date: <留返檔案自己生成嗰個>
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "<同檔案原值>"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.create_table(
        "user_tb",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            primary_key=True,
        ),
        sa.Column("email", postgresql.CITEXT(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("role IN ('admin', 'user')", name="user_role_chk"),
        sa.CheckConstraint(
            "char_length(password_hash) >= 50",
            name="user_password_hash_chk",
        ),
        sa.UniqueConstraint("email", name="user_tb_email_key"),
    )


def downgrade() -> None:
    op.drop_table("user_tb")
```

`revision` / `down_revision` 用 `alembic revision` 生成嗰份，唔好自己作。

呢個 migration 只做 `citext` + `user_tb`。唔好喺度開 `vector`，亦唔好建 gateway / transaction。

### 4.3 升級

Neon 上面如果未跑過 `sql/tables/user_tb.sql`：

```bash
alembic upgrade head
```

如果之前已經用 psql 建過 `user_tb`，`upgrade` 會因為表已存在而失敗。嗰種情況先核對欄位同 `user_tb.sql` 一樣，然後：

```bash
alembic stamp head
```

`stamp` 只係話俾 Alembic 聽「呢個版本已經喺庫度」，唔會再 `CREATE TABLE`。

完成檢查：

```bash
alembic current
```

要見到 `(head)`。

---

## Step 5 — 用 ORM seed 3 個 user

新檔 `backend/scripts/seed_users.py`。只 insert user。同 `01_reference_seed.sql` 嘅三個 demo 帳號一樣，方便之後交易 seed 用同一批 email。

```python
import bcrypt
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User

# Local demo only. Same accounts as sql/seed/01_reference_seed.sql.
USERS = [
    ("admin@fakebank.local", "Local Admin", "admin", "LocalAdmin#2026"),
    ("merchant.north@fakebank.local", "North Merchant", "user", "LocalNorth#2026"),
    ("merchant.east@fakebank.local", "East Merchant", "user", "LocalEast#2026"),
]


def hash_password(raw: str) -> str:
    digest = bcrypt.hashpw(raw.encode(), bcrypt.gensalt(rounds=12))
    return digest.decode()


def main() -> None:
    with SessionLocal() as db:
        for email, display_name, role, password in USERS:
            existing = db.scalar(select(User).where(User.email == email))
            if existing is not None:
                continue
            db.add(
                User(
                    email=email,
                    display_name=display_name,
                    role=role,
                    password_hash=hash_password(password),
                    is_active=True,
                )
            )
        db.commit()


if __name__ == "__main__":
    main()
```

對住你識嘅 SQL，上面個 loop 即係：

```sql
SELECT * FROM user_tb WHERE email = $1;

-- 冇 row 先：
INSERT INTO user_tb (email, display_name, role, password_hash, is_active)
VALUES ($1, $2, $3, $4, true);

COMMIT;
```

再跑一次唔會插重複，因為 email 已存在就 `continue`。同 seed 檔入面 `ON CONFLICT (email) DO NOTHING` 同一個效果。

```bash
python scripts/seed_users.py
```

`scripts/` 唔喺 package 入面，所以要喺 `backend/` 跑，Python 先搵到 `app`。

完成檢查（`psql` 用冇 `+psycopg` 嗰條 URL）：

```sql
SELECT id, email, role, is_active, char_length(password_hash) AS hash_len
FROM user_tb
ORDER BY id;
```

3 行。`hash_len` = 60。`password_hash` 以 `$2b$` 開頭。

---

## Step 6 — Login

JWT 只放兩樣：`sub` = user id（字串），`exp` = 15 分鐘。角色唔放 token。每次要身份嘅 route 解 `sub`，再查 `user_tb`。`role` 同 `is_active` 以資料庫嗰刻為準。

新檔 `backend/app/core/security.py`：

```python
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 15


def verify_password(plain: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain.encode(), password_hash.encode())


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)
```

新檔 `backend/app/schemas/user.py`：

```python
from pydantic import BaseModel, ConfigDict


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    display_name: str
    role: str
    is_active: bool
```

`from_attributes = True` 讓你直接 `UserPublic.model_validate(user)`。class 上面冇 `password_hash`，response 就唔會帶出 hash。

新檔 `backend/app/schemas/auth.py`：

```python
from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

新檔 `backend/app/api/deps.py`：

```python
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import ALGORITHM
from app.db.session import get_db
from app.models.user import User

bearer = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return user
```

`db.get(User, user_id)` 即係 `SELECT ... FROM user_tb WHERE id = $1`。主鍵查詢用呢個，唔使自己寫 `where`。

新檔 `backend/app/api/auth.py`：

```python
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == body.email))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return TokenResponse(access_token=create_access_token(user.id))
```

Email 唔存在、用戶停用、密碼錯，都回同一句 `401`。Log 唔好寫 `body.password`。

`backend/app/main.py` 掛上 auth router：

```python
from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.db_demo import router as db_demo_router
from app.api.users import router as users_router

app = FastAPI(title="My API")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(db_demo_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
```

---

## Step 7 — GET current user

`backend/app/api/users.py` 而家返回硬編碼 `Alex`。換成讀 token 對應嗰行。

```python
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
def read_me(current: Annotated[User, Depends(get_current_user)]) -> User:
    return current
```

`response_model=UserPublic` 會再濾一次。就算有人 `return current`，JSON 都冇 `password_hash`。

路徑係 `GET /api/v1/users/me`。

---

## Step 8 — 完成檢查

開第二個終端，backend 目錄、venv 開住：

```bash
uvicorn app.main:app --reload
```

登入 north：

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H 'content-type: application/json' \
  -d '{"email":"merchant.north@fakebank.local","password":"LocalNorth#2026"}'
```

要見到 `access_token`。用呢粒 token：

```bash
curl -s http://127.0.0.1:8000/api/v1/users/me \
  -H "authorization: Bearer 貼上access_token"
```

要見到 north 嘅 `id`、`email`、`display_name`、`role=user`、`is_active=true`。JSON 冇 `password_hash`。

再試三樣，都應該 `401`：

- 錯密碼
- 冇 `Authorization` header 就 call `/users/me`
- token 亂改一個字

Admin 同一條 login。`admin@fakebank.local` / `LocalAdmin#2026`，`/users/me` 嘅 `role` 係 `admin`。

FastAPI `/docs` 可以試。`Authorize` 撳入 `Bearer <token>`，再 call `GET /users/me`。

---

## 而家未做

| 之後 | 原因 |
|---|---|
| `01_reference_seed.sql` 其餘 INSERT | gateway、fee、10 筆 golden txn 要對應表先存在 |
| 約 5,000 筆 `generate_data.py` | 同上。`owner_user_id` 會指住你剛 seed 嘅 user |
| 交易查詢加 `WHERE owner_user_id = current.id` | user 先做到。admin 先唔加呢句 |
| 其餘表嘅 Alembic revision | 一張表一個 migration，對住 `sql/tables/*.sql` |
| RAG / LLM | 未有文件 chunk 之前唔接 |

下一個 model 先寫 `payment_gateway_tb`，做法同 `User` 一樣：class 對住 SQL 檔，然後一個新 revision。有 FK 先至用 `relationship`。而家 user 冇子表要載入，唔使 relationship。

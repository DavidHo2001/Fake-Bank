from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 60*9 #9hours
jwt_secret = settings.jwt_secret


def verify_password(plain: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain.encode(), password_hash.encode())


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, jwt_secret, algorithm=ALGORITHM)
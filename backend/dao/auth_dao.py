"""认证数据访问层 — JWT 无状态 token"""

import jwt
from datetime import datetime, timedelta

SECRET_KEY = "golden-triangle-cafe-2026-jwt-secret"
ALGORITHM = "HS256"
TOKEN_HOURS = 24


def generate_token(user_id: int, role: str) -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_HOURS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def validate_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"user_id": payload["user_id"], "role": payload["role"]}
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def remove_token(token: str):
    pass  # JWT 无状态，无需主动失效

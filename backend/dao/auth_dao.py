"""认证数据访问层 — token 管理"""

from database import get_connection
import secrets

# 简单的内存 token 存储：{token: {"member_id": int, "role": str}}
_token_store = {}


def generate_token() -> str:
    return secrets.token_hex(32)


def store_token(token: str, member_id: int, role: str):
    _token_store[token] = {"member_id": member_id, "role": role}


def validate_token(token: str) -> dict:
    return _token_store.get(token)


def remove_token(token: str):
    _token_store.pop(token, None)

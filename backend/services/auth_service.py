"""认证服务 — 支持操作员和会员双通道登录"""

import bcrypt
from dao.member_dao import get_member_by_phone
from dao.operator_dao import get_operator_by_login
from dao.auth_dao import generate_token, store_token, validate_token, remove_token


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def login(login_name: str, password: str) -> dict:
    """
    登录认证：优先查 OPERATOR 表（管理人员），再查 MEMBER 表（顾客）
    """
    # 1. 尝试操作员登录
    operator = get_operator_by_login(login_name)
    if operator and verify_password(password, operator["password_hash"]):
        role = operator["role"]
        token = generate_token()
        store_token(token, operator["operator_id"], role)
        return {
            "token": token,
            "user_id": operator["operator_id"],
            "name": operator["name"],
            "login_name": operator["login_name"],
            "role": role,  # super_admin / cashier
        }

    # 2. 尝试会员登录
    member = get_member_by_phone(login_name)
    if member and verify_password(password, member["password_hash"]):
        if not member["is_active"]:
            raise ValueError("账号已停用")
        role = "member"
        token = generate_token()
        store_token(token, member["member_id"], role)
        return {
            "token": token,
            "user_id": member["member_id"],
            "name": member["name"],
            "phone": member["phone"],
            "role": role,
            "balance": float(member["balance"]),
        }

    raise ValueError("账号或密码错误")


def logout(token: str):
    remove_token(token)


def get_current_user(token: str) -> dict:
    user = validate_token(token)
    if not user:
        raise PermissionError("未登录或 token 已过期")
    return user

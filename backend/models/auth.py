"""认证相关模型"""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    login: str  # 操作员用户名 或 会员手机号
    password: str


class LoginResponse(BaseModel):
    token: str
    user_id: int
    name: str
    role: str  # "super_admin" | "cashier" | "member"

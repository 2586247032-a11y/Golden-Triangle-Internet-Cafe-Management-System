"""认证路由"""

from fastapi import APIRouter, Header, HTTPException
from models.auth import LoginRequest, LoginResponse
from services.auth_service import login, logout, get_current_user

router = APIRouter(tags=["认证"])


@router.post("/login", response_model=LoginResponse)
def api_login(body: LoginRequest):
    """登录"""
    try:
        result = login(body.login, body.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
def api_logout(authorization: str = Header(default="")):
    """登出"""
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    if token:
        logout(token)
    return {"message": "已登出"}


@router.get("/me")
def api_me(authorization: str = Header(default="")):
    """获取当前用户信息"""
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        user = get_current_user(token)
        return user
    except PermissionError as e:
        raise HTTPException(status_code=401, detail=str(e))

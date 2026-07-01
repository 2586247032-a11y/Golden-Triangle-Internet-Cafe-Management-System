"""系统设置路由 — 仅管理员可访问"""

from fastapi import APIRouter, Header, HTTPException
from dao import config_dao, zone_dao
from services.auth_service import get_current_user

router = APIRouter(tags=["系统设置"])


def _auth_admin(authorization: str):
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        user = get_current_user(token)
        if user["role"] not in ("admin", "super_admin"):
            raise PermissionError("需要管理员权限")
        return user
    except PermissionError:
        raise HTTPException(status_code=401, detail="未登录或 token 已过期")


def _auth_super(authorization: str):
    """仅超级管理员"""
    user = _auth_admin(authorization)
    if user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="仅超级管理员可修改定价")
    return user


@router.get("/settings")
def get_settings(authorization: str = Header(default="")):
    _auth_admin(authorization)
    configs = config_dao.get_all_configs()
    return configs


@router.put("/settings/{config_key}")
def update_setting(config_key: str, body: dict, authorization: str = Header(default="")):
    _auth_admin(authorization)
    value = body.get("config_value", "")
    if not config_dao.update_config(config_key, value):
        raise HTTPException(status_code=404, detail="配置项不存在")
    return {"message": "配置更新成功"}


@router.get("/settings/zones")
def get_zone_settings(authorization: str = Header(default="")):
    _auth_admin(authorization)
    return zone_dao.get_all_zones()


@router.put("/settings/zones/{zone_id}")
def update_zone_pricing(zone_id: int, body: dict, authorization: str = Header(default="")):
    _auth_super(authorization)
    zone_dao.update_zone_pricing(
        zone_id=zone_id,
        hourly_member=float(body["hourly_member"]),
        hourly_guest=float(body["hourly_guest"]),
        overnight_member=float(body["overnight_member"]),
        overnight_guest=float(body["overnight_guest"]),
    )
    return {"message": "区域定价更新成功"}

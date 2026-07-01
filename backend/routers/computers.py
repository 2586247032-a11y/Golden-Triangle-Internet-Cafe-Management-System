"""电脑管理路由"""

from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional
from dao import computer_dao, zone_dao
from services.auth_service import get_current_user

router = APIRouter(tags=["电脑管理"])


def _auth(authorization: str):
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        return get_current_user(token)
    except PermissionError:
        raise HTTPException(status_code=401, detail="未登录或 token 已过期")


@router.get("/computers")
def list_computers(
    zone_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    authorization: str = Header(default=""),
):
    _auth(authorization)
    return computer_dao.get_computers(zone_id=zone_id, status=status)


@router.get("/computers/overview")
def computers_overview(authorization: str = Header(default="")):
    _auth(authorization)
    return computer_dao.get_computers_overview()


@router.put("/computers/{computer_id}/status")
def update_computer_status(computer_id: int, body: dict, authorization: str = Header(default="")):
    _auth(authorization)
    new_status = body.get("status", "")
    if new_status not in ("free", "fault"):
        raise HTTPException(status_code=400, detail="状态值无效，仅支持 free 或 fault")

    computer = computer_dao.get_computer_by_id(computer_id)
    if not computer:
        raise HTTPException(status_code=404, detail="电脑不存在")

    # 只能从 using 以外的状态切换
    if computer["status"] == "using":
        raise HTTPException(status_code=400, detail="使用中的电脑不能直接切换状态，请先下机")

    computer_dao.update_computer_status(computer_id, new_status)
    return {"message": "状态更新成功"}


@router.get("/zones")
def list_zones(authorization: str = Header(default="")):
    _auth(authorization)
    return zone_dao.get_all_zones()

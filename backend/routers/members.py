"""会员管理路由"""

from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional
from database import get_connection
from dao import member_dao, recharge_dao
from services.auth_service import get_current_user, hash_password
from models.member import MemberCreate, RechargeRequest, RechargeBonus

router = APIRouter(tags=["会员管理"])


def _auth(authorization: str):
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        return get_current_user(token)
    except PermissionError:
        raise HTTPException(status_code=401, detail="未登录或 token 已过期")


@router.get("/members")
def list_members(
    keyword: Optional[str] = Query(None),
    authorization: str = Header(default=""),
):
    _auth(authorization)
    return member_dao.get_members(keyword=keyword)


@router.get("/members/{member_id}")
def get_member(member_id: int, authorization: str = Header(default="")):
    _auth(authorization)
    member = member_dao.get_member_by_id(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    recharge_records = member_dao.get_member_recharge_records(member_id)
    return {
        "member_id": member["member_id"],
        "phone": member["phone"],
        "name": member["name"],
        "balance": float(member["balance"]),
        "total_recharged": float(member["total_recharged"]),
        "points": member["points"],
        "is_active": bool(member["is_active"]),
        "role": member.get("role", "cashier"),
        "created_at": str(member["created_at"]) if member["created_at"] else None,
        "recharge_records": recharge_records,
    }


@router.put("/members/{member_id}/role")
def update_member_role(member_id: int, body: dict, authorization: str = Header(default="")):
    """修改会员角色 — 仅超级管理员（已废弃，角色现在在 OPERATOR 表管理）"""
    user = _auth(authorization)
    if user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="仅超级管理员可修改角色")
    raise HTTPException(status_code=400, detail="角色管理请通过 OPERATOR 表操作")


@router.post("/members")
def create_member(body: MemberCreate, authorization: str = Header(default="")):
    _auth(authorization)
    # 校验手机号唯一
    existing = member_dao.get_member_by_phone(body.phone)
    if existing:
        raise HTTPException(status_code=400, detail="该手机号已注册")

    password_hash = hash_password(body.password)
    member_id = member_dao.create_member(body.phone, body.name, password_hash)
    return {"member_id": member_id, "message": "注册成功"}


@router.post("/members/{member_id}/recharge")
def recharge_member(member_id: int, body: RechargeRequest, authorization: str = Header(default="")):
    """会员充值 — 事务操作"""
    _auth(authorization)

    member = member_dao.get_member_by_id(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")

    amount = body.amount
    bonus = RechargeBonus.get_bonus(amount)
    balance_after = float(member["balance"]) + amount + bonus

    # 事务操作
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # 更新余额
        cursor.execute(
            "UPDATE MEMBER SET Balance = Balance + ?, Total_Recharged = Total_Recharged + ? WHERE Member_ID = ?",
            (amount + bonus, amount, member_id)
        )
        # 插入充值记录
        recharge_dao.insert_recharge(conn, cursor, member_id, amount, bonus, balance_after, body.operator or "收银员")
        conn.commit()
        return {"message": f"充值成功，到账 {amount + bonus} 元（含赠送 {bonus} 元）", "balance_after": balance_after}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"充值失败: {str(e)}")
    finally:
        conn.close()

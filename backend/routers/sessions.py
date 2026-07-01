"""上机会话路由 — 开卡/下机/查询"""

from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional
from database import get_connection
from dao import computer_dao, zone_dao, session_dao, member_dao, config_dao
from services.auth_service import get_current_user
from services.billing import BillingCalculator, parse_pricing_snapshot
from models.session import SessionStartRequest
from datetime import datetime

router = APIRouter(tags=["上机管理"])


def _auth(authorization: str):
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        return get_current_user(token)
    except PermissionError:
        raise HTTPException(status_code=401, detail="未登录或 token 已过期")


@router.post("/sessions/start")
def start_session(body: SessionStartRequest, authorization: str = Header(default="")):
    """开卡上机"""
    _auth(authorization)

    # 验证电脑
    computer = computer_dao.get_computer_by_id(body.computer_id)
    if not computer:
        raise HTTPException(status_code=404, detail="电脑不存在")
    if computer["status"] != "free":
        raise HTTPException(status_code=400, detail=f"电脑状态为 {computer['status']}，无法开卡")

    # 散客验证
    if body.is_guest and not body.guest_phone:
        raise HTTPException(status_code=400, detail="散客手机号必填")
    if body.is_guest and body.guest_phone and len(body.guest_phone) != 11:
        raise HTTPException(status_code=400, detail="手机号格式错误，需为 11 位数字")

    # 会员验证
    member_id = body.member_id
    if not body.is_guest and body.member_id:
        member = member_dao.get_member_by_id(body.member_id)
        if not member:
            raise HTTPException(status_code=404, detail="会员不存在")

    # 获取区域定价，写入定价快照
    zone = zone_dao.get_zone_by_id(computer["zone_id"])
    if not zone:
        raise HTTPException(status_code=404, detail="区域不存在")

    pricing_snapshot = {
        "hourly_member": float(zone["hourly_member"]),
        "hourly_guest": float(zone["hourly_guest"]),
        "overnight_member": float(zone["overnight_member"]),
        "overnight_guest": float(zone["overnight_guest"]),
        "zone_id": zone["zone_id"],
        "zone_name": zone["zone_name"],
    }

    # 事务：创建上机记录 + 更新电脑状态
    conn = get_connection()
    try:
        cursor = conn.cursor()
        session_dao.create_session(
            conn, cursor,
            computer_id=body.computer_id,
            member_id=member_id,
            is_guest=body.is_guest,
            guest_phone=body.guest_phone,
            pricing_snapshot=pricing_snapshot,
        )
        conn.commit()
        return {"message": "开卡成功", "pricing": pricing_snapshot}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"开卡失败: {str(e)}")
    finally:
        conn.close()


@router.post("/sessions/{record_id}/end")
def end_session(record_id: int, authorization: str = Header(default="")):
    """下机结算"""
    _auth(authorization)

    session = session_dao.get_session_by_id(record_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if session["status"] != "active":
        raise HTTPException(status_code=400, detail="该会话已结束")

    # 解析定价快照
    pricing = parse_pricing_snapshot(session.get("amount_detail"))

    # 判断用户类型
    is_member = not bool(session["is_guest"])
    hourly_price = pricing["hourly_member"] if is_member else pricing["hourly_guest"]
    overnight_price = pricing["overnight_member"] if is_member else pricing["overnight_guest"]

    # 最低消费开关
    min_charge = config_dao.get_config_value("min_charge_threshold", "15")
    min_charge_enabled = int(min_charge) > 0

    # 计算费用
    t_start = session["start_time"]
    t_end = datetime.now()
    result = BillingCalculator.calculate(
        t_start=t_start,
        t_end=t_end,
        hourly_price=hourly_price,
        overnight_price=overnight_price,
        is_member=is_member,
        min_charge_enabled=min_charge_enabled,
    )

    # 事务：完结记录 + 释放电脑 + 扣余额
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # 完结上机记录
        session_dao.end_session(
            conn, cursor, record_id,
            billing_mode=result["billing_mode"],
            actual_amount=result["actual_amount"],
            amount_detail=result["detail"],
        )

        # 如果是会员，扣减余额
        if is_member and session["member_id"] and result["actual_amount"] > 0:
            member = member_dao.get_member_by_id(session["member_id"])
            if member and float(member["balance"]) < result["actual_amount"]:
                conn.rollback()
                raise HTTPException(status_code=400, detail="余额不足，请先充值")
            member_dao.update_member_balance(conn, cursor, session["member_id"], -result["actual_amount"])

        conn.commit()

        return {
            "record_id": record_id,
            "computer_id": session["computer_id"],
            "start_time": str(t_start),
            "end_time": str(t_end),
            "total_minutes": result["total_minutes"],
            "billing_mode": result["billing_mode"],
            "billing_detail": result["detail"],
            "actual_amount": result["actual_amount"],
            "member_id": session["member_id"],
            "is_guest": bool(session["is_guest"]),
            "guest_phone": session["guest_phone"],
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"结算失败: {str(e)}")
    finally:
        conn.close()


@router.get("/sessions/active")
def active_sessions(authorization: str = Header(default="")):
    """当前所有进行中的会话"""
    _auth(authorization)
    sessions = session_dao.get_active_sessions()
    result = []
    for s in sessions:
        pricing = parse_pricing_snapshot(s.get("amount_detail"))
        is_member = not bool(s["is_guest"])
        hourly_price = pricing["hourly_member"] if is_member else pricing["hourly_guest"]
        overnight_price = pricing["overnight_member"] if is_member else pricing["overnight_guest"]

        # 预估当前费用
        t_start = s["start_time"]
        elapsed = s.get("elapsed_minutes", 0)
        minute_price = hourly_price / 60.0
        estimated = round(elapsed * minute_price, 2)

        result.append({
            "record_id": s["record_id"],
            "computer_id": s["computer_id"],
            "computer_no": s["computer_no"],
            "zone_id": s["zone_id"],
            "zone_name": s["zone_name"],
            "member_id": s["member_id"],
            "member_name": s.get("member_name"),
            "start_time": str(t_start),
            "elapsed_minutes": elapsed,
            "estimated_amount": estimated,
            "is_guest": bool(s["is_guest"]),
            "guest_phone": s["guest_phone"],
            "billing_mode": "hourly",
        })
    return result


@router.get("/sessions")
def history_sessions(
    date: Optional[str] = Query(None),
    member_id: Optional[int] = Query(None),
    authorization: str = Header(default=""),
):
    _auth(authorization)
    sessions = session_dao.get_completed_sessions(date=date, member_id=member_id)
    return [
        {
            "record_id": s["record_id"],
            "computer_id": s["computer_id"],
            "computer_no": s["computer_no"],
            "member_id": s["member_id"],
            "member_name": s.get("member_name"),
            "start_time": str(s["start_time"]),
            "end_time": str(s["end_time"]) if s["end_time"] else None,
            "billing_mode": s["billing_mode"],
            "actual_amount": float(s["actual_amount"]) if s["actual_amount"] is not None else None,
            "amount_detail": s["amount_detail"],
            "status": s["status"],
            "is_guest": bool(s["is_guest"]),
            "guest_phone": s["guest_phone"],
        }
        for s in sessions
    ]


@router.get("/dashboard/revenue")
def dashboard_revenue(authorization: str = Header(default="")):
    """今日营收概览"""
    _auth(authorization)
    revenue = session_dao.get_today_revenue()
    overview = computer_dao.get_computers_overview()

    total = sum(o["total"] for o in overview)
    using = sum(o["using"] for o in overview)
    occupancy = round(using / total * 100, 1) if total > 0 else 0

    return {
        "today_revenue": {
            "session": revenue["session_revenue"],
            "product": revenue["product_revenue"],
            "rental": revenue["rental_revenue"],
            "total": revenue["session_revenue"] + revenue["product_revenue"] + revenue["rental_revenue"],
        },
        "occupancy_rate": occupancy,
        "zone_overview": overview,
    }

"""设备租借路由"""

from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional
from database import get_connection
from dao import member_dao, rental_dao
from services.auth_service import get_current_user
from models.rental import RentalCreate, RentalReturn

router = APIRouter(tags=["设备租借"])


def _auth(authorization: str):
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        return get_current_user(token)
    except PermissionError:
        raise HTTPException(status_code=401, detail="未登录或 token 已过期")


# 固定设备价格表
EQUIPMENT_PRICES = {
    "游戏耳机": 10,
    "机械键盘": 15,
    "充电宝": 5,
    "游戏鼠标": 8,
    "游戏手柄": 10,
    "摄像头": 8,
}


@router.post("/rentals")
def create_rental(body: RentalCreate, authorization: str = Header(default="")):
    _auth(authorization)

    member = member_dao.get_member_by_id(body.member_id)
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")

    # 价格校验：如果是已知设备类型，使用固定价格
    if body.equipment_name in EQUIPMENT_PRICES:
        body.rental_fee_per_day = EQUIPMENT_PRICES[body.equipment_name]

    conn = get_connection()
    try:
        cursor = conn.cursor()
        rental_id = rental_dao.create_rental(conn, cursor, body.member_id, body.equipment_name, body.rental_fee_per_day)
        conn.commit()
        return {"rental_id": rental_id, "message": "租借成功"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"租借失败: {str(e)}")
    finally:
        conn.close()


@router.post("/rentals/{rental_id}/return")
def return_rental(rental_id: int, body: RentalReturn, authorization: str = Header(default="")):
    _auth(authorization)

    rental = rental_dao.get_rental_by_id(rental_id)
    if not rental:
        raise HTTPException(status_code=404, detail="租借记录不存在")
    if rental["status"] != "active":
        raise HTTPException(status_code=400, detail="该租借已归还")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        total_fee = rental_dao.return_rental(conn, cursor, rental_id, body.actual_days)
        conn.commit()
        return {"rental_id": rental_id, "total_fee": total_fee, "message": f"归还成功，费用 {total_fee} 元"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"归还失败: {str(e)}")
    finally:
        conn.close()


@router.get("/rentals")
def list_rentals(
    status: Optional[str] = Query(None),
    member_id: Optional[int] = Query(None),
    authorization: str = Header(default=""),
):
    _auth(authorization)
    rentals = rental_dao.get_rentals(status=status, member_id=member_id)
    return [
        {
            "rental_id": r["rental_id"],
            "member_id": r["member_id"],
            "member_name": r.get("member_name"),
            "equipment_name": r["equipment_name"],
            "rental_fee_per_day": float(r["rental_fee_per_day"]),
            "start_time": str(r["start_time"]),
            "end_time": str(r["end_time"]) if r["end_time"] else None,
            "total_fee": float(r["total_fee"]) if r["total_fee"] is not None else None,
            "status": r["status"],
        }
        for r in rentals
    ]

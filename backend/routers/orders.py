"""商品订单路由"""

from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional
from database import get_connection
from dao import member_dao, product_dao, order_dao
from services.auth_service import get_current_user
from models.order import OrderCreate

router = APIRouter(tags=["商品订单"])


def _auth(authorization: str):
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        return get_current_user(token)
    except PermissionError:
        raise HTTPException(status_code=401, detail="未登录或 token 已过期")


@router.post("/orders")
def create_order(body: OrderCreate, authorization: str = Header(default="")):
    """创建商品订单 — 事务：扣库存 + 扣余额"""
    _auth(authorization)

    member = member_dao.get_member_by_id(body.member_id)
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")

    # 计算总金额并验证库存
    total = 0.0
    order_items = []
    for item in body.items:
        product = product_dao.get_product_by_id(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"商品 ID {item.product_id} 不存在")
        if product["stock"] < item.quantity:
            raise HTTPException(status_code=400, detail=f"商品「{product['name']}」库存不足（当前: {product['stock']}）")
        if not product["is_available"]:
            raise HTTPException(status_code=400, detail=f"商品「{product['name']}」已下架")
        subtotal = float(product["price"]) * item.quantity
        total += subtotal
        order_items.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": float(product["price"]),
        })

    total = round(total, 2)

    # 检查余额
    if float(member["balance"]) < total:
        raise HTTPException(status_code=400, detail=f"余额不足（当前: {member['balance']} 元，需: {total} 元）")

    # 事务操作
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # 创建订单
        order_id = order_dao.create_order(conn, cursor, body.member_id, total, body.operator or "收银员")

        # 插入明细 + 扣库存
        for oi in order_items:
            order_dao.create_order_detail(conn, cursor, order_id, oi["product"]["product_id"], oi["quantity"], oi["unit_price"])
            product_dao.update_product_stock(conn, cursor, oi["product"]["product_id"], -oi["quantity"])

        # 扣余额
        member_dao.update_member_balance(conn, cursor, body.member_id, -total)

        conn.commit()
        return {"order_id": order_id, "total_amount": total, "message": "下单成功"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"下单失败: {str(e)}")
    finally:
        conn.close()


@router.get("/orders")
def list_orders(
    date: Optional[str] = Query(None),
    authorization: str = Header(default=""),
):
    _auth(authorization)
    orders = order_dao.get_orders(date=date)
    result = []
    for o in orders:
        items = order_dao.get_order_details(o["order_id"])
        result.append({
            "order_id": o["order_id"],
            "member_id": o["member_id"],
            "member_name": o.get("member_name"),
            "total_amount": float(o["total_amount"]),
            "order_time": str(o["order_time"]),
            "operator": o.get("operator", ""),
            "items": items,
        })
    return result

"""商品管理路由"""

from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional
from database import get_connection
from dao import product_dao
from services.auth_service import get_current_user

router = APIRouter(tags=["商品管理"])


def _auth(authorization: str):
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        return get_current_user(token)
    except PermissionError:
        raise HTTPException(status_code=401, detail="未登录或 token 已过期")


def _auth_super(authorization: str):
    user = _auth(authorization)
    if user.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="仅超级管理员可操作")
    return user


@router.get("/products")
def list_products(
    category: Optional[str] = Query(None),
    authorization: str = Header(default=""),
):
    _auth(authorization)
    return product_dao.get_products(category=category)


@router.put("/products/{product_id}/restock")
def restock_product(product_id: int, body: dict, authorization: str = Header(default="")):
    """补货 — 仅超级管理员"""
    _auth_super(authorization)

    quantity = int(body.get("quantity", 0))
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="补货数量必须大于0")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE PRODUCT SET Stock = Stock + ? WHERE Product_ID = ?", (quantity, product_id))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="商品不存在")
        return {"message": f"补货成功，增加 {quantity} 件"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

"""订单相关模型"""

from pydantic import BaseModel, Field
from typing import List


class OrderDetailItem(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    member_id: int
    items: List[OrderDetailItem]
    operator: str = ""


class OrderResponse(BaseModel):
    order_id: int
    member_id: int
    total_amount: float
    order_time: str
    operator: str
    items: List[dict] = []

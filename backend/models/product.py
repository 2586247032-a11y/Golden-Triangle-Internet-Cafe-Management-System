"""商品相关模型"""

from pydantic import BaseModel
from typing import Optional


class ProductResponse(BaseModel):
    product_id: int
    name: str
    category: str
    price: float
    stock: int
    unit: str
    is_available: bool

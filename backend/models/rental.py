"""设备租借相关模型"""

from pydantic import BaseModel, Field
from typing import Optional


class RentalCreate(BaseModel):
    member_id: int
    equipment_name: str
    rental_fee_per_day: float = Field(..., gt=0)


class RentalResponse(BaseModel):
    rental_id: int
    member_id: int
    member_name: str = ""
    equipment_name: str
    rental_fee_per_day: float
    start_time: str
    end_time: Optional[str] = None
    total_fee: Optional[float] = None
    status: str


class RentalReturn(BaseModel):
    actual_days: int = Field(..., gt=0)

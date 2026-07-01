"""会员相关模型"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MemberCreate(BaseModel):
    phone: str = Field(..., min_length=11, max_length=11)
    name: str
    password: str


class MemberResponse(BaseModel):
    member_id: int
    phone: str
    name: str
    balance: float
    total_recharged: float
    points: int
    is_active: bool
    created_at: Optional[datetime] = None


class MemberDetail(BaseModel):
    member_id: int
    phone: str
    name: str
    balance: float
    total_recharged: float
    points: int
    is_active: bool
    created_at: Optional[datetime] = None
    recharge_records: list = []


class RechargeRequest(BaseModel):
    amount: float = Field(..., gt=0)
    operator: str = ""


class RechargeBonus:
    """充值赠送档位"""
    TIERS = [
        (100, 30),
        (200, 70),
        (300, 120),
        (500, 220),
        (1000, 500),
    ]

    @classmethod
    def get_bonus(cls, amount: float) -> float:
        bonus = 0
        for threshold, b in cls.TIERS:
            if amount >= threshold:
                bonus = b
        return bonus

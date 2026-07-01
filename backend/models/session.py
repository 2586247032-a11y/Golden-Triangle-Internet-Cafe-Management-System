"""上机会话相关模型"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SessionStartRequest(BaseModel):
    computer_id: int
    member_id: Optional[int] = None
    is_guest: bool = False
    guest_phone: Optional[str] = None


class SessionEndResponse(BaseModel):
    record_id: int
    computer_id: int
    start_time: str
    end_time: str
    total_minutes: int
    billing_mode: str  # hourly / overnight
    billing_detail: str  # 人类可读的计费明细
    actual_amount: float
    member_id: Optional[int] = None
    is_guest: bool
    guest_phone: Optional[str] = None


class ActiveSession(BaseModel):
    record_id: int
    computer_id: int
    computer_no: str
    zone_id: int
    zone_name: str
    member_id: Optional[int] = None
    member_name: Optional[str] = None
    start_time: str
    elapsed_minutes: int
    estimated_amount: float
    is_guest: bool
    guest_phone: Optional[str] = None
    billing_mode: str


class SessionHistory(BaseModel):
    record_id: int
    computer_id: int
    computer_no: str
    member_id: Optional[int] = None
    member_name: Optional[str] = None
    start_time: str
    end_time: Optional[str] = None
    billing_mode: str
    actual_amount: Optional[float] = None
    amount_detail: Optional[str] = None
    status: str
    is_guest: bool
    guest_phone: Optional[str] = None

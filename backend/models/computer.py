"""电脑相关模型"""

from pydantic import BaseModel
from typing import Optional


class ComputerResponse(BaseModel):
    computer_id: int
    zone_id: int
    zone_name: str = ""
    computer_no: str
    room_no: Optional[str] = None
    status: str  # free / using / fault


class ComputerStatusUpdate(BaseModel):
    status: str  # free / fault


class ComputerOverview(BaseModel):
    zone_id: int
    zone_name: str
    total: int
    free: int
    using: int
    fault: int


class ZoneResponse(BaseModel):
    zone_id: int
    zone_name: str
    hourly_member: float
    hourly_guest: float
    overnight_member: float
    overnight_guest: float
    sort_order: int

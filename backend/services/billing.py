"""计费引擎 — 核心业务逻辑

规则：
  包夜时段 = [当日22:00, 次日07:00]
  包夜累计时长 >= 240 分钟 → 账单 = 包夜价
  否则 → 账单 = 总分钟数 × (小时单价 / 60)
  最低消费开关开启 && 总时长 <= 15 分钟 → 账单 = 0
"""

from datetime import datetime, timedelta
import json
import math


class BillingCalculator:
    """计费计算器"""

    OVERNIGHT_START_HOUR = 22  # 包夜开始：22:00
    OVERNIGHT_END_HOUR = 7     # 包夜结束：次日 07:00

    @classmethod
    def _get_overnight_periods(cls, t_start: datetime, t_end: datetime) -> list:
        """生成 t_start 到 t_end 之间所有的包夜时段 [(start, end), ...]"""
        periods = []
        current_date = t_start.date()

        # 从 t_start 当天开始，一直生成到 t_end 之后的日期
        while current_date <= t_end.date():
            overnight_start = datetime(current_date.year, current_date.month, current_date.day, cls.OVERNIGHT_START_HOUR, 0, 0)
            overnight_end = overnight_start + timedelta(hours=9)  # 22:00 → 次日 07:00 = 9 小时

            # 重叠检测
            overlap_start = max(t_start, overnight_start)
            overlap_end = min(t_end, overnight_end)

            if overlap_start < overlap_end:
                periods.append((overlap_start, overlap_end))

            current_date += timedelta(days=1)

        return periods

    @classmethod
    def _calc_overlap_minutes(cls, t_start: datetime, t_end: datetime, periods: list) -> int:
        """计算在包夜时段内的累计分钟数"""
        total = 0
        for p_start, p_end in periods:
            overlap_start = max(t_start, p_start)
            overlap_end = min(t_end, p_end)
            if overlap_start < overlap_end:
                total += (overlap_end - overlap_start).total_seconds() / 60
        return int(total)

    @classmethod
    def calculate(cls, t_start: datetime, t_end: datetime, hourly_price: float, overnight_price: float,
                  is_member: bool = True, min_charge_enabled: bool = False) -> dict:
        """
        计费计算

        Args:
            t_start: 上机时间
            t_end: 下机时间
            hourly_price: 小时单价
            overnight_price: 包夜价
            is_member: 是否会员
            min_charge_enabled: 最低消费开关是否开启

        Returns:
            {
                "total_minutes": int,
                "overnight_minutes": int,
                "billing_mode": "hourly" | "overnight",
                "actual_amount": float,
                "detail": str  # 人类可读的计费明细
            }
        """
        total_seconds = (t_end - t_start).total_seconds()
        total_minutes = int(math.ceil(total_seconds / 60))  # 按分钟向上取整

        # 计算包夜时段重叠
        overnight_periods = cls._get_overnight_periods(t_start, t_end)
        overnight_minutes = cls._calc_overlap_minutes(t_start, t_end, overnight_periods)
        minute_price = hourly_price / 60.0

        detail_parts = []

        # 判断是否触发包夜封顶
        if overnight_minutes >= 240:
            billing_mode = "overnight"
            actual_amount = overnight_price
            detail_parts.append(f"包夜时段累计 {overnight_minutes} 分钟 >= 240 分钟，触发包夜封顶")
            detail_parts.append(f"包夜价: {overnight_price} 元")
        else:
            billing_mode = "hourly"
            actual_amount = round(total_minutes * minute_price, 2)
            detail_parts.append(f"总时长 {total_minutes} 分钟 × {minute_price:.4f} 元/分钟 = {total_minutes * minute_price:.2f} 元")
            if overnight_minutes > 0:
                detail_parts.append(f"(其中包夜时段 {overnight_minutes} 分钟，未触发封顶)")

        # 最低消费检查（≤15 分钟免计费）
        if min_charge_enabled and total_minutes <= 15:
            actual_amount = 0
            detail_parts.append(f"最低消费：上机 {total_minutes} 分钟 ≤ 15 分钟，免计费")
            billing_mode = "hourly"

        detail_str = "；".join(detail_parts)

        return {
            "total_minutes": total_minutes,
            "overnight_minutes": overnight_minutes,
            "billing_mode": billing_mode,
            "actual_amount": actual_amount,
            "detail": detail_str,
        }

    @classmethod
    def estimate(cls, t_start: datetime, hourly_price: float, overnight_price: float) -> dict:
        """从 t_start 到当前时间的预估费用（用于收银台实时显示）"""
        return cls.calculate(t_start, datetime.now(), hourly_price, overnight_price, min_charge_enabled=False)


def parse_pricing_snapshot(amount_detail: str) -> dict:
    """从 Amount_Detail JSON 中解析定价快照"""
    if not amount_detail:
        return {"hourly_member": 0, "hourly_guest": 0, "overnight_member": 0, "overnight_guest": 0}
    try:
        return json.loads(amount_detail)
    except (json.JSONDecodeError, TypeError):
        return {"hourly_member": 0, "hourly_guest": 0, "overnight_member": 0, "overnight_guest": 0}

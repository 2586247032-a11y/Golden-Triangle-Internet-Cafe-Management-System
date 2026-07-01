"""充值记录数据访问层"""

from database import get_connection


def insert_recharge(conn, cursor, member_id: int, amount: float, bonus: float, balance_after: float, operator: str):
    """插入充值记录，使用外部传入的连接和游标以支持事务"""
    cursor.execute(
        "INSERT INTO RECHARGE_RECORD (Member_ID, Amount, Bonus, Balance_After, Operator) VALUES (?, ?, ?, ?, ?)",
        (member_id, amount, bonus, balance_after, operator)
    )

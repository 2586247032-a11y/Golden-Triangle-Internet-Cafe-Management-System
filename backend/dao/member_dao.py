"""会员数据访问层"""

from database import get_connection, dict_from_row, dicts_from_cursor


def get_member_by_phone(phone: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Member_ID, Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active, Created_At FROM MEMBER WHERE Phone = ?",
            (phone,)
        )
        return dict_from_row(cursor, cursor.fetchone())
    finally:
        conn.close()


def get_member_by_id(member_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Member_ID, Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active, Created_At FROM MEMBER WHERE Member_ID = ?",
            (member_id,)
        )
        return dict_from_row(cursor, cursor.fetchone())
    finally:
        conn.close()


def get_members(keyword: str = None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        sql = "SELECT Member_ID, Phone, Name, Balance, Total_Recharged, Points, Is_Active, Created_At FROM MEMBER WHERE 1=1"
        params = []
        if keyword:
            sql += " AND (Phone LIKE ? OR Name LIKE ?)"
            kw = f"%{keyword}%"
            params.extend([kw, kw])
        sql += " ORDER BY Member_ID DESC"
        cursor.execute(sql, params)
        return dicts_from_cursor(cursor)
    finally:
        conn.close()


def create_member(phone: str, name: str, password_hash: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO MEMBER (Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active) OUTPUT INSERTED.Member_ID VALUES (?, ?, ?, 0, 0, 0, 1)",
            (phone, name, password_hash)
        )
        member_id = cursor.fetchone()[0]
        conn.commit()
        return member_id
    finally:
        conn.close()


def update_member_balance(conn, cursor, member_id: int, amount: float):
    """扣减余额（amount 为负数表示扣款），使用外部传入的连接和游标以支持事务"""
    cursor.execute(
        "UPDATE MEMBER SET Balance = Balance + ? WHERE Member_ID = ?",
        (amount, member_id)
    )


def get_member_recharge_records(member_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Recharge_ID, Member_ID, Amount, Bonus, Total, Balance_After, Recharge_Time, Operator FROM RECHARGE_RECORD WHERE Member_ID = ? ORDER BY Recharge_Time DESC",
            (member_id,)
        )
        return dicts_from_cursor(cursor)
    finally:
        conn.close()

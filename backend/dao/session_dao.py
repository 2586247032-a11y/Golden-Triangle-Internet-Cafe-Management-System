"""上机会话数据访问层"""

from database import get_connection, dict_from_row, dicts_from_cursor
import json


def create_session(conn, cursor, computer_id: int, member_id: int, is_guest: bool, guest_phone: str, pricing_snapshot: dict):
    """创建上机记录，使用外部连接和游标支持事务"""
    cursor.execute(
        """INSERT INTO ONLINE_RECORD (Computer_ID, Member_ID, Start_Time, Status, Is_Guest, Guest_Phone, Amount_Detail)
           VALUES (?, ?, GETDATE(), N'active', ?, ?, ?)""",
        (computer_id, member_id, 1 if is_guest else 0, guest_phone, json.dumps(pricing_snapshot, ensure_ascii=False))
    )
    # 更新电脑状态为 using
    cursor.execute("UPDATE COMPUTER SET Status = N'using' WHERE Computer_ID = ?", (computer_id,))


def get_active_sessions():
    """获取所有进行中的会话"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                o.Record_ID, o.Computer_ID, c.Computer_No, c.Zone_ID, z.Zone_Name,
                o.Member_ID, m.Name AS Member_Name,
                o.Start_Time, o.Status, o.Is_Guest, o.Guest_Phone,
                o.Amount_Detail,
                DATEDIFF(MINUTE, o.Start_Time, GETDATE()) AS Elapsed_Minutes
            FROM ONLINE_RECORD o
            JOIN COMPUTER c ON o.Computer_ID = c.Computer_ID
            JOIN ZONE z ON c.Zone_ID = z.Zone_ID
            LEFT JOIN MEMBER m ON o.Member_ID = m.Member_ID
            WHERE o.Status = N'active'
            ORDER BY o.Start_Time
        """)
        return dicts_from_cursor(cursor)
    finally:
        conn.close()


def get_session_by_id(record_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                o.Record_ID, o.Computer_ID, c.Computer_No, c.Zone_ID, z.Zone_Name,
                o.Member_ID, m.Name AS Member_Name,
                o.Start_Time, o.End_Time, o.Billing_Mode, o.Actual_Amount, o.Amount_Detail,
                o.Status, o.Is_Guest, o.Guest_Phone
            FROM ONLINE_RECORD o
            JOIN COMPUTER c ON o.Computer_ID = c.Computer_ID
            JOIN ZONE z ON c.Zone_ID = z.Zone_ID
            LEFT JOIN MEMBER m ON o.Member_ID = m.Member_ID
            WHERE o.Record_ID = ?
        """, (record_id,))
        return dict_from_row(cursor, cursor.fetchone())
    finally:
        conn.close()


def get_completed_sessions(date: str = None, member_id: int = None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        sql = """
            SELECT
                o.Record_ID, o.Computer_ID, c.Computer_No,
                o.Member_ID, m.Name AS Member_Name,
                o.Start_Time, o.End_Time, o.Billing_Mode, o.Actual_Amount, o.Amount_Detail,
                o.Status, o.Is_Guest, o.Guest_Phone
            FROM ONLINE_RECORD o
            JOIN COMPUTER c ON o.Computer_ID = c.Computer_ID
            LEFT JOIN MEMBER m ON o.Member_ID = m.Member_ID
            WHERE o.Status IN (N'completed', N'cancelled')
        """
        params = []
        if date:
            sql += " AND CAST(o.Start_Time AS DATE) = ?"
            params.append(date)
        if member_id:
            sql += " AND o.Member_ID = ?"
            params.append(member_id)
        sql += " ORDER BY o.Start_Time DESC"
        cursor.execute(sql, params)
        return dicts_from_cursor(cursor)
    finally:
        conn.close()


def end_session(conn, cursor, record_id: int, billing_mode: str, actual_amount: float, amount_detail: str):
    """完结上机记录并释放电脑，使用外部连接和游标支持事务"""
    cursor.execute("""
        UPDATE ONLINE_RECORD
        SET End_Time = GETDATE(), Billing_Mode = ?, Actual_Amount = ?, Amount_Detail = ?, Status = N'completed'
        WHERE Record_ID = ?
    """, (billing_mode, actual_amount, amount_detail, record_id))

    # 释放电脑
    cursor.execute("""
        UPDATE COMPUTER
        SET Status = N'free'
        WHERE Computer_ID = (SELECT Computer_ID FROM ONLINE_RECORD WHERE Record_ID = ?)
    """, (record_id,))


def get_today_revenue():
    """今日营收汇总"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                ISNULL((SELECT SUM(Actual_Amount) FROM ONLINE_RECORD
                        WHERE Status = N'completed' AND CAST(End_Time AS DATE) = CAST(GETDATE() AS DATE)), 0) AS session_revenue,
                ISNULL((SELECT SUM(Total_Amount) FROM PRODUCT_ORDER
                        WHERE CAST(Order_Time AS DATE) = CAST(GETDATE() AS DATE)), 0) AS product_revenue,
                ISNULL((SELECT SUM(Total_Fee) FROM EQUIPMENT_RENTAL
                        WHERE CAST(End_Time AS DATE) = CAST(GETDATE() AS DATE) AND Total_Fee > 0), 0) AS rental_revenue
        """)
        row = cursor.fetchone()
        if row:
            return {
                "session_revenue": float(row[0] or 0),
                "product_revenue": float(row[1] or 0),
                "rental_revenue": float(row[2] or 0),
            }
        return {"session_revenue": 0, "product_revenue": 0, "rental_revenue": 0}
    finally:
        conn.close()

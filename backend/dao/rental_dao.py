"""设备租借数据访问层"""

from database import get_connection, dict_from_row, dicts_from_cursor


def create_rental(conn, cursor, member_id: int, equipment_name: str, rental_fee_per_day: float):
    cursor.execute(
        """INSERT INTO EQUIPMENT_RENTAL (Member_ID, Equipment_Name, Rental_Fee_Per_Day, Start_Time, Status)
           OUTPUT INSERTED.Rental_ID
           VALUES (?, ?, ?, GETDATE(), N'active')""",
        (member_id, equipment_name, rental_fee_per_day)
    )
    return cursor.fetchone()[0]


def get_rentals(status: str = None, member_id: int = None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        sql = """
            SELECT r.Rental_ID, r.Member_ID, m.Name AS Member_Name,
                   r.Equipment_Name, r.Rental_Fee_Per_Day, r.Start_Time, r.End_Time, r.Total_Fee, r.Status
            FROM EQUIPMENT_RENTAL r
            LEFT JOIN MEMBER m ON r.Member_ID = m.Member_ID
            WHERE 1=1
        """
        params = []
        if status:
            sql += " AND r.Status = ?"
            params.append(status)
        if member_id:
            sql += " AND r.Member_ID = ?"
            params.append(member_id)
        sql += " ORDER BY r.Start_Time DESC"
        cursor.execute(sql, params)
        return dicts_from_cursor(cursor)
    finally:
        conn.close()


def get_rental_by_id(rental_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.Rental_ID, r.Member_ID, m.Name AS Member_Name,
                   r.Equipment_Name, r.Rental_Fee_Per_Day, r.Start_Time, r.End_Time, r.Total_Fee, r.Status
            FROM EQUIPMENT_RENTAL r
            LEFT JOIN MEMBER m ON r.Member_ID = m.Member_ID
            WHERE r.Rental_ID = ?
        """, (rental_id,))
        return dict_from_row(cursor, cursor.fetchone())
    finally:
        conn.close()


def return_rental(conn, cursor, rental_id: int, actual_days: int):
    total_fee = None
    cursor.execute("SELECT Rental_Fee_Per_Day FROM EQUIPMENT_RENTAL WHERE Rental_ID = ?", (rental_id,))
    row = cursor.fetchone()
    if row:
        fee_per_day = row[0]
        total_fee = float(fee_per_day) * actual_days

    cursor.execute("""
        UPDATE EQUIPMENT_RENTAL
        SET End_Time = GETDATE(), Total_Fee = ?, Status = N'returned'
        WHERE Rental_ID = ?
    """, (total_fee, rental_id))
    return total_fee

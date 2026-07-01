"""电脑数据访问层"""

from database import get_connection, dict_from_row, dicts_from_cursor


def get_computers(zone_id: int = None, status: str = None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        sql = """
            SELECT c.Computer_ID, c.Zone_ID, z.Zone_Name, c.Computer_No, c.Room_No, c.Status
            FROM COMPUTER c
            LEFT JOIN ZONE z ON c.Zone_ID = z.Zone_ID
            WHERE 1=1
        """
        params = []
        if zone_id:
            sql += " AND c.Zone_ID = ?"
            params.append(zone_id)
        if status:
            sql += " AND c.Status = ?"
            params.append(status)
        sql += " ORDER BY z.Sort_Order, c.Computer_No"
        cursor.execute(sql, params)
        return dicts_from_cursor(cursor)
    finally:
        conn.close()


def get_computer_by_id(computer_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT c.Computer_ID, c.Zone_ID, z.Zone_Name, c.Computer_No, c.Room_No, c.Status
               FROM COMPUTER c LEFT JOIN ZONE z ON c.Zone_ID = z.Zone_ID
               WHERE c.Computer_ID = ?""",
            (computer_id,)
        )
        return dict_from_row(cursor, cursor.fetchone())
    finally:
        conn.close()


def update_computer_status(computer_id: int, status: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE COMPUTER SET Status = ? WHERE Computer_ID = ?", (status, computer_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_computers_overview():
    """各区空闲/使用中/故障数量汇总"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                z.Zone_ID, z.Zone_Name,
                COUNT(c.Computer_ID) AS total,
                SUM(CASE WHEN c.Status = N'free' THEN 1 ELSE 0 END) AS free,
                SUM(CASE WHEN c.Status = N'using' THEN 1 ELSE 0 END) AS using,
                SUM(CASE WHEN c.Status = N'fault' THEN 1 ELSE 0 END) AS fault
            FROM ZONE z
            LEFT JOIN COMPUTER c ON z.Zone_ID = c.Zone_ID
            GROUP BY z.Zone_ID, z.Zone_Name, z.Sort_Order
            ORDER BY z.Sort_Order
        """)
        return dicts_from_cursor(cursor)
    finally:
        conn.close()

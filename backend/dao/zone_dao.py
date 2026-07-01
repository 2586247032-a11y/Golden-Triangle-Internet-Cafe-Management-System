"""区域数据访问层"""

from database import get_connection, dict_from_row, dicts_from_cursor


def get_all_zones():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Zone_ID, Zone_Name, Hourly_Member, Hourly_Guest, Overnight_Member, Overnight_Guest, Sort_Order FROM ZONE ORDER BY Sort_Order")
        return dicts_from_cursor(cursor)
    finally:
        conn.close()


def get_zone_by_id(zone_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Zone_ID, Zone_Name, Hourly_Member, Hourly_Guest, Overnight_Member, Overnight_Guest, Sort_Order FROM ZONE WHERE Zone_ID = ?", (zone_id,))
        return dict_from_row(cursor, cursor.fetchone())
    finally:
        conn.close()


def update_zone_pricing(zone_id: int, hourly_member: float, hourly_guest: float, overnight_member: float, overnight_guest: float):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE ZONE SET Hourly_Member = ?, Hourly_Guest = ?, Overnight_Member = ?, Overnight_Guest = ? WHERE Zone_ID = ?",
            (hourly_member, hourly_guest, overnight_member, overnight_guest, zone_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

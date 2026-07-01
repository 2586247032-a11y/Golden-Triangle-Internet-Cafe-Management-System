"""订单数据访问层"""

from database import get_connection, dicts_from_cursor


def create_order(conn, cursor, member_id: int, total_amount: float, operator: str):
    """创建订单，返回订单 ID"""
    cursor.execute(
        "INSERT INTO PRODUCT_ORDER (Member_ID, Total_Amount, Operator) OUTPUT INSERTED.Order_ID VALUES (?, ?, ?)",
        (member_id, total_amount, operator)
    )
    return cursor.fetchone()[0]


def create_order_detail(conn, cursor, order_id: int, product_id: int, quantity: int, unit_price: float):
    cursor.execute(
        "INSERT INTO ORDER_DETAIL (Order_ID, Product_ID, Quantity, Unit_Price) VALUES (?, ?, ?, ?)",
        (order_id, product_id, quantity, unit_price)
    )


def get_orders(date: str = None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        sql = """
            SELECT o.Order_ID, o.Member_ID, m.Name AS Member_Name, o.Total_Amount, o.Order_Time, o.Operator
            FROM PRODUCT_ORDER o
            LEFT JOIN MEMBER m ON o.Member_ID = m.Member_ID
            WHERE 1=1
        """
        params = []
        if date:
            sql += " AND CAST(o.Order_Time AS DATE) = ?"
            params.append(date)
        sql += " ORDER BY o.Order_Time DESC"
        cursor.execute(sql, params)
        return dicts_from_cursor(cursor)
    finally:
        conn.close()


def get_order_details(order_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.Detail_ID, d.Order_ID, d.Product_ID, p.Name AS Product_Name, d.Quantity, d.Unit_Price
            FROM ORDER_DETAIL d
            JOIN PRODUCT p ON d.Product_ID = p.Product_ID
            WHERE d.Order_ID = ?
        """, (order_id,))
        return dicts_from_cursor(cursor)
    finally:
        conn.close()

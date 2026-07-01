"""商品数据访问层"""

from database import get_connection, dict_from_row, dicts_from_cursor


def get_products(category: str = None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        sql = "SELECT Product_ID, Name, Category, Price, Stock, Unit, Is_Available FROM PRODUCT WHERE 1=1"
        params = []
        if category:
            sql += " AND Category = ?"
            params.append(category)
        sql += " ORDER BY Category, Name"
        cursor.execute(sql, params)
        return dicts_from_cursor(cursor)
    finally:
        conn.close()


def get_product_by_id(product_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Product_ID, Name, Category, Price, Stock, Unit, Is_Available FROM PRODUCT WHERE Product_ID = ?",
            (product_id,)
        )
        return dict_from_row(cursor, cursor.fetchone())
    finally:
        conn.close()


def update_product_stock(conn, cursor, product_id: int, quantity_change: int):
    """更新库存（quantity_change 为负数表示扣库存），使用外部连接和游标支持事务"""
    cursor.execute(
        "UPDATE PRODUCT SET Stock = Stock + ? WHERE Product_ID = ? AND Stock + ? >= 0",
        (quantity_change, product_id, quantity_change)
    )
    return cursor.rowcount > 0

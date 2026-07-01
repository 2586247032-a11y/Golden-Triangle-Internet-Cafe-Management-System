"""操作员数据访问层"""

from database import get_connection, dict_from_row


def get_operator_by_login(login_name: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Operator_ID, Login_Name, Password_Hash, Name, Role FROM OPERATOR WHERE Login_Name = ?",
            (login_name,)
        )
        return dict_from_row(cursor, cursor.fetchone())
    finally:
        conn.close()

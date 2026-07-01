"""数据库连接与工具函数"""

import pyodbc
from config import get_connection_string


def get_connection():
    """获取数据库连接"""
    return pyodbc.connect(get_connection_string())


def dict_from_row(cursor, row):
    """将 pyodbc 查询结果的一行转为 dict，键名统一小写"""
    if row is None:
        return None
    columns = [column[0].lower() for column in cursor.description]
    return dict(zip(columns, row))


def dicts_from_cursor(cursor):
    """将查询结果的所有行转为 dict 列表，键名统一小写"""
    columns = [column[0].lower() for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

"""系统配置数据访问层"""

from database import get_connection, dict_from_row, dicts_from_cursor


def get_all_configs():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Config_Key, Config_Value, Description FROM SYSTEM_CONFIG")
        return dicts_from_cursor(cursor)
    finally:
        conn.close()


def get_config(key: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Config_Key, Config_Value, Description FROM SYSTEM_CONFIG WHERE Config_Key = ?", (key,))
        return dict_from_row(cursor, cursor.fetchone())
    finally:
        conn.close()


def get_config_value(key: str, default: str = "0"):
    config = get_config(key)
    return config["config_value"] if config else default


def update_config(key: str, value: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE SYSTEM_CONFIG SET Config_Value = ? WHERE Config_Key = ?", (value, key))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

"""应用配置：从 .env 读取数据库连接参数"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_connection_string():
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    server = os.getenv("DB_SERVER", r"localhost\SQLEXPRESS")
    database = os.getenv("DB_NAME", "GoldenTriangleCafe")
    trusted = os.getenv("DB_TRUSTED_CONNECTION", "yes")

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection={trusted};"
    )

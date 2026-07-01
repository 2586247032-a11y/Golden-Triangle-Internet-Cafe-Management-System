"""操作员管理路由"""

from fastapi import APIRouter, Header, HTTPException
from database import get_connection
from dao import operator_dao
from services.auth_service import get_current_user, hash_password
from models.auth import LoginRequest

router = APIRouter(tags=["操作员管理"])


def _auth_super(authorization: str):
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    user = get_current_user(token)
    if user.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="仅超级管理员可操作")
    return user


@router.get("/operators")
def list_operators(authorization: str = Header(default="")):
    _auth_super(authorization)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Operator_ID, Login_Name, Name, Role, Created_At FROM OPERATOR ORDER BY Operator_ID")
        columns = [c[0].lower() for c in cursor.description]
        return [dict(zip(columns, r)) for r in cursor.fetchall()]
    finally:
        conn.close()


@router.post("/operators")
def create_operator(body: dict, authorization: str = Header(default="")):
    """创建收银员账号"""
    _auth_super(authorization)

    login_name = body.get("login", "").strip()
    password = body.get("password", "")
    name = body.get("name", "").strip() or login_name

    if len(login_name) < 3:
        raise HTTPException(status_code=400, detail="账号名至少3位")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="密码至少6位")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM OPERATOR WHERE Login_Name = ?", (login_name,))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="账号已存在")

        pw_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO OPERATOR (Login_Name, Password_Hash, Name, Role) OUTPUT INSERTED.Operator_ID VALUES (?, ?, ?, 'cashier')",
            (login_name, pw_hash, name)
        )
        op_id = cursor.fetchone()[0]
        conn.commit()
        return {"operator_id": op_id, "message": "收银员账号创建成功"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.delete("/operators/{operator_id}")
def delete_operator(operator_id: int, authorization: str = Header(default="")):
    """删除收银员（不能删除超级管理员）"""
    _auth_super(authorization)

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Role FROM OPERATOR WHERE Operator_ID = ?", (operator_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="操作员不存在")
        if row[0] == 'super_admin':
            raise HTTPException(status_code=400, detail="不能删除超级管理员")

        cursor.execute("DELETE FROM OPERATOR WHERE Operator_ID = ?", (operator_id,))
        conn.commit()
        return {"message": "已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

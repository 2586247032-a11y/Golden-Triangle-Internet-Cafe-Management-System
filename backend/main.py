"""金三角网吧收银管理系统 — FastAPI 入口"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from routers import auth, computers, members, sessions, products, orders, rentals, settings, operators

app = FastAPI(title="金三角网吧收银管理系统", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由（必须先于静态文件）
app.include_router(auth.router, prefix="/api")
app.include_router(computers.router, prefix="/api")
app.include_router(members.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(rentals.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(operators.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# 生产模式：加载前端静态文件（仅处理非 /api 请求）
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(STATIC_DIR) and os.path.isfile(os.path.join(STATIC_DIR, "index.html")):
    # 挂载 assets 目录
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{path_name:path}")
    async def spa_fallback(path_name: str):
        """SPA fallback: 非 /api 路径全部返回 index.html"""
        # /api 开头的已经由上面的路由处理，不会到这里
        file_path = os.path.join(STATIC_DIR, path_name)
        if path_name and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))



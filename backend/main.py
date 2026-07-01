"""金三角网吧收银管理系统 — FastAPI 入口"""

import os
from fastapi import FastAPI
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

# 注册 API 路由
app.include_router(auth.router, prefix="/api")
app.include_router(computers.router, prefix="/api")
app.include_router(members.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(rentals.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(operators.router, prefix="/api")

# 生产模式：加载前端静态文件
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str = ""):
        """SPA fallback：所有非 API 路由返回 index.html"""
        import os.path as _osp
        file_path = _osp.join(STATIC_DIR, full_path) if full_path else _osp.join(STATIC_DIR, "index.html")
        if _osp.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(_osp.join(STATIC_DIR, "index.html"))

    @app.get("/")
    async def root():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


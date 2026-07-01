"""金三角网吧收银管理系统 — FastAPI 入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, computers, members, sessions, products, orders, rentals, settings, operators

app = FastAPI(title="金三角网吧收银管理系统", version="1.0.0")

# CORS：允许所有来源（开发环境）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
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

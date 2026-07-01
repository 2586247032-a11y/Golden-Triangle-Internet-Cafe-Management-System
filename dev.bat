@echo off
chcp 65001 >nul
title 金三角网吧 - 开发模式

echo ============================================
echo   开发模式
echo   后端: http://localhost:8000
echo   前端: http://localhost:5173
echo ============================================

:: 启动后端
cd /d "%~dp0backend"
start "后端 API" cmd /c "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

:: 启动前端
cd /d "%~dp0frontend"
start "前端 Dev" cmd /c "npm run dev"

echo 两个窗口已打开，关闭窗口停止服务
pause

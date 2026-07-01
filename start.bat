@echo off
chcp 65001 >nul
title 金三角网吧收银管理系统

echo ============================================
echo   金三角网吧收银管理系统 - 一键启动
echo ============================================
echo.

:: 1. 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

:: 2. 安装后端依赖
echo [1/4] 安装后端依赖...
cd /d "%~dp0backend"
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

:: 3. 检查前端是否已构建
cd /d "%~dp0frontend"
if not exist "dist\index.html" (
    echo [2/4] 构建前端（首次需要，之后跳过）...
    call npm install --silent
    call npm run build
    if %errorlevel% neq 0 (
        echo [错误] 前端构建失败
        pause
        exit /b 1
    )
) else (
    echo [2/4] 前端已构建，跳过
)

:: 4. 构建前端（每次启动都重新构建以确保最新）
echo [3/4] 构建前端最新版本...
call npm run build
if %errorlevel% neq 0 (
    echo [警告] 前端构建失败，使用旧版本
)

:: 5. 启动后端
cd /d "%~dp0backend"
echo.
echo [4/4] 启动服务器...
echo.
echo ============================================
echo   服务已启动！
echo   浏览器访问: http://localhost:8000
echo   管理员: admin / 123456
echo   按 Ctrl+C 停止服务
echo ============================================
echo.
uvicorn main:app --host 0.0.0.0 --port 8000

pause

# 金三角网吧收银管理系统

FastAPI + Vue 3 + SQL Server 网吧收银管理 B/S 系统。

## 快速部署（Windows）

### 前置条件
- Python 3.9+
- Node.js 18+
- SQL Server（本地或远程）
- ODBC Driver 17 for SQL Server

### 第一步：导入数据库

在 SSMS 中打开 `database/export.sql`，执行即可创建数据库和所有初始数据。

### 第二步：配置连接

编辑 `backend/.env`，修改数据库连接信息：

```env
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=GoldenTriangleCafe
DB_TRUSTED_CONNECTION=yes
```

### 第三步：启动

双击 `start.bat`，自动完成依赖安装、前端构建、服务启动。

浏览器访问 `http://localhost:8000`

## 开发模式

双击 `dev.bat`，前后端分别启动（后端 8000 + 前端 5173，支持热重载）。

## 默认账号

| 角色 | 账号 | 密码 |
|------|------|------|
| 超级管理员 | `admin` | `123456` |
| 收银员 | `cashier1` | `123456` |
| 会员 | `13800001111` | `123456` |

## 项目结构

```
├── start.bat              # 一键生产部署
├── dev.bat                # 开发模式
├── database/
│   └── export.sql         # 数据库导出（建库+建表+种子数据）
├── backend/
│   ├── main.py            # FastAPI 入口 + 静态文件服务
│   ├── config.py          # 数据库连接配置
│   ├── database.py        # pyodbc 连接 + dict 工具
│   ├── models/            # Pydantic 请求/响应模型
│   ├── dao/               # 数据访问层（纯 SQL + 参数化查询）
│   ├── services/          # 业务逻辑（计费引擎、认证）
│   └── routers/           # REST API 端点
└── frontend/
    ├── src/
    │   ├── api/           # Axios 封装
    │   ├── stores/        # Pinia 状态管理
    │   ├── router/        # Vue Router（含权限守卫）
    │   ├── components/    # 公共组件
    │   └── views/         # 页面（管理端 + 会员端）
    └── dist/              # 构建产物（生产模式由此加载）
```

## 技术栈

| 层 | 技术 |
|----|------|
| 数据库 | SQL Server |
| 后端 | FastAPI + pyodbc（纯 SQL，无 ORM） |
| 前端 | Vue 3 + Element Plus + Pinia |
| 构建 | Vite |

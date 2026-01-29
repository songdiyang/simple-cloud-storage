@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ============================================
REM 简单云盘 - 本地开发环境部署 (Windows)
REM Simple Cloud Storage - Local Dev Setup
REM ============================================

echo.
echo ============================================
echo   简单云盘 - 本地开发环境
echo   Simple Cloud Storage - Local Dev
echo ============================================
echo.

cd /d "%~dp0\.."

REM 1. Python 虚拟环境
echo [INFO] 配置 Python 环境 / Setting up Python...

if not exist "venv" (
    python -m venv venv
)

call venv\Scripts\activate.bat

pip install --upgrade pip -q
pip install -r requirements.txt -q
echo [OK] Python 依赖安装完成

REM 2. 数据库配置
echo.
echo 数据库选项 / Database options:
echo 1) 使用 SQLite（无需配置，推荐开发用）
echo 2) 使用 MySQL
echo 3) 跳过 / Skip
set /p db_choice="选择 / Choose [1/2/3]: "

if "%db_choice%"=="1" (
    set DB_ENGINE=sqlite
    echo [OK] 使用 SQLite 数据库
)

if "%db_choice%"=="2" (
    set /p DB_NAME="数据库名 / DB name [cloud_storage]: "
    if "!DB_NAME!"=="" set DB_NAME=cloud_storage
    set /p DB_USER="用户名 / Username [root]: "
    if "!DB_USER!"=="" set DB_USER=root
    set /p DB_PASSWORD="密码 / Password: "
    set /p DB_HOST="主机 / Host [localhost]: "
    if "!DB_HOST!"=="" set DB_HOST=localhost
    set /p DB_PORT="端口 / Port [3306]: "
    if "!DB_PORT!"=="" set DB_PORT=3306
    echo [OK] MySQL 配置完成
)

REM 3. 数据库迁移
echo.
echo [INFO] 迁移数据库 / Migrating database...
python manage.py migrate --run-syncdb
if %errorlevel% neq 0 (
    echo [ERROR] 数据库迁移失败
    pause
    exit /b 1
)
echo [OK] 数据库迁移完成

REM 4. 创建管理员
echo.
set /p create_admin="创建管理员账户? / Create admin? [y/n]: "
if /i "%create_admin%"=="y" (
    python manage.py createsuperuser
)

REM 5. 前端依赖
echo.
echo [INFO] 安装前端依赖 / Installing frontend...
cd frontend
where npm >nul 2>nul
if %errorlevel%==0 (
    npm install
    echo [OK] 前端依赖安装完成
) else (
    echo [WARN] npm 未安装，跳过前端
)
cd ..

REM 6. 完成
echo.
echo ============================================
echo   部署完成 / Setup Complete!
echo ============================================
echo.
echo 启动后端 / Start backend:
echo   python manage.py runserver
echo.
echo 启动前端 / Start frontend:
echo   cd frontend ^&^& npm start
echo.
echo 访问 / Access:
echo   前端 Frontend: http://localhost:3000
echo   后端 Backend:  http://localhost:8000/admin
echo.

pause

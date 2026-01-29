#!/bin/bash

# ============================================
# 简单云盘 - 本地开发环境部署
# Simple Cloud Storage - Local Dev Setup
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

print_banner() {
    echo ""
    echo "============================================"
    echo "  简单云盘 - 本地开发环境"
    echo "  Simple Cloud Storage - Local Dev"
    echo "============================================"
    echo ""
}

get_password() {
    local password
    read -sp "$1: " password
    echo ""
    echo "$password"
}

# 检测项目目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

print_banner

# ============================================
# 1. Python 虚拟环境
# ============================================
info "配置 Python 环境 / Setting up Python..."

if [ ! -d "venv" ]; then
    python3 -m venv venv || python -m venv venv
fi

if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

pip install --upgrade pip -q
pip install -r requirements.txt -q
success "Python 依赖安装完成 / Python dependencies installed"

# ============================================
# 2. 数据库配置
# ============================================
info "配置数据库 / Setting up database..."

echo ""
echo "数据库选项 / Database options:"
echo "1) 使用 SQLite（无需配置，推荐开发用）"
echo "2) 使用 MySQL"
echo "3) 跳过 / Skip"
read -p "选择 / Choose [1/2/3]: " db_choice

case "$db_choice" in
    1)
        export DB_ENGINE="sqlite"
        success "使用 SQLite 数据库 / Using SQLite"
        ;;
    2)
        read -p "数据库名 / DB name [cloud_storage]: " DB_NAME
        read -p "用户名 / Username [root]: " DB_USER
        DB_PASSWORD=$(get_password "密码 / Password")
        read -p "主机 / Host [localhost]: " DB_HOST
        read -p "端口 / Port [3306]: " DB_PORT
        
        export DB_NAME=${DB_NAME:-cloud_storage}
        export DB_USER=${DB_USER:-root}
        export DB_PASSWORD
        export DB_HOST=${DB_HOST:-localhost}
        export DB_PORT=${DB_PORT:-3306}
        
        success "MySQL 配置完成 / MySQL configured"
        ;;
    3)
        warning "跳过数据库配置 / Skipping database"
        ;;
esac

# ============================================
# 3. 数据库迁移
# ============================================
info "迁移数据库 / Migrating database..."

python manage.py migrate --run-syncdb
if [ $? -eq 0 ]; then
    success "数据库迁移完成 / Migration complete"
else
    error "数据库迁移失败 / Migration failed"
    exit 1
fi

# ============================================
# 4. 创建管理员
# ============================================
echo ""
read -p "创建管理员账户? / Create admin? [y/n]: " create_admin

if [[ "$create_admin" =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# ============================================
# 5. 前端依赖
# ============================================
info "安装前端依赖 / Installing frontend..."

cd frontend
if command -v npm &> /dev/null; then
    npm install -q 2>/dev/null || npm install
    success "前端依赖安装完成 / Frontend dependencies installed"
else
    warning "npm 未安装，跳过前端 / npm not found, skipping frontend"
fi
cd "$PROJECT_DIR"

# ============================================
# 6. 完成
# ============================================
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  部署完成 / Setup Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "启动后端 / Start backend:"
echo "  python manage.py runserver"
echo ""
echo "启动前端 / Start frontend:"
echo "  cd frontend && npm start"
echo ""
echo "访问 / Access:"
echo "  前端 Frontend: http://localhost:3000"
echo "  后端 Backend:  http://localhost:8000/admin"
echo ""

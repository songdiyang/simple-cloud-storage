#!/bin/bash

# ============================================
# 简单云盘 - 更新脚本
# Simple Cloud Storage - Update Script
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# 日志函数
info() { echo -e "${CYAN}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 获取项目目录
DEPLOY_DIR=$(cd "$(dirname "$0")/.." && pwd)

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  简单云盘更新 / Simple Cloud Update${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""
info "项目目录 / Project dir: $DEPLOY_DIR"

# 检查是否在正确目录
if [ ! -f "$DEPLOY_DIR/manage.py" ]; then
    error "未找到项目文件 / Project files not found"
    exit 1
fi

cd "$DEPLOY_DIR"

# 拉取最新代码
echo ""
info "拉取最新代码 / Pulling latest code..."
git pull origin main
if [ $? -ne 0 ]; then
    error "代码拉取失败 / Git pull failed"
    exit 1
fi
success "代码已更新 / Code updated"

# 更新后端依赖
echo ""
info "更新后端依赖 / Updating backend dependencies..."
source venv/bin/activate
pip install --prefer-binary -r requirements.txt --quiet 2>&1 | tail -3
success "后端依赖已更新 / Backend dependencies updated"

# 数据库迁移
echo ""
info "数据库迁移 / Database migration..."
python manage.py migrate --noinput
success "数据库已迁移 / Database migrated"

# 收集静态文件
python manage.py collectstatic --noinput --quiet

# 检查前端是否有更新
echo ""
read -p "更新前端? / Update frontend? [y/n]: " update_fe

if [[ "$update_fe" =~ ^[Yy]$ ]]; then
    if [ -d "frontend" ]; then
        cd frontend
        
        # 检查内存
        mem_gb=$(free -g 2>/dev/null | awk '/^Mem:/{print $2}')
        
        if [ -d "build" ] && [ "${mem_gb:-0}" -lt 2 ]; then
            warning "内存不足，建议本地构建 / Low memory, build locally recommended"
            read -p "仍要构建? / Build anyway? [y/n]: " build_anyway
            if [[ ! "$build_anyway" =~ ^[Yy]$ ]]; then
                cd "$DEPLOY_DIR"
            else
                export NODE_OPTIONS="--max-old-space-size=512"
                npm install --no-audit --no-fund --quiet 2>&1 | tail -3
                npm run build 2>&1 | tail -5
            fi
        else
            npm install --no-audit --no-fund --quiet 2>&1 | tail -3
            npm run build 2>&1 | tail -5
        fi
        
        cd "$DEPLOY_DIR"
        success "前端已更新 / Frontend updated"
    fi
fi

# 重启服务
echo ""
info "重启服务 / Restarting service..."
if systemctl is-active --quiet cloudstorage 2>/dev/null; then
    sudo systemctl restart cloudstorage
    success "服务已重启 / Service restarted"
else
    warning "未找到 cloudstorage 服务 / Service not found"
    echo "请手动重启 / Please restart manually"
fi

# 完成
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  更新完成 / Update Complete${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

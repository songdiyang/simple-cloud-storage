#!/bin/bash

# ============================================
# 简单云盘 - 一键部署脚本
# Simple Cloud Storage - One-Click Deploy
# 支持: Ubuntu/Debian/CentOS/RHEL/Fedora/Arch
# 仅支持 Linux 系统 / Linux Only
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 全局变量
DEPLOY_DIR=""
OS_TYPE=""
PKG_MANAGER=""
PKG_INSTALL=""
SERVICE_MANAGER=""

# ============================================
# 系统检查 - 仅支持 Linux
# ============================================
check_linux_only() {
    case "$(uname -s)" in
        Linux*) return 0 ;;
        Darwin*)
            echo -e "${RED}错误: 不支持 macOS / Error: macOS not supported${NC}"
            exit 1 ;;
        MINGW*|CYGWIN*|MSYS*)
            echo -e "${RED}错误: 不支持 Windows / Error: Windows not supported${NC}"
            exit 1 ;;
        *)
            echo -e "${RED}错误: 未知系统 / Unknown OS${NC}"
            exit 1 ;;
    esac
}

check_linux_only

# 艺术字
print_cloud_art() {
    echo -e "${GREEN}"
    echo "    ██████╗██╗      ██████╗ ██╗   ██╗██████╗ "
    echo "   ██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗"
    echo "   ██║     ██║     ██║   ██║██║   ██║██║  ██║"
    echo "   ██║     ██║     ██║   ██║██║   ██║██║  ██║"
    echo "   ╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝"
    echo "    ╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ "
    echo ""
    echo "   ☁️  简单云盘部署成功 / Deploy Success  ☁️"
    echo -e "${NC}"
}

print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════╗"
    echo "║     简单云盘 - 一键部署脚本                ║"
    echo "║     Simple Cloud Storage - One-Click       ║"
    echo "╚════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 日志函数
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
step() { echo -e "${CYAN}[STEP]${NC} $1"; }

# ============================================
# 获取主机IP
# ============================================
get_host_ip() {
    local ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    [ -z "$ip" ] && ip=$(ip route get 1 2>/dev/null | awk '{print $7;exit}')
    [ -z "$ip" ] && ip="127.0.0.1"
    echo "$ip"
}

# ============================================
# 检测 Linux 发行版
# ============================================
detect_os() {
    step "检测操作系统 / Detecting OS..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME=$ID
    elif [ -f /etc/redhat-release ]; then
        OS_NAME="rhel"
    elif [ -f /etc/debian_version ]; then
        OS_NAME="debian"
    else
        error "不支持的系统 / Unsupported OS"
        exit 1
    fi
    
    case "$OS_NAME" in
        ubuntu|debian|linuxmint|pop)
            OS_TYPE="debian"
            PKG_MANAGER="apt"
            PKG_INSTALL="apt install -y"
            PKG_UPDATE="apt update"
            ;;
        centos|rhel|rocky|almalinux)
            OS_TYPE="rhel"
            PKG_MANAGER="yum"
            PKG_INSTALL="yum install -y"
            PKG_UPDATE="yum makecache"
            command -v dnf &>/dev/null && { PKG_MANAGER="dnf"; PKG_INSTALL="dnf install -y"; PKG_UPDATE="dnf makecache"; }
            ;;
        fedora)
            OS_TYPE="fedora"
            PKG_MANAGER="dnf"
            PKG_INSTALL="dnf install -y"
            PKG_UPDATE="dnf makecache"
            ;;
        arch|manjaro)
            OS_TYPE="arch"
            PKG_MANAGER="pacman"
            PKG_INSTALL="pacman -S --noconfirm"
            PKG_UPDATE="pacman -Sy"
            ;;
        *)
            error "不支持: $OS_NAME / Unsupported: $OS_NAME"
            exit 1
            ;;
    esac
    
    [ -x "$(command -v systemctl)" ] && SERVICE_MANAGER="systemd"
    success "系统: $OS_NAME | 包管理: $PKG_MANAGER"
}

# ============================================
# 安装依赖（无Nginx）
# ============================================
install_packages() {
    step "安装依赖 / Installing dependencies..."
    
    sudo $PKG_UPDATE
    
    case "$OS_TYPE" in
        debian)
            sudo $PKG_INSTALL python3 python3-pip python3-venv git curl
            sudo $PKG_INSTALL mysql-server mysql-client libmysqlclient-dev 2>/dev/null || \
            sudo $PKG_INSTALL mariadb-server mariadb-client libmariadb-dev
            if ! command -v node &>/dev/null; then
                curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                sudo $PKG_INSTALL nodejs
            fi
            ;;
        rhel|fedora)
            sudo $PKG_INSTALL python3 python3-pip git curl
            sudo $PKG_INSTALL mysql-server mysql-devel 2>/dev/null || \
            sudo $PKG_INSTALL mariadb-server mariadb-devel
            if ! command -v node &>/dev/null; then
                curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
                sudo $PKG_INSTALL nodejs
            fi
            sudo $PKG_INSTALL python3-virtualenv 2>/dev/null || sudo pip3 install virtualenv
            ;;
        arch)
            sudo $PKG_INSTALL python python-pip git curl nodejs npm mariadb
            ;;
    esac
    
    success "依赖安装完成 / Dependencies installed"
}

# ============================================
# 配置 MySQL 数据库
# ============================================
setup_database() {
    step "配置数据库 / Database Setup"
    
    echo ""
    echo "数据库选项 / Database Options:"
    echo "  1) 创建新数据库 / Create new"
    echo "  2) 使用已有数据库 / Use existing"
    echo "  3) 跳过 / Skip"
    read -p "选择 [1/2/3]: " db_choice
    
    case "$db_choice" in
        1)
            # 启动MySQL
            sudo systemctl start mysql 2>/dev/null || sudo systemctl start mariadb 2>/dev/null
            sudo systemctl enable mysql 2>/dev/null || sudo systemctl enable mariadb 2>/dev/null
            
            read -p "数据库名 / DB name [cloud_storage]: " DB_NAME
            DB_NAME=${DB_NAME:-cloud_storage}
            read -p "用户名 / Username [cloud_user]: " DB_USER
            DB_USER=${DB_USER:-cloud_user}
            read -sp "密码 / Password: " DB_PASS
            echo ""
            
            sudo mysql -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4;"
            sudo mysql -e "CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';"
            sudo mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';"
            sudo mysql -e "FLUSH PRIVILEGES;"
            
            # 写入.env
            cat > "$DEPLOY_DIR/.env" << EOF
DEBUG=False
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
DATABASE_ENGINE=mysql
DATABASE_NAME=$DB_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASS
DATABASE_HOST=localhost
DATABASE_PORT=3306
ALLOWED_HOSTS=*
EOF
            success "数据库创建完成 / Database created"
            ;;
        2)
            read -p "数据库名 / DB name: " DB_NAME
            read -p "用户名 / Username: " DB_USER
            read -sp "密码 / Password: " DB_PASS
            echo ""
            read -p "主机 / Host [localhost]: " DB_HOST
            DB_HOST=${DB_HOST:-localhost}
            
            cat > "$DEPLOY_DIR/.env" << EOF
DEBUG=False
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
DATABASE_ENGINE=mysql
DATABASE_NAME=$DB_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASS
DATABASE_HOST=$DB_HOST
DATABASE_PORT=3306
ALLOWED_HOSTS=*
EOF
            success "数据库配置完成 / Database configured"
            ;;
        3)
            warning "跳过数据库配置 / Skipping database"
            [ ! -f "$DEPLOY_DIR/.env" ] && cp "$DEPLOY_DIR/.env.example" "$DEPLOY_DIR/.env" 2>/dev/null
            ;;
    esac
}

# ============================================
# 配置存储
# ============================================
setup_storage() {
    step "配置存储 / Storage Setup"
    
    echo ""
    echo "存储选项 / Storage Options:"
    echo "  1) 本地存储 / Local storage"
    echo "  2) OpenStack Swift（需4GB+内存）"
    echo "  3) 跳过 / Skip"
    read -p "选择 [1/2/3]: " storage_choice
    
    case "$storage_choice" in
        1)
            mkdir -p "$DEPLOY_DIR/media/uploads"
            sed -i 's/STORAGE_BACKEND=.*/STORAGE_BACKEND=local/' "$DEPLOY_DIR/.env" 2>/dev/null || \
            echo "STORAGE_BACKEND=local" >> "$DEPLOY_DIR/.env"
            success "本地存储配置完成 / Local storage configured"
            ;;
        2)
            local mem_gb=$(free -g | awk '/^Mem:/{print $2}')
            if [ "${mem_gb:-0}" -lt 4 ]; then
                warning "内存不足4GB，Swift可能失败 / Less than 4GB RAM"
                read -p "继续? [y/n]: " continue_swift
                [[ ! "$continue_swift" =~ ^[Yy]$ ]] && return
            fi
            
            info "安装 DevStack + Swift..."
            cd /opt
            sudo git clone https://opendev.org/openstack/devstack 2>/dev/null || true
            cd devstack
            
            cat > local.conf << EOF
[[local|localrc]]
ADMIN_PASSWORD=secret
DATABASE_PASSWORD=secret
RABBIT_PASSWORD=secret
SERVICE_PASSWORD=secret
disable_all_services
enable_service key mysql s-proxy s-object s-container s-account
SWIFT_HASH=66a3d6b56c1f479c8b4e70ab5c2000f5
EOF
            ./stack.sh
            
            echo "STORAGE_BACKEND=swift" >> "$DEPLOY_DIR/.env"
            success "Swift 安装完成 / Swift installed"
            ;;
        3)
            warning "跳过存储配置 / Skipping storage"
            ;;
    esac
}

# ============================================
# 部署后端
# ============================================
deploy_backend() {
    step "部署后端 / Deploying backend..."
    
    cd "$DEPLOY_DIR"
    
    # 创建虚拟环境
    python3 -m venv venv
    source venv/bin/activate
    
    # 安装依赖（使用预编译包）
    pip install --prefer-binary -r requirements.txt --quiet
    
    # 数据库迁移
    python manage.py migrate --noinput
    
    # 静态文件
    python manage.py collectstatic --noinput
    
    success "后端部署完成 / Backend deployed"
}

# ============================================
# 配置管理员
# ============================================
setup_admin() {
    step "配置管理员 / Admin Setup"
    
    echo ""
    read -p "允许用户自行注册? / Allow registration? [y/n]: " allow_reg
    
    if [[ "$allow_reg" =~ ^[Nn]$ ]]; then
        echo ""
        info "创建管理员账户 / Create admin account"
        read -p "用户名 / Username [admin]: " ADMIN_USER
        ADMIN_USER=${ADMIN_USER:-admin}
        read -p "邮箱 / Email: " ADMIN_EMAIL
        read -sp "密码 / Password: " ADMIN_PASS
        echo ""
        
        cd "$DEPLOY_DIR"
        source venv/bin/activate
        
        python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$ADMIN_USER').exists():
    User.objects.create_superuser('$ADMIN_USER', '$ADMIN_EMAIL', '$ADMIN_PASS')
    print('Admin created')
EOF
        success "管理员创建完成 / Admin created"
    fi
}

# ============================================
# 部署前端
# ============================================
deploy_frontend() {
    step "部署前端 / Deploying frontend..."
    
    cd "$DEPLOY_DIR/frontend"
    
    # 检查内存，低于4GB启用Swap
    local mem_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [ "${mem_gb:-0}" -lt 4 ]; then
        warning "内存较低，启用Swap / Low memory, enabling swap..."
        if [ ! -f /swapfile ]; then
            sudo fallocate -l 2G /swapfile 2>/dev/null || \
            sudo dd if=/dev/zero of=/swapfile bs=1M count=2048 status=progress
            sudo chmod 600 /swapfile
            sudo mkswap /swapfile
            sudo swapon /swapfile
        fi
        export NODE_OPTIONS="--max-old-space-size=512"
    fi
    
    npm install --no-audit --no-fund 2>&1 | tail -5
    npm run build 2>&1 | tail -10
    
    success "前端构建完成 / Frontend built"
}

# ============================================
# 启动服务
# ============================================
start_service() {
    step "启动服务 / Starting service..."
    
    cd "$DEPLOY_DIR"
    source venv/bin/activate
    
    local HOST_IP=$(get_host_ip)
    local PORT=8000
    
    # 创建systemd服务
    if [ "$SERVICE_MANAGER" = "systemd" ]; then
        sudo tee /etc/systemd/system/cloudstorage.service > /dev/null << EOF
[Unit]
Description=Simple Cloud Storage
After=network.target mysql.service

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$DEPLOY_DIR
ExecStart=$DEPLOY_DIR/venv/bin/gunicorn cloud_storage.wsgi:application --bind 0.0.0.0:$PORT --workers 2
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable cloudstorage
        sudo systemctl restart cloudstorage
        
        success "服务已启动 / Service started"
    else
        # 非systemd直接启动
        nohup $DEPLOY_DIR/venv/bin/gunicorn cloud_storage.wsgi:application --bind 0.0.0.0:$PORT --workers 2 > /dev/null 2>&1 &
        success "服务已启动 (后台) / Service started (background)"
    fi
}

# ============================================
# 显示访问信息
# ============================================
print_service_info() {
    local HOST_IP=$(get_host_ip)
    local PORT=8000
    
    echo ""
    echo -e "${CYAN}============================================${NC}"
    echo -e "${CYAN}  访问地址 / Access URL${NC}"
    echo -e "${CYAN}============================================${NC}"
    echo ""
    echo -e "  ${GREEN}云存储服务 / Cloud Storage:${NC}"
    echo "    http://$HOST_IP:$PORT/"
    echo ""
    echo -e "  ${GREEN}管理后台 / Admin:${NC}"
    echo "    http://$HOST_IP:$PORT/admin/"
    echo ""
}

# ============================================
# 主流程
# ============================================
main() {
    print_banner
    
    # 获取当前目录
    DEPLOY_DIR=$(cd "$(dirname "$0")/.." && pwd)
    info "部署目录 / Deploy dir: $DEPLOY_DIR"
    
    # 检测系统
    detect_os
    
    # 安装依赖
    echo ""
    read -p "安装系统依赖? [y/n]: " install_deps
    [[ "$install_deps" =~ ^[Yy]$ ]] && install_packages
    
    # 配置数据库
    echo ""
    setup_database
    
    # 配置存储
    echo ""
    setup_storage
    
    # 部署后端
    echo ""
    deploy_backend
    
    # 配置管理员
    echo ""
    setup_admin
    
    # 部署前端
    echo ""
    read -p "构建前端? [y/n]: " build_fe
    [[ "$build_fe" =~ ^[Yy]$ ]] && deploy_frontend
    
    # 启动服务
    echo ""
    read -p "启动服务? [y/n]: " start_svc
    [[ "$start_svc" =~ ^[Yy]$ ]] && start_service
    
    # 完成
    echo ""
    print_cloud_art
    print_service_info
    success "部署完成! / Deployment Complete!"
    echo ""
}

main "$@"

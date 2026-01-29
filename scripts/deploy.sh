#!/bin/bash

# ============================================
# 简单云盘 - 自动部署脚本
# Simple Cloud Storage - Auto Deploy Script
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 艺术字 "云"
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

# 打印信息
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo -e "${RED}[错误]${NC} $2"
}

# 询问是否跳过
ask_skip() {
    read -p "$1 [y/n/skip]: " choice
    case "$choice" in
        y|Y ) return 0 ;;
        n|N ) return 1 ;;
        skip|SKIP|s|S ) return 2 ;;
        * ) return 1 ;;
    esac
}

# 获取密码输入
get_password() {
    local prompt="$1"
    local password
    read -sp "$prompt: " password
    echo ""
    echo "$password"
}

# ============================================
# 1. 检测系统环境
# ============================================
check_system() {
    info "检测系统环境 / Checking system environment..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        info "检测到系统 / Detected OS: $OS"
    else
        error "Cannot detect OS" "无法检测操作系统"
        exit 1
    fi
}

# ============================================
# 2. 安装基础依赖
# ============================================
install_dependencies() {
    info "安装基础依赖 / Installing dependencies..."
    
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv nginx mysql-server nodejs npm git
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip nginx mysql-server nodejs npm git
    else
        error "Package manager not found" "找不到包管理器"
        exit 1
    fi
    
    success "依赖安装完成 / Dependencies installed"
}

# ============================================
# 3. 配置 MySQL 数据库
# ============================================
configure_mysql() {
    info "配置 MySQL 数据库 / Configuring MySQL..."
    
    echo ""
    echo "MySQL 配置选项 / MySQL Configuration:"
    echo "1. 新建数据库 / Create new database"
    echo "2. 使用已有数据库 / Use existing database"
    echo "3. 跳过 / Skip"
    read -p "请选择 / Choose [1/2/3]: " mysql_choice
    
    case "$mysql_choice" in
        1)
            # 新建数据库
            DB_NAME="cloud_storage"
            DB_USER="clouduser"
            
            DB_PASSWORD=$(get_password "请输入新数据库密码 / Enter new database password")
            
            if [ -z "$DB_PASSWORD" ]; then
                error "Password cannot be empty" "密码不能为空"
                return 1
            fi
            
            # 获取MySQL root密码
            MYSQL_ROOT_PASS=$(get_password "请输入 MySQL root 密码 / Enter MySQL root password")
            
            # 创建数据库和用户
            mysql -u root -p"$MYSQL_ROOT_PASS" <<EOF 2>/dev/null
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF
            
            if [ $? -eq 0 ]; then
                success "数据库创建成功 / Database created successfully"
                export DB_NAME DB_USER DB_PASSWORD
                export DB_HOST="localhost"
                export DB_PORT="3306"
            else
                error "Failed to create database" "数据库创建失败"
                error "Please check MySQL root password" "请检查 MySQL root 密码是否正确"
                return 1
            fi
            ;;
        2)
            # 使用已有数据库
            read -p "数据库名 / Database name: " DB_NAME
            read -p "数据库用户 / Database user: " DB_USER
            DB_PASSWORD=$(get_password "数据库密码 / Database password")
            read -p "数据库主机 / Database host [localhost]: " DB_HOST
            DB_HOST=${DB_HOST:-localhost}
            read -p "数据库端口 / Database port [3306]: " DB_PORT
            DB_PORT=${DB_PORT:-3306}
            
            # 测试连接
            mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "USE $DB_NAME;" 2>/dev/null
            
            if [ $? -eq 0 ]; then
                success "数据库连接成功 / Database connection successful"
                export DB_NAME DB_USER DB_PASSWORD DB_HOST DB_PORT
            else
                error "Failed to connect to database" "数据库连接失败"
                error "Please check database credentials" "请检查数据库凭据是否正确"
                return 1
            fi
            ;;
        3)
            warning "跳过 MySQL 配置 / Skipping MySQL configuration"
            return 2
            ;;
    esac
}

# ============================================
# 4. 配置 OpenStack Swift
# ============================================
configure_swift() {
    info "配置 OpenStack Swift / Configuring OpenStack Swift..."
    
    echo ""
    echo "Swift 配置选项 / Swift Configuration:"
    echo "1. 配置 Swift / Configure Swift"
    echo "2. 使用本地存储 / Use local storage"
    echo "3. 跳过 / Skip"
    read -p "请选择 / Choose [1/2/3]: " swift_choice
    
    case "$swift_choice" in
        1)
            read -p "Keystone Auth URL (e.g., http://host/identity/v3): " OS_AUTH_URL
            read -p "Username: " OS_USERNAME
            OS_PASSWORD=$(get_password "Password")
            read -p "Project Name: " OS_PROJECT_NAME
            read -p "User Domain ID [default]: " OS_USER_DOMAIN_ID
            OS_USER_DOMAIN_ID=${OS_USER_DOMAIN_ID:-default}
            read -p "Project Domain ID [default]: " OS_PROJECT_DOMAIN_ID
            OS_PROJECT_DOMAIN_ID=${OS_PROJECT_DOMAIN_ID:-default}
            read -p "Region Name [RegionOne]: " OS_REGION_NAME
            OS_REGION_NAME=${OS_REGION_NAME:-RegionOne}
            
            # 测试 Swift 连接
            export OS_AUTH_URL OS_USERNAME OS_PASSWORD OS_PROJECT_NAME
            export OS_USER_DOMAIN_ID OS_PROJECT_DOMAIN_ID OS_REGION_NAME
            
            if command -v swift &> /dev/null; then
                swift stat 2>/dev/null
                if [ $? -eq 0 ]; then
                    success "Swift 连接成功 / Swift connection successful"
                else
                    error "Failed to connect to Swift" "Swift 连接失败"
                    error "Please check Swift credentials" "请检查 Swift 凭据是否正确"
                    return 1
                fi
            else
                warning "swift 命令未安装，跳过连接测试 / swift command not installed, skipping test"
            fi
            ;;
        2)
            info "使用本地存储模式 / Using local storage mode"
            export STORAGE_BACKEND="local"
            ;;
        3)
            warning "跳过 Swift 配置 / Skipping Swift configuration"
            return 2
            ;;
    esac
}

# ============================================
# 5. 部署后端
# ============================================
deploy_backend() {
    info "部署后端服务 / Deploying backend..."
    
    DEPLOY_DIR=${DEPLOY_DIR:-$(pwd)}
    cd "$DEPLOY_DIR"
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # 安装依赖
    pip install -r requirements.txt
    pip install gunicorn
    
    # 生成 SECRET_KEY
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    
    # 迁移数据库
    python manage.py migrate 2>/dev/null
    if [ $? -ne 0 ]; then
        error "Database migration failed" "数据库迁移失败"
        error "Please check database configuration" "请检查数据库配置"
        return 1
    fi
    
    # 收集静态文件
    python manage.py collectstatic --noinput
    
    success "后端部署完成 / Backend deployed"
}

# ============================================
# 6. 配置用户注册
# ============================================
configure_registration() {
    info "配置用户注册 / Configuring user registration..."
    
    echo ""
    read -p "是否允许用户注册？/ Allow user registration? [y/n]: " allow_reg
    
    if [[ "$allow_reg" =~ ^[Yy]$ ]]; then
        export ALLOW_REGISTRATION="true"
        success "已启用用户注册 / User registration enabled"
    else
        export ALLOW_REGISTRATION="false"
        warning "已禁用用户注册 / User registration disabled"
        
        echo ""
        info "请创建管理员账户 / Please create admin account"
        read -p "管理员用户名 / Admin username: " ADMIN_USER
        ADMIN_PASSWORD=$(get_password "管理员密码 / Admin password")
        read -p "管理员邮箱 / Admin email: " ADMIN_EMAIL
        
        # 创建超级用户
        source venv/bin/activate
        echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$ADMIN_USER', '$ADMIN_EMAIL', '$ADMIN_PASSWORD') if not User.objects.filter(username='$ADMIN_USER').exists() else None" | python manage.py shell
        
        if [ $? -eq 0 ]; then
            success "管理员账户创建成功 / Admin account created"
        else
            error "Failed to create admin account" "管理员账户创建失败"
        fi
    fi
}

# ============================================
# 7. 部署前端
# ============================================
deploy_frontend() {
    info "部署前端 / Deploying frontend..."
    
    cd frontend
    
    npm install 2>/dev/null
    if [ $? -ne 0 ]; then
        error "npm install failed" "npm 安装失败"
        error "Please check Node.js installation" "请检查 Node.js 是否正确安装"
        return 1
    fi
    
    npm run build 2>/dev/null
    if [ $? -ne 0 ]; then
        error "npm build failed" "npm 构建失败"
        error "Please check frontend code" "请检查前端代码"
        return 1
    fi
    
    cd ..
    success "前端部署完成 / Frontend deployed"
}

# ============================================
# 8. 配置 Nginx
# ============================================
configure_nginx() {
    info "配置 Nginx / Configuring Nginx..."
    
    read -p "请输入域名或IP / Enter domain or IP: " SERVER_NAME
    
    NGINX_CONF="/etc/nginx/sites-available/cloudstorage"
    
    sudo tee $NGINX_CONF > /dev/null <<EOF
server {
    listen 80;
    server_name $SERVER_NAME;

    location / {
        root $(pwd)/frontend/build;
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
    }

    location /static/ {
        alias $(pwd)/staticfiles/;
    }

    location /media/ {
        alias $(pwd)/media/;
    }
}
EOF

    sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
    sudo nginx -t 2>/dev/null
    
    if [ $? -eq 0 ]; then
        sudo systemctl restart nginx
        success "Nginx 配置完成 / Nginx configured"
    else
        error "Nginx configuration error" "Nginx 配置错误"
        error "Please check nginx config file" "请检查 nginx 配置文件"
        return 1
    fi
}

# ============================================
# 9. 配置 Gunicorn 服务
# ============================================
configure_gunicorn() {
    info "配置 Gunicorn 服务 / Configuring Gunicorn service..."
    
    SERVICE_FILE="/etc/systemd/system/cloudstorage.service"
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Simple Cloud Storage Backend
After=network.target

[Service]
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
Environment="DB_NAME=${DB_NAME:-cloud_storage}"
Environment="DB_USER=${DB_USER:-clouduser}"
Environment="DB_PASSWORD=${DB_PASSWORD:-}"
Environment="DB_HOST=${DB_HOST:-localhost}"
Environment="DB_PORT=${DB_PORT:-3306}"
Environment="SECRET_KEY=${SECRET_KEY}"
ExecStart=$(pwd)/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 cloud_storage.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl start cloudstorage
    sudo systemctl enable cloudstorage
    
    if [ $? -eq 0 ]; then
        success "Gunicorn 服务配置完成 / Gunicorn service configured"
    else
        error "Failed to start Gunicorn service" "Gunicorn 服务启动失败"
        return 1
    fi
}

# ============================================
# 主流程
# ============================================
main() {
    echo ""
    echo "============================================"
    echo "  简单云盘 - 自动部署脚本"
    echo "  Simple Cloud Storage - Auto Deploy"
    echo "============================================"
    echo ""
    
    # 1. 检测系统
    check_system
    
    # 2. 安装依赖
    echo ""
    read -p "是否安装基础依赖？/ Install dependencies? [y/n]: " install_deps
    if [[ "$install_deps" =~ ^[Yy]$ ]]; then
        install_dependencies
    fi
    
    # 3. 配置 MySQL
    echo ""
    configure_mysql
    mysql_status=$?
    
    # 4. 配置 Swift
    echo ""
    configure_swift
    swift_status=$?
    
    # 5. 部署后端
    echo ""
    deploy_backend || exit 1
    
    # 6. 配置注册
    echo ""
    configure_registration
    
    # 7. 部署前端
    echo ""
    deploy_frontend || exit 1
    
    # 8. 配置 Nginx
    echo ""
    read -p "是否配置 Nginx？/ Configure Nginx? [y/n]: " config_nginx
    if [[ "$config_nginx" =~ ^[Yy]$ ]]; then
        configure_nginx
    fi
    
    # 9. 配置 Gunicorn
    echo ""
    read -p "是否配置 Gunicorn 服务？/ Configure Gunicorn? [y/n]: " config_gunicorn
    if [[ "$config_gunicorn" =~ ^[Yy]$ ]]; then
        configure_gunicorn
    fi
    
    # 完成
    echo ""
    print_cloud_art
    echo ""
    info "访问地址 / Access URL: http://${SERVER_NAME:-localhost}"
    info "管理后台 / Admin Panel: http://${SERVER_NAME:-localhost}/admin"
    echo ""
}

# 运行主流程
main "$@"

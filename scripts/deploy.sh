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

# ============================================
# 系统检查 - 仅支持 Linux
# ============================================
check_linux_only() {
    case "$(uname -s)" in
        Linux*)
            return 0
            ;;
        Darwin*)
            echo -e "${RED}============================================${NC}"
            echo -e "${RED}  错误: 不支持 macOS 系统${NC}"
            echo -e "${RED}  Error: macOS is not supported${NC}"
            echo -e "${RED}============================================${NC}"
            echo ""
            echo -e "${YELLOW}此脚本仅支持 Linux 服务器部署。${NC}"
            echo -e "${YELLOW}This script only supports Linux server deployment.${NC}"
            echo ""
            echo "建议 / Suggestion:"
            echo "  - 使用 Ubuntu/Debian/CentOS 云服务器"
            echo "  - Use Ubuntu/Debian/CentOS cloud server"
            exit 1
            ;;
        MINGW*|CYGWIN*|MSYS*)
            echo -e "${RED}============================================${NC}"
            echo -e "${RED}  错误: 不支持 Windows 系统${NC}"
            echo -e "${RED}  Error: Windows is not supported${NC}"
            echo -e "${RED}============================================${NC}"
            echo ""
            echo -e "${YELLOW}此脚本仅支持 Linux 服务器部署。${NC}"
            echo -e "${YELLOW}This script only supports Linux server deployment.${NC}"
            echo ""
            echo "建议 / Suggestion:"
            echo "  - 使用 Ubuntu/Debian/CentOS 云服务器"
            echo "  - 或使用 WSL2 (Windows Subsystem for Linux)"
            exit 1
            ;;
        *)
            echo -e "${RED}错误: 未知操作系统 / Unknown OS${NC}"
            exit 1
            ;;
    esac
}

# 立即检查系统
check_linux_only

# 全局变量
DEPLOY_DIR=""
OS_TYPE=""
PKG_MANAGER=""
PKG_INSTALL=""
SERVICE_MANAGER=""

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
error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo -e "${RED}[错误]${NC} $2"
}
step() { echo -e "${CYAN}[STEP]${NC} $1"; }

# 密码输入
get_password() {
    local password
    read -sp "$1: " password
    echo ""
    echo "$password"
}

# ============================================
# 检测 Linux 发行版
# ============================================
detect_os() {
    step "检测操作系统 / Detecting OS..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME=$ID
        OS_VERSION=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        OS_NAME="rhel"
    elif [ -f /etc/debian_version ]; then
        OS_NAME="debian"
    else
        error "Unsupported OS" "不支持的操作系统"
        exit 1
    fi
    
    case "$OS_NAME" in
        ubuntu|debian|linuxmint|pop)
            OS_TYPE="debian"
            PKG_MANAGER="apt"
            PKG_INSTALL="apt install -y"
            PKG_UPDATE="apt update"
            ;;
        centos|rhel|rocky|almalinux|ol)
            OS_TYPE="rhel"
            PKG_MANAGER="yum"
            PKG_INSTALL="yum install -y"
            PKG_UPDATE="yum makecache"
            if command -v dnf &> /dev/null; then
                PKG_MANAGER="dnf"
                PKG_INSTALL="dnf install -y"
                PKG_UPDATE="dnf makecache"
            fi
            ;;
        fedora)
            OS_TYPE="fedora"
            PKG_MANAGER="dnf"
            PKG_INSTALL="dnf install -y"
            PKG_UPDATE="dnf makecache"
            ;;
        arch|manjaro|endeavouros)
            OS_TYPE="arch"
            PKG_MANAGER="pacman"
            PKG_INSTALL="pacman -S --noconfirm"
            PKG_UPDATE="pacman -Sy"
            ;;
        opensuse*|sles)
            OS_TYPE="suse"
            PKG_MANAGER="zypper"
            PKG_INSTALL="zypper install -y"
            PKG_UPDATE="zypper refresh"
            ;;
        alpine)
            OS_TYPE="alpine"
            PKG_MANAGER="apk"
            PKG_INSTALL="apk add"
            PKG_UPDATE="apk update"
            ;;
        *)
            error "Unsupported distribution: $OS_NAME" "不支持的发行版: $OS_NAME"
            exit 1
            ;;
    esac
    
    # 检测服务管理器
    if command -v systemctl &> /dev/null; then
        SERVICE_MANAGER="systemd"
    elif command -v service &> /dev/null; then
        SERVICE_MANAGER="sysvinit"
    elif command -v rc-service &> /dev/null; then
        SERVICE_MANAGER="openrc"
    fi
    
    success "系统: $OS_NAME ($OS_TYPE) | 包管理: $PKG_MANAGER | 服务: $SERVICE_MANAGER"
}

# ============================================
# 安装依赖
# ============================================
install_packages() {
    step "安装依赖包 / Installing packages..."
    
    sudo $PKG_UPDATE
    
    case "$OS_TYPE" in
        debian)
            sudo $PKG_INSTALL python3 python3-pip python3-venv nginx git curl
            # MySQL
            sudo $PKG_INSTALL mysql-server mysql-client libmysqlclient-dev || \
            sudo $PKG_INSTALL mariadb-server mariadb-client libmariadb-dev
            # Node.js
            if ! command -v node &> /dev/null; then
                curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                sudo $PKG_INSTALL nodejs
            fi
            ;;
        rhel|fedora)
            sudo $PKG_INSTALL python3 python3-pip nginx git curl
            # MySQL
            sudo $PKG_INSTALL mysql-server mysql-devel || \
            sudo $PKG_INSTALL mariadb-server mariadb-devel
            # Node.js
            if ! command -v node &> /dev/null; then
                curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
                sudo $PKG_INSTALL nodejs
            fi
            # Python venv
            sudo $PKG_INSTALL python3-virtualenv || sudo pip3 install virtualenv
            ;;
        arch)
            sudo $PKG_INSTALL python python-pip nginx git curl nodejs npm
            sudo $PKG_INSTALL mariadb
            ;;
        suse)
            sudo $PKG_INSTALL python3 python3-pip nginx git curl nodejs npm
            sudo $PKG_INSTALL mariadb mariadb-client
            ;;
        alpine)
            sudo $PKG_INSTALL python3 py3-pip nginx git curl nodejs npm
            sudo $PKG_INSTALL mariadb mariadb-client
            ;;
    esac
    
    success "依赖安装完成 / Dependencies installed"
}

# ============================================
# 启动/停止服务 - 跨平台
# ============================================
service_start() {
    local svc=$1
    case "$SERVICE_MANAGER" in
        systemd) sudo systemctl start $svc ;;
        sysvinit) sudo service $svc start ;;
        openrc) sudo rc-service $svc start ;;
    esac
}

service_stop() {
    local svc=$1
    case "$SERVICE_MANAGER" in
        systemd) sudo systemctl stop $svc 2>/dev/null || true ;;
        sysvinit) sudo service $svc stop 2>/dev/null || true ;;
        openrc) sudo rc-service $svc stop 2>/dev/null || true ;;
    esac
}

service_enable() {
    local svc=$1
    case "$SERVICE_MANAGER" in
        systemd) sudo systemctl enable $svc ;;
        sysvinit) sudo update-rc.d $svc defaults 2>/dev/null || sudo chkconfig $svc on 2>/dev/null || true ;;
        openrc) sudo rc-update add $svc default ;;
    esac
}

service_restart() {
    local svc=$1
    case "$SERVICE_MANAGER" in
        systemd) sudo systemctl restart $svc ;;
        sysvinit) sudo service $svc restart ;;
        openrc) sudo rc-service $svc restart ;;
    esac
}

# ============================================
# 配置 MySQL/MariaDB
# ============================================
setup_database() {
    step "配置数据库 / Setting up database..."
    
    echo ""
    echo "数据库配置 / Database Setup:"
    echo "1) 自动创建新数据库 / Auto create new"
    echo "2) 使用已有数据库 / Use existing"
    echo "3) 跳过 / Skip"
    read -p "选择 / Choose [1/2/3]: " db_choice
    
    case "$db_choice" in
        1)
            # 启动MySQL/MariaDB
            local mysql_svc="mysql"
            if ! service_start mysql 2>/dev/null; then
                mysql_svc="mariadb"
                service_start mariadb
            fi
            service_enable $mysql_svc
            
            export DB_NAME="cloud_storage"
            export DB_USER="clouduser"
            export DB_HOST="localhost"
            export DB_PORT="3306"
            
            DB_PASSWORD=$(get_password "设置数据库密码 / Set DB password")
            export DB_PASSWORD
            
            MYSQL_ROOT_PASS=$(get_password "MySQL root 密码 / MySQL root password (留空则无密码)")
            
            # 创建数据库
            local mysql_cmd="mysql -u root"
            [ -n "$MYSQL_ROOT_PASS" ] && mysql_cmd="mysql -u root -p$MYSQL_ROOT_PASS"
            
            $mysql_cmd <<EOF 2>/dev/null
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF
            if [ $? -eq 0 ]; then
                success "数据库创建成功 / Database created"
            else
                error "Database creation failed" "数据库创建失败"
                error "Check MySQL root password" "请检查 MySQL root 密码"
                return 1
            fi
            ;;
        2)
            read -p "数据库名 / DB name: " DB_NAME
            read -p "用户名 / Username: " DB_USER
            DB_PASSWORD=$(get_password "密码 / Password")
            read -p "主机 / Host [localhost]: " DB_HOST
            read -p "端口 / Port [3306]: " DB_PORT
            export DB_NAME DB_USER DB_PASSWORD
            export DB_HOST=${DB_HOST:-localhost}
            export DB_PORT=${DB_PORT:-3306}
            
            # 测试连接
            mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "USE $DB_NAME" 2>/dev/null
            if [ $? -eq 0 ]; then
                success "数据库连接成功 / Database connected"
            else
                error "Connection failed" "连接失败"
                return 1
            fi
            ;;
        3)
            warning "跳过数据库配置 / Skipping database"
            ;;
    esac
}

# ============================================
# 配置 OpenStack Swift
# ============================================
# ============================================
# 生成强密码
# ============================================
generate_strong_password() {
    local length=${1:-32}
    python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range($length)))"
}

# ============================================
# 自动安装 OpenStack DevStack
# ============================================
install_devstack() {
    step "安装 OpenStack DevStack / Installing DevStack..."
    
    # 检查是否已安装
    if [ -d "/opt/stack/devstack" ]; then
        warning "DevStack 已存在 / DevStack already exists"
        read -p "重新安装? / Reinstall? [y/n]: " reinstall
        if [[ ! "$reinstall" =~ ^[Yy]$ ]]; then
            return 0
        fi
    fi
    
    # 检查系统要求
    local mem_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$mem_gb" -lt 4 ]; then
        warning "内存不足 4GB，DevStack 可能运行缓慢 / Less than 4GB RAM"
        read -p "继续? / Continue? [y/n]: " cont
        [[ ! "$cont" =~ ^[Yy]$ ]] && return 1
    fi
    
    # 安装依赖
    info "安装 DevStack 依赖 / Installing DevStack dependencies..."
    sudo $PKG_UPDATE
    sudo $PKG_INSTALL git curl sudo
    
    # 创建 stack 用户
    if ! id "stack" &>/dev/null; then
        info "创建 stack 用户 / Creating stack user..."
        sudo useradd -s /bin/bash -d /opt/stack -m stack
        echo "stack ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/stack
    fi
    
    # 生成强密码
    DEVSTACK_PASSWORD=$(generate_strong_password 24)
    export DEVSTACK_PASSWORD
    
    info "生成的强密码 / Generated strong password: $DEVSTACK_PASSWORD"
    info "请保存此密码 / Please save this password!"
    echo ""
    
    # 克隆 DevStack
    info "克隆 DevStack / Cloning DevStack..."
    sudo -u stack git clone https://opendev.org/openstack/devstack /opt/stack/devstack 2>/dev/null || true
    
    # 创建 local.conf
    local HOST_IP=$(hostname -I | awk '{print $1}')
    
    sudo -u stack tee /opt/stack/devstack/local.conf > /dev/null <<EOF
[[local|localrc]]
# 密码配置 - 使用强密码
ADMIN_PASSWORD=$DEVSTACK_PASSWORD
DATABASE_PASSWORD=$DEVSTACK_PASSWORD
RABBIT_PASSWORD=$DEVSTACK_PASSWORD
SERVICE_PASSWORD=$DEVSTACK_PASSWORD

# 网络配置
HOST_IP=$HOST_IP
FLOATING_RANGE=192.168.1.0/24
FIXED_RANGE=10.11.12.0/24
FIXED_NETWORK_SIZE=256

# 启用 Swift 对象存储
ENABLE_SERVICE=s-proxy,s-object,s-container,s-account
SWIFT_HASH=$(openssl rand -hex 16)
SWIFT_REPLICAS=1

# 禁用不需要的服务 - 最小化安装
DISABLE_SERVICE=n-net,tempest,c-api,c-vol,c-sch,c-bak
disable_service horizon

# 日志配置
LOGFILE=/opt/stack/logs/stack.sh.log
VERBOSE=True
LOG_COLOR=True

# 分支配置
KEYSTONE_BRANCH=stable/2024.1
SWIFT_BRANCH=stable/2024.1
EOF
    
    # 运行 DevStack 安装
    info "开始安装 DevStack（需要 20-40 分钟）/ Starting DevStack installation (20-40 mins)..."
    
    cd /opt/stack/devstack
    sudo -u stack ./stack.sh
    
    if [ $? -eq 0 ]; then
        success "DevStack 安装成功 / DevStack installed successfully"
        
        # 保存配置信息
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}OpenStack 配置信息 / Configuration Info${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo "Auth URL: http://$HOST_IP/identity/v3"
        echo "Username: admin"
        echo "Password: $DEVSTACK_PASSWORD"
        echo "Project: admin"
        echo "Region: RegionOne"
        echo -e "${GREEN}========================================${NC}"
        
        # 自动配置环境变量
        export OS_AUTH_URL="http://$HOST_IP/identity/v3"
        export OS_USERNAME="admin"
        export OS_PASSWORD="$DEVSTACK_PASSWORD"
        export OS_PROJECT_NAME="admin"
        export OS_USER_DOMAIN_ID="default"
        export OS_PROJECT_DOMAIN_ID="default"
        export OS_REGION_NAME="RegionOne"
        export STORAGE_BACKEND="swift"
        
        return 0
    else
        error "DevStack installation failed" "DevStack 安装失败"
        error "Check logs at /opt/stack/logs/" "请检查日志 /opt/stack/logs/"
        return 1
    fi
}

# ============================================
# 检查内存是否满足 Swift 要求
# ============================================
check_memory_for_swift() {
    local mem_gb=$(free -g 2>/dev/null | awk '/^Mem:/{print $2}')
    
    if [ -z "$mem_gb" ] || [ "$mem_gb" -lt 4 ]; then
        echo ""
        echo -e "${RED}============================================${NC}"
        echo -e "${RED}  内存不足 / Insufficient Memory${NC}"
        echo -e "${RED}============================================${NC}"
        echo ""
        echo -e "${YELLOW}当前内存 / Current RAM: ${mem_gb:-<2}GB${NC}"
        echo -e "${YELLOW}Swift 最低要求 / Swift minimum: 4GB${NC}"
        echo -e "${YELLOW}DevStack 推荐 / DevStack recommended: 8GB+${NC}"
        echo ""
        echo -e "原因 / Reason:"
        echo "  - DevStack 需要运行 MySQL, RabbitMQ, Keystone, Swift 等服务"
        echo "  - 内存不足会导致安装失败或服务崩溃"
        echo ""
        echo -e "建议 / Suggestion:"
        echo "  - 升级服务器到 4GB+ 内存"
        echo "  - 或选择本地存储模式"
        echo ""
        return 1
    fi
    return 0
}

setup_swift() {
    step "配置存储后端 / Setting up storage..."
    
    while true; do
        echo ""
        echo "存储配置 / Storage Setup:"
        echo "1) 自动安装 OpenStack DevStack + Swift（需要 4GB+ 内存）"
        echo "2) 连接已有 OpenStack Swift"
        echo "3) 使用本地存储 / Local storage（推荐小内存服务器）"
        echo "4) 跳过 / Skip"
        read -p "选择 / Choose [1/2/3/4]: " swift_choice
        
        case "$swift_choice" in
            1)
                # 检查内存
                if ! check_memory_for_swift; then
                    echo ""
                    read -p "返回存储选择 / Return to storage selection [Enter]: "
                    continue
                fi
                
                install_devstack
                if [ $? -eq 0 ]; then
                    write_swift_config
                fi
                break
                ;;
            2)
                read -p "Auth URL (http://host/identity/v3): " OS_AUTH_URL
                read -p "Username: " OS_USERNAME
                OS_PASSWORD=$(get_password "Password")
                read -p "Project: " OS_PROJECT_NAME
                read -p "User Domain [default]: " OS_USER_DOMAIN_ID
                read -p "Project Domain [default]: " OS_PROJECT_DOMAIN_ID
                read -p "Region [RegionOne]: " OS_REGION_NAME
                
                export OS_AUTH_URL OS_USERNAME OS_PASSWORD OS_PROJECT_NAME
                export OS_USER_DOMAIN_ID=${OS_USER_DOMAIN_ID:-default}
                export OS_PROJECT_DOMAIN_ID=${OS_PROJECT_DOMAIN_ID:-default}
                export OS_REGION_NAME=${OS_REGION_NAME:-RegionOne}
                export STORAGE_BACKEND="swift"
                
                write_swift_config
                success "Swift 配置完成 / Swift configured"
                break
                ;;
            3)
                export STORAGE_BACKEND="local"
                success "使用本地存储 / Using local storage"
                break
                ;;
            4)
                warning "跳过存储配置 / Skipping storage"
                break
                ;;
            *)
                warning "无效选择 / Invalid choice"
                ;;
        esac
    done
}

# 写入 Swift 配置到项目
write_swift_config() {
    step "写入 Swift 配置到项目 / Writing Swift config..."
    
    # 创建 .env 文件
    cat > "$DEPLOY_DIR/.env" <<EOF
# OpenStack Swift 配置 - 自动生成
OS_AUTH_URL=$OS_AUTH_URL
OS_USERNAME=$OS_USERNAME
OS_PASSWORD=$OS_PASSWORD
OS_PROJECT_NAME=$OS_PROJECT_NAME
OS_USER_DOMAIN_ID=${OS_USER_DOMAIN_ID:-default}
OS_PROJECT_DOMAIN_ID=${OS_PROJECT_DOMAIN_ID:-default}
OS_REGION_NAME=${OS_REGION_NAME:-RegionOne}
STORAGE_BACKEND=swift

# 数据库配置
DB_NAME=${DB_NAME:-cloud_storage}
DB_USER=${DB_USER:-clouduser}
DB_PASSWORD=${DB_PASSWORD:-}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-3306}

# Django
SECRET_KEY=${SECRET_KEY:-}
EOF
    
    chmod 600 "$DEPLOY_DIR/.env"
    success "配置已写入 .env 文件 / Config written to .env"
}

# ============================================
# 部署后端
# ============================================
deploy_backend() {
    step "部署后端 / Deploying backend..."
    
    cd "$DEPLOY_DIR"
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv || virtualenv venv
    fi
    source venv/bin/activate
    
    # 安装依赖
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn mysqlclient
    
    # 生成密钥
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    
    # 迁移数据库
    python manage.py migrate
    if [ $? -ne 0 ]; then
        error "Migration failed" "数据库迁移失败"
        return 1
    fi
    
    python manage.py collectstatic --noinput
    
    success "后端部署完成 / Backend deployed"
}

# ============================================
# 配置注册与管理员
# ============================================
setup_admin() {
    step "配置用户注册 / Setting up registration..."
    
    echo ""
    read -p "允许用户注册? / Allow registration? [y/n]: " allow_reg
    
    if [[ "$allow_reg" =~ ^[Nn]$ ]]; then
        export ALLOW_REGISTRATION="false"
        warning "已禁用注册 / Registration disabled"
        
        echo ""
        info "创建管理员 / Create admin"
        read -p "用户名 / Username: " ADMIN_USER
        ADMIN_PASS=$(get_password "密码 / Password")
        read -p "邮箱 / Email: " ADMIN_EMAIL
        
        source venv/bin/activate
        python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$ADMIN_USER').exists():
    User.objects.create_superuser('$ADMIN_USER', '$ADMIN_EMAIL', '$ADMIN_PASS')
    print('Admin created')
EOF
        success "管理员创建成功 / Admin created"
    else
        export ALLOW_REGISTRATION="true"
        success "已启用注册 / Registration enabled"
        
        echo ""
        read -p "是否创建管理员? / Create admin? [y/n]: " create_admin
        if [[ "$create_admin" =~ ^[Yy]$ ]]; then
            python manage.py createsuperuser
        fi
    fi
}

# ============================================
# 部署前端
# ============================================
deploy_frontend() {
    step "部署前端 / Deploying frontend..."
    
    cd "$DEPLOY_DIR/frontend"
    
    npm install
    if [ $? -ne 0 ]; then
        error "npm install failed" "npm 安装失败"
        return 1
    fi
    
    npm run build
    if [ $? -ne 0 ]; then
        error "npm build failed" "前端构建失败"
        return 1
    fi
    
    cd "$DEPLOY_DIR"
    success "前端部署完成 / Frontend deployed"
}

# ============================================
# 配置 Nginx
# ============================================
setup_nginx() {
    step "配置 Nginx / Setting up Nginx..."
    
    read -p "域名或IP / Domain or IP: " SERVER_NAME
    SERVER_NAME=${SERVER_NAME:-localhost}
    
    local nginx_conf=""
    if [ -d "/etc/nginx/sites-available" ]; then
        nginx_conf="/etc/nginx/sites-available/cloudstorage"
    elif [ -d "/etc/nginx/conf.d" ]; then
        nginx_conf="/etc/nginx/conf.d/cloudstorage.conf"
    else
        nginx_conf="/etc/nginx/nginx.conf.d/cloudstorage.conf"
        sudo mkdir -p /etc/nginx/nginx.conf.d
    fi
    
    sudo tee $nginx_conf > /dev/null <<EOF
server {
    listen 80;
    server_name $SERVER_NAME;
    client_max_body_size 100M;

    location / {
        root $DEPLOY_DIR/frontend/build;
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
    }

    location /static/ {
        alias $DEPLOY_DIR/staticfiles/;
    }

    location /media/ {
        alias $DEPLOY_DIR/media/;
    }
}
EOF

    # 创建符号链接 (Debian系)
    if [ -d "/etc/nginx/sites-enabled" ] && [ -f "/etc/nginx/sites-available/cloudstorage" ]; then
        sudo ln -sf /etc/nginx/sites-available/cloudstorage /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
    fi
    
    sudo nginx -t
    if [ $? -eq 0 ]; then
        service_restart nginx
        success "Nginx 配置完成 / Nginx configured"
    else
        error "Nginx config error" "Nginx 配置错误"
        return 1
    fi
}

# ============================================
# 配置 Gunicorn 服务
# ============================================
setup_gunicorn() {
    step "配置 Gunicorn 服务 / Setting up Gunicorn..."
    
    if [ "$SERVICE_MANAGER" = "systemd" ]; then
        sudo tee /etc/systemd/system/cloudstorage.service > /dev/null <<EOF
[Unit]
Description=Simple Cloud Storage
After=network.target

[Service]
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$DEPLOY_DIR
Environment="PATH=$DEPLOY_DIR/venv/bin"
Environment="DB_NAME=${DB_NAME:-cloud_storage}"
Environment="DB_USER=${DB_USER:-clouduser}"
Environment="DB_PASSWORD=${DB_PASSWORD:-}"
Environment="DB_HOST=${DB_HOST:-localhost}"
Environment="DB_PORT=${DB_PORT:-3306}"
Environment="SECRET_KEY=${SECRET_KEY}"
Environment="STORAGE_BACKEND=${STORAGE_BACKEND:-local}"
ExecStart=$DEPLOY_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 cloud_storage.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF
        sudo systemctl daemon-reload
        sudo systemctl start cloudstorage
        sudo systemctl enable cloudstorage
    else
        # 非 systemd 系统使用启动脚本
        cat > "$DEPLOY_DIR/start.sh" <<EOF
#!/bin/bash
cd $DEPLOY_DIR
source venv/bin/activate
export DB_NAME=${DB_NAME:-cloud_storage}
export DB_USER=${DB_USER:-clouduser}
export DB_PASSWORD="${DB_PASSWORD:-}"
export DB_HOST=${DB_HOST:-localhost}
export DB_PORT=${DB_PORT:-3306}
export SECRET_KEY="${SECRET_KEY}"
gunicorn --workers 3 --bind 127.0.0.1:8000 --daemon cloud_storage.wsgi:application
EOF
        chmod +x "$DEPLOY_DIR/start.sh"
        "$DEPLOY_DIR/start.sh"
    fi
    
    success "Gunicorn 服务已启动 / Gunicorn started"
}

# ============================================
# 主流程
# ============================================
main() {
    print_banner
    
    # 设置部署目录
    DEPLOY_DIR=$(cd "$(dirname "$0")/.." && pwd)
    info "部署目录 / Deploy dir: $DEPLOY_DIR"
    
    # 检测系统
    detect_os
    
    # 安装依赖
    echo ""
    read -p "安装系统依赖? / Install dependencies? [y/n]: " install_deps
    [[ "$install_deps" =~ ^[Yy]$ ]] && install_packages
    
    # 配置数据库
    echo ""
    setup_database
    
    # 配置存储
    echo ""
    setup_swift
    
    # 部署后端
    echo ""
    deploy_backend || exit 1
    
    # 配置管理员
    echo ""
    setup_admin
    
    # 部署前端
    echo ""
    deploy_frontend || exit 1
    
    # 配置 Nginx
    echo ""
    read -p "配置 Nginx? [y/n]: " setup_ng
    [[ "$setup_ng" =~ ^[Yy]$ ]] && setup_nginx
    
    # 配置 Gunicorn
    echo ""
    read -p "配置后台服务? / Setup service? [y/n]: " setup_svc
    [[ "$setup_svc" =~ ^[Yy]$ ]] && setup_gunicorn
    
    # 完成
    echo ""
    print_cloud_art
    echo ""
    info "访问 / URL: http://${SERVER_NAME:-localhost}"
    info "后台 / Admin: http://${SERVER_NAME:-localhost}/admin"
    echo ""
}

main "$@"

## 导航 / Navigation

- [中文说明（Chinese Guide）](#cn-guide)
- [English Guide](#en-guide)

---

<a id="cn-guide"></a>

## 一、中文说明（Chinese Guide）

### 1. 项目简介

**简单云盘（Simple Cloud Storage）** 是一个基于 **Django + React + MySQL + OpenStack Swift** 的个人 / 团队云存储项目，支持文件管理、分享、回收站、管理员后台等功能。

### 2. 项目定位（中文）

- **目标用户**：需要自建网盘的个人开发者、小团队、实验室、校园社团等，希望掌控数据而不依赖第三方公有云。
- **使用场景**：
  - 内网文件共享与备份（公司 / 学校 / 宿舍局域网）
  - 个人多设备同步和备份（配合对象存储或本地磁盘）
  - 作为「Django + React + OpenStack Swift」技术组合的学习 / 教学示例
- **产品特点**：前后端分离、部署简单、代码结构清晰，适合二次开发和功能扩展。

### 3. 功能列表

- **文件管理**：上传、下载、重命名、移动、删除、文件夹管理
- **存储后端**：
  - OpenStack Swift 对象存储
  - 本地存储（作为备选或开发环境使用）
- **用户与权限**：注册、登录、个人资料、头像上传、角色（普通用户 / 管理员 / VIP）
- **分享功能**：生成分享链接、设置密码和有效期、外链访问
- **回收站**：软删除、恢复、彻底删除
- **统计与管理**：存储空间统计、VIP 申请与审核、登录记录、在线用户
- **前端体验**：React + Ant Design，支持基础响应式布局

### 4. 界面预览

<div align="center">

![系统预览](./assets/preview.png "简单云盘界面预览")

</div>

### 5. 技术栈

- **后端**
  - Django 4.2.7
  - Django REST Framework
  - MySQL
  - OpenStack Swift（对象存储）
  - Celery + Redis（异步任务 & 消息队列）

- **前端**
  - React 18
  - Ant Design
  - React Router v6
  - React Query

---

### 5. 本地部署步骤（仅代码，不包含演示数据）

#### 5.1 克隆代码

```bash
git clone https://github.com/songdiyang/simple-cloud-storage.git
cd cloud-storage-system
```

#### 5.2 后端环境（Django + MySQL）

1）创建虚拟环境并安装依赖：

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

2）配置数据库（MySQL）：  
- 默认在 `cloud_storage/settings.py` 中读取环境变量：
  - `DB_NAME`（默认：`cloud_storage`）
  - `DB_USER`（默认：`root`）
  - `DB_PASSWORD`（默认：`3306`）
  - `DB_HOST`（默认：`localhost`）
  - `DB_PORT`（默认：`3306`）

请在 MySQL 中创建对应数据库，并按需修改环境变量或直接修改 `settings.py`。

3）迁移数据库并创建超级用户：

```bash
python manage.py migrate
python manage.py createsuperuser
```

4）启动后端服务：

```bash
python manage.py runserver 0.0.0.0:8000
```

#### 5.3 前端环境（React）

```bash
cd frontend
npm install
npm start
```

前端默认运行在 `http://localhost:3000`，`package.json` 中配置了：

```json
"proxy": "http://localhost:8000"
```

因此前端会自动把 `/api/...` 请求转发到后端。

#### 5.4 访问入口

- 登录页：`http://localhost:3000/login`
- 用户首页 / 文件页：`http://localhost:3000/dashboard`
- 分享访问：`http://localhost:3000/share/:shareCode`
- Django 管理后台：`http://localhost:8000/admin`

---

### 6. OpenStack Swift 部署与连接（详细）

后端通过 `cloud_storage/settings.py` 中的 `SWIFT_CONFIG` 使用 OpenStack Swift。你需要准备好一个可用的 OpenStack 环境，并配置好认证信息。

#### 6.1 前置条件

- 已部署好的 OpenStack（DevStack 或 生产环境）
- 已安装并运行 Swift（Object Storage）服务
- 拥有一个项目（Project / Project）和具备访问 Swift 权限的用户

#### 6.2 在服务器上配置环境变量

在运行 Django 后端的服务器 / 容器中，设置以下环境变量（示例）：

```bash
# Keystone 认证地址（注意 /v3）
export OS_AUTH_URL=http://<YOUR_OPENSTACK_HOST>/identity/v3

# 域配置（默认即可，不清楚就用 default）
export OS_USER_DOMAIN_ID=default
export OS_PROJECT_DOMAIN_ID=default

# 认证用户信息
export OS_USERNAME=admin
export OS_PASSWORD=your_password
export OS_PROJECT_NAME=admin

# 区域（和你 OpenStack 配置一致）
export OS_REGION_NAME=RegionOne

# 可选：自签名证书的 CA 文件路径
export OS_CACERT=
```

`settings.py` 中的 `SWIFT_CONFIG` 会读取这些环境变量，无需修改代码：

```python
SWIFT_CONFIG = {
    'auth_version': '3',
    'auth_url': os.getenv('OS_AUTH_URL', 'http://.../identity/v3'),
    'username': os.getenv('OS_USERNAME', 'admin'),
    'password': os.getenv('OS_PASSWORD', 'devstack123'),
    'project_name': os.getenv('OS_PROJECT_NAME', 'admin'),
    'project_domain_id': os.getenv('OS_PROJECT_DOMAIN_ID', 'default'),
    'user_domain_id': os.getenv('OS_USER_DOMAIN_ID', 'default'),
    'region_name': os.getenv('OS_REGION_NAME', 'RegionOne'),
    'cacert': os.getenv('OS_CACERT', None),
}
```

#### 6.3 使用 python-swiftclient 测试连接（可选）

在激活虚拟环境后执行：

```bash
swift stat
swift list
```

- `swift stat`：查看当前账号信息
- `swift list`：列出所有容器

如果命令返回正常数据，说明 Swift 认证配置正确。

#### 6.4 容器与存储策略

- 项目会为用户上传的文件创建对象，容器命名可以在代码中统一配置（例如：按用户分容器或统一容器 + 目录）。
- 建议在 OpenStack 端开启：版本控制、生命周期（自动过期）、配额限制等策略，以便更好地控制成本和安全。

#### 6.5 生产环境建议

- 使用内网 / 专用子网访问 Swift，避免直接暴露存储节点到公网。
- 对外下载链接建议走 Django + Nginx 反向代理，并做限速、鉴权、日志记录。
- 对 Swift 操作添加监控（请求失败率、响应时间、存储容量告警等）。

---

### 7. 云端部署教程

本节介绍如何将简单云盘部署到云服务器（如阿里云、腾讯云、AWS等）。

#### 7.0 一键部署脚本（推荐）

项目提供自动部署脚本，支持多种 Linux 发行版：

**支持系统**：Ubuntu / Debian / CentOS / RHEL / Fedora / Arch / openSUSE / Alpine

```bash
# 克隆项目
git clone https://github.com/songdiyang/simple-cloud-storage.git
cd simple-cloud-storage

# 运行一键部署
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

**脚本功能**：
- 自动识别 Linux 发行版和包管理器
- 交互式配置 MySQL 数据库
- 交互式配置 OpenStack Swift（可选）
- 自动部署前后端
- 配置 Nginx 和 Gunicorn 服务
- 支持禁用注册并手动创建管理员
- 中英文错误提示

如需手动部署，请参考以下步骤：

#### 7.1 服务器要求

- **操作系统**：Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **配置要求**：
  - CPU：2核+
  - 内存：4GB+
  - 硬盘：20GB+
- **开放端口**：80、443、8000、3306

#### 7.2 安装基础环境

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx mysql-server nodejs npm git

# CentOS
sudo yum install -y python3 python3-pip nginx mysql-server nodejs npm git
```

#### 7.3 配置 MySQL

```bash
# 启动 MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全配置
sudo mysql_secure_installation

# 创建数据库和用户
sudo mysql -u root -p
```

```sql
CREATE DATABASE cloud_storage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'clouduser'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON cloud_storage.* TO 'clouduser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 7.4 部署后端

```bash
# 克隆项目
cd /var/www
sudo git clone https://github.com/songdiyang/simple-cloud-storage.git
cd simple-cloud-storage

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn

# 配置环境变量
export DB_NAME=cloud_storage
export DB_USER=clouduser
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=3306
export SECRET_KEY=your_django_secret_key

# 迁移数据库
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 7.5 配置 Gunicorn

创建 systemd 服务文件：

```bash
sudo nano /etc/systemd/system/cloudstorage.service
```

内容如下：

```ini
[Unit]
Description=Simple Cloud Storage Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/simple-cloud-storage
Environment="PATH=/var/www/simple-cloud-storage/venv/bin"
Environment="DB_NAME=cloud_storage"
Environment="DB_USER=clouduser"
Environment="DB_PASSWORD=your_password"
ExecStart=/var/www/simple-cloud-storage/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 cloud_storage.wsgi:application

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start cloudstorage
sudo systemctl enable cloudstorage
```

#### 7.6 部署前端

```bash
cd /var/www/simple-cloud-storage/frontend

# 安装依赖并构建
npm install
npm run build
```

#### 7.7 配置 Nginx

```bash
sudo nano /etc/nginx/sites-available/cloudstorage
```

配置内容：

```nginx
server {
    listen 80;
    server_name your_domain.com;

    # 前端静态文件
    location / {
        root /var/www/simple-cloud-storage/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # 静态文件
    location /static/ {
        alias /var/www/simple-cloud-storage/staticfiles/;
    }

    # 媒体文件
    location /media/ {
        alias /var/www/simple-cloud-storage/media/;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/cloudstorage /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7.8 配置 HTTPS（推荐）

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your_domain.com

# 自动续期
sudo systemctl enable certbot.timer
```

#### 7.9 常见问题

**Q: 端口被占用？**
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

**Q: 静态文件无法访问？**
```bash
python manage.py collectstatic --noinput
sudo chown -R www-data:www-data /var/www/simple-cloud-storage
```

**Q: 服务无法启动？**
```bash
sudo systemctl status cloudstorage
sudo journalctl -u cloudstorage -f
```

---

### 8. 目录结构（简要概览）

```
cloud-storage-system/
├─ cloud_storage/        # Django 项目配置
├─ accounts/             # 用户 / 角色 / VIP / 登录记录等
├─ files/                # 文件 / 文件夹 / 分享 / 回收站等
├─ frontend/             # React 前端源码
├─ requirements.txt      # 后端依赖
└─ manage.py             # Django 管理脚本
```

---

### 9. 许可证

本项目采用 **MIT License**，可用于学习、实验和二次开发。

---

## 赞助 / Sponsor

如果您觉得这个项目对您有帮助，欢迎赞助支持！

<div align="center">

### WeChat Pay / 微信支付

<img src="./assets/wechat-pay-qrcode.png" alt="WeChat Pay QR Code" width="200" />

### Alipay / 支付宝

<img src="./assets/alipay-qrcode.png" alt="Alipay QR Code" width="200" />

</div>

---

<a id="en-guide"></a>

## II. English Guide

### 1. Overview

**Simple Cloud Storage** is a personal / team cloud drive project built with **Django + React + MySQL + OpenStack Swift**.  
It supports file management, sharing, recycle bin, and an admin dashboard.

### 2. Positioning & Use Cases

- **Target users**: individual developers, small teams, labs, and student groups who want a self-hosted cloud drive and full control over their data.
- **Typical scenarios**:
  - Intranet file sharing and backup (office / school / dorm LAN)
  - Personal multi-device backup with object storage or local disks
  - A reference implementation for learning / teaching the stack “Django + React + OpenStack Swift”
- **Key traits**: clean architecture, simple deployment, and easy to extend for your own business needs.

### 3. Features

- **File Management**: upload, download, rename, move, delete, folder management
- **Storage Backends**:
  - OpenStack Swift object storage
  - Local storage (as backup or for development)
- **Users & Roles**: registration, login, profile, avatar upload, roles (user / admin / VIP)
- **Sharing**: share links, password protection, expiration, public access
- **Recycle Bin**: soft delete, restore, permanent delete
- **Statistics & Admin**: storage usage, VIP applications, login records, online users
- **Frontend**: React + Ant Design, basic responsive layout

### 4. Interface Preview

<div align="center">

![System Preview](./assets/preview.png "Cloud Storage System Interface Preview")

</div>

### 5. Tech Stack

- **Backend**
  - Django 4.2.7, Django REST Framework
  - MySQL
  - OpenStack Swift
  - Celery + Redis

- **Frontend**
  - React 18
  - Ant Design
  - React Router v6
  - React Query

---

### 5. Local Setup

#### 5.1 Clone the project

```bash
git clone https://github.com/songdiyang/simple-cloud-storage.git
cd cloud-storage-system
```

#### 5.2 Backend (Django + MySQL)

1) Create virtual env and install dependencies:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

2) Configure MySQL:  
Database settings are read from environment variables in `cloud_storage/settings.py`:

- `DB_NAME` (default: `cloud_storage`)
- `DB_USER` (default: `root`)
- `DB_PASSWORD` (default: `3306`)
- `DB_HOST` (default: `localhost`)
- `DB_PORT` (default: `3306`)

Create the database in MySQL and adjust env vars or `settings.py` if needed.

3) Migrate and create superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

4) Run backend:

```bash
python manage.py runserver 0.0.0.0:8000
```

#### 5.3 Frontend (React)

```bash
cd frontend
npm install
npm start
```

The frontend runs at `http://localhost:3000` and proxies API requests to `http://localhost:8000` via `package.json`:

```json
"proxy": "http://localhost:8000"
```

#### 5.4 Entry Points

- Login: `http://localhost:3000/login`
- User dashboard: `http://localhost:3000/dashboard`
- Share view: `http://localhost:3000/share/:shareCode`
- Django admin: `http://localhost:8000/admin`

---

### 6. OpenStack Swift Setup & Integration

The backend uses the `SWIFT_CONFIG` section in `cloud_storage/settings.py` and environment variables to connect to Swift.

#### 6.1 Prerequisites

- A running OpenStack environment (DevStack or production)
- Swift (Object Storage) service installed and running
- A project and a user with permission to access Swift

#### 6.2 Environment Variables

Set the following env vars on the server where Django runs:

```bash
# Keystone endpoint (make sure /v3 is used)
export OS_AUTH_URL=http://<YOUR_OPENSTACK_HOST>/identity/v3

# Domains
export OS_USER_DOMAIN_ID=default
export OS_PROJECT_DOMAIN_ID=default

# Credentials
export OS_USERNAME=admin
export OS_PASSWORD=your_password
export OS_PROJECT_NAME=admin

# Region
export OS_REGION_NAME=RegionOne

# Optional CA cert
export OS_CACERT=
```

These will be read by:

```python
SWIFT_CONFIG = {
    'auth_version': '3',
    'auth_url': os.getenv('OS_AUTH_URL', 'http://.../identity/v3'),
    'username': os.getenv('OS_USERNAME', 'admin'),
    'password': os.getenv('OS_PASSWORD', 'devstack123'),
    'project_name': os.getenv('OS_PROJECT_NAME', 'admin'),
    'project_domain_id': os.getenv('OS_PROJECT_DOMAIN_ID', 'default'),
    'user_domain_id': os.getenv('OS_USER_DOMAIN_ID', 'default'),
    'region_name': os.getenv('OS_REGION_NAME', 'RegionOne'),
    'cacert': os.getenv('OS_CACERT', None),
}
```

#### 6.3 Test Swift Connection (optional)

With `python-swiftclient` installed, run:

```bash
swift stat
swift list
```

If both commands succeed, your Swift authentication is correctly configured.

#### 6.4 Containers & Strategy

- The project creates objects for uploaded files; you can use per-user containers or a shared container with folder prefixes.
- On the OpenStack side, consider enabling lifecycle policies, versioning, and quotas.

#### 6.5 Production Recommendations

- Access Swift via internal networks or dedicated subnets.
- Serve downloads through Django + Nginx (reverse proxy), with throttling, auth, and logging.
- Add monitoring and alerts for Swift operations and capacity.

---

### 7. Cloud Deployment Guide

This section describes how to deploy Simple Cloud Storage to cloud servers (such as Aliyun, Tencent Cloud, AWS, etc.).

#### 7.0 One-Click Deploy Script (Recommended)

The project provides an automatic deployment script that supports multiple Linux distributions:

**Supported OS**: Ubuntu / Debian / CentOS / RHEL / Fedora / Arch / openSUSE / Alpine

```bash
# Clone project
git clone https://github.com/songdiyang/simple-cloud-storage.git
cd simple-cloud-storage

# Run one-click deploy
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

**Features**:
- Auto-detect Linux distribution and package manager
- Interactive MySQL database configuration
- Interactive OpenStack Swift configuration (optional)
- Auto deploy frontend and backend
- Configure Nginx and Gunicorn services
- Support disabling registration and manual admin creation
- Bilingual error messages (English/Chinese)

For manual deployment, please refer to the following steps:

#### 7.1 Server Requirements

- **OS**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **Resources**:
  - CPU: 2 cores+
  - RAM: 4GB+
  - Disk: 20GB+
- **Open Ports**: 80, 443, 8000, 3306

#### 7.2 Install Base Environment

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx mysql-server nodejs npm git

# CentOS
sudo yum install -y python3 python3-pip nginx mysql-server nodejs npm git
```

#### 7.3 Configure MySQL

```bash
# Start MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Security setup
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

```sql
CREATE DATABASE cloud_storage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'clouduser'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON cloud_storage.* TO 'clouduser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 7.4 Deploy Backend

```bash
# Clone project
cd /var/www
sudo git clone https://github.com/songdiyang/simple-cloud-storage.git
cd simple-cloud-storage

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Configure environment variables
export DB_NAME=cloud_storage
export DB_USER=clouduser
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=3306
export SECRET_KEY=your_django_secret_key

# Migrate database
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 7.5 Configure Gunicorn

Create systemd service file:

```bash
sudo nano /etc/systemd/system/cloudstorage.service
```

Content:

```ini
[Unit]
Description=Simple Cloud Storage Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/simple-cloud-storage
Environment="PATH=/var/www/simple-cloud-storage/venv/bin"
Environment="DB_NAME=cloud_storage"
Environment="DB_USER=clouduser"
Environment="DB_PASSWORD=your_password"
ExecStart=/var/www/simple-cloud-storage/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 cloud_storage.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl start cloudstorage
sudo systemctl enable cloudstorage
```

#### 7.6 Deploy Frontend

```bash
cd /var/www/simple-cloud-storage/frontend

# Install and build
npm install
npm run build
```

#### 7.7 Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/cloudstorage
```

Configuration:

```nginx
server {
    listen 80;
    server_name your_domain.com;

    # Frontend static files
    location / {
        root /var/www/simple-cloud-storage/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # API reverse proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # Static files
    location /static/ {
        alias /var/www/simple-cloud-storage/staticfiles/;
    }

    # Media files
    location /media/ {
        alias /var/www/simple-cloud-storage/media/;
    }
}
```

Enable configuration:

```bash
sudo ln -s /etc/nginx/sites-available/cloudstorage /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7.8 Configure HTTPS (Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your_domain.com

# Auto renewal
sudo systemctl enable certbot.timer
```

#### 7.9 Troubleshooting

**Q: Port already in use?**
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

**Q: Cannot access static files?**
```bash
python manage.py collectstatic --noinput
sudo chown -R www-data:www-data /var/www/simple-cloud-storage
```

**Q: Service fails to start?**
```bash
sudo systemctl status cloudstorage
sudo journalctl -u cloudstorage -f
```

---

### 8. License

This project is released under the **MIT License**.

---

## Sponsor / 赞助

If you find this project helpful, you're welcome to support us!

<div align="center">

### WeChat Pay / 微信支付

<img src="./assets/wechat-pay-qrcode.png" alt="WeChat Pay QR Code" width="200" />

### Alipay / 支付宝

<img src="./assets/alipay-qrcode.png" alt="Alipay QR Code" width="200" />

</div>

---

## Contributors / 贡献者

感谢以下贡献者为项目做出的努力：

<div align="center">

<!-- 用法: ![贡献者头像](头像URL "贡献者姓名") -->

[<img src="https://foruda.gitee.com/avatar/1765030028102188735/15302629_song-diyang_1765030028.png!avatar200" width="100" style="border-radius: 50%; margin: 10px;" title="songdiyang">](https://gitee.com/song-diyang)

</div>

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

### 5. 本地部署

#### 5.1 一键部署（推荐）

```bash
# 克隆项目
git clone https://github.com/songdiyang/simple-cloud-storage.git
cd simple-cloud-storage

# 运行部署脚本
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh
```

脚本自动完成：Python环境、数据库配置、依赖安装、管理员创建。

#### 5.2 启动服务

```bash
# 启动后端
python manage.py runserver

# 启动前端（新终端）
cd frontend && npm start
```

#### 5.3 访问入口

- 前端：`http://localhost:3000`
- 后台：`http://localhost:8000/admin`

---

### 6. OpenStack Swift 存储（可选）

项目支持 OpenStack Swift 对象存储，也可使用本地存储。

#### 6.1 自动配置

部署脚本已集成 Swift 配置，运行 `./scripts/deploy.sh` 时选择配置 Swift 即可。

#### 6.2 环境变量

如需手动配置，设置以下环境变量：

```bash
export OS_AUTH_URL=http://<HOST>/identity/v3
export OS_USERNAME=admin
export OS_PASSWORD=your_password
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_ID=default
export OS_PROJECT_DOMAIN_ID=default
export OS_REGION_NAME=RegionOne
```

#### 6.3 验证连接

```bash
swift stat
swift list
```

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
- 自动安装 OpenStack DevStack + Swift（需 4GB+ 内存）
- 自动部署前后端
- 配置 Gunicorn 后台服务
- 部署完成显示服务端口和访问地址
- 中英文错误提示

**部署成功示例**：

```
    ██████╗██╗      ██████╗ ██╗   ██╗██████╗ 
   ██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗
   ██║     ██║     ██║   ██║██║   ██║██║  ██║
   ██║     ██║     ██║   ██║██║   ██║██║  ██║
   ╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝
    ╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ 

   ☁️  简单云盘部署成功 / Deploy Success  ☁️

============================================
  访问地址 / Access URL
============================================

  云存储服务 / Cloud Storage:
    http://<服务器IP>:8000/

  管理后台 / Admin:
    http://<服务器IP>:8000/admin/
```

#### 7.1 服务器要求

- **操作系统**：Linux（不支持 Windows/macOS）
- **最低配置**：2核 CPU、2GB 内存、20GB 硬盘
- **Swift 配置**：需 4GB+ 内存
- **开放端口**：8000、3306

#### 7.2 部署后更新

```bash
cd /var/www/simple-cloud-storage
git pull origin main
./scripts/deploy.sh
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

#### 5.1 One-Click Setup (Recommended)

```bash
# Clone project
git clone https://github.com/songdiyang/simple-cloud-storage.git
cd simple-cloud-storage

# Run setup script
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh
```

The script automatically handles: Python environment, database configuration, dependency installation, admin creation.

#### 5.2 Start Services

```bash
# Start backend
python manage.py runserver

# Start frontend (new terminal)
cd frontend && npm start
```

#### 5.3 Entry Points

- Frontend: `http://localhost:3000`
- Admin: `http://localhost:8000/admin`

---

### 6. OpenStack Swift Storage (Optional)

The project supports OpenStack Swift object storage, or local storage.

#### 6.1 Auto Configuration

Swift configuration is integrated in the deploy script. Run `./scripts/deploy.sh` and select Swift configuration.

#### 6.2 Environment Variables

For manual configuration, set the following:

```bash
export OS_AUTH_URL=http://<HOST>/identity/v3
export OS_USERNAME=admin
export OS_PASSWORD=your_password
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_ID=default
export OS_PROJECT_DOMAIN_ID=default
export OS_REGION_NAME=RegionOne
```

#### 6.3 Verify Connection

```bash
swift stat
swift list
```

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
- Auto install OpenStack DevStack + Swift (requires 4GB+ RAM)
- Auto deploy frontend and backend
- Configure Gunicorn backend service
- Display service ports and access URLs after deployment
- Bilingual error messages (English/Chinese)

**Deployment Success Example**:

```
    ██████╗██╗      ██████╗ ██╗   ██╗██████╗ 
   ██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗
   ██║     ██║     ██║   ██║██║   ██║██║  ██║
   ██║     ██║     ██║   ██║██║   ██║██║  ██║
   ╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝
    ╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ 

   ☁️  Deploy Success  ☁️

============================================
  Access URL
============================================

  Cloud Storage:
    http://<your_server_ip>:8000/

  Admin:
    http://<your_server_ip>:8000/admin/
```

#### 7.1 Server Requirements

- **OS**: Linux only (Windows/macOS not supported)
- **Minimum**: 2 CPU cores, 2GB RAM, 20GB disk
- **Swift**: Requires 4GB+ RAM
- **Open Ports**: 8000, 3306

#### 7.2 Update After Deployment

```bash
cd /var/www/simple-cloud-storage
git pull origin main
./scripts/deploy.sh
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

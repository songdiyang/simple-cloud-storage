## 云盘系统

基于 **Django + React + MySQL + OpenStack Swift** 的个人/团队云存储系统，前后端分离，UI 采用明快的赛璐璐风格。

### 功能特性

- **文件管理**：文件/文件夹的创建、重命名、删除、移动
- **多存储支持**：OpenStack Swift 对象存储 + 本地存储备份
- **用户体系**：注册 / 登录 / 资料修改 / 头像上传
- **权限与角色**：普通用户 / 管理员，支持 VIP 申请与审核
- **分享功能**：生成分享链接、设置密码与有效期、外链访问
- **回收站**：删除文件进入回收站，可恢复或彻底删除
- **存储统计**：已用空间、配额、全局统计（管理后台）
- **管理后台**：用户管理、VIP 审核、登录记录、在线用户等

### 技术栈

- **后端**
  - Django 4.2.7, Django REST Framework
  - MySQL
  - OpenStack Swift
  - Celery + Redis（异步任务与消息队列）

- **前端**
  - React 18
  - Ant Design
  - React Router v6
  - React Query

---

### 快速开始

#### 1. 克隆项目

```bash
git clone https://gitee.com/song-diyang/cloud-storage-system.git
cd cloud-storage-system
```

#### 2. 后端环境

```bash
# 创建并激活虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# 或
source venv/bin/activate  # Linux / Mac

# 安装依赖
pip install -r requirements.txt

# 迁移数据库
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动后端
python manage.py runserver 0.0.0.0:8000
```

> 数据库默认使用 MySQL，连接信息在 `cloud_storage/settings.py` 中通过环境变量配置。

#### 3. 前端环境

```bash
cd frontend
npm install
npm start
```

前端默认运行在 `http://localhost:3000`，通过 `package.json` 中的 `proxy` 代理到后端 `http://localhost:8000`。

#### 4. 访问入口

- 用户登录页：`http://localhost:3000/login`
- 用户文件管理页：`http://localhost:3000/dashboard`
- 分享访问页：`http://localhost:3000/share/:shareCode`
- Django 管理后台：`http://localhost:8000/admin`

---

### 项目结构（精简版）

```text
cloud-storage-system/
├─ cloud_storage/        # Django 项目配置
│  ├─ settings.py        # 配置（数据库、Swift、Redis 等）
│  ├─ urls.py            # 主路由
│  └─ wsgi.py / asgi.py
├─ accounts/             # 用户与权限
│  ├─ models.py          # 用户、VIP 申请、登录记录、在线用户
│  ├─ views.py           # 注册、登录、资料、VIP 接口等
│  ├─ serializers.py
│  └─ authentication.py  # 自定义 Token 过期逻辑
├─ files/                # 文件与存储
│  ├─ models.py          # 文件、文件夹等模型
│  ├─ views/             # 文件、分享、回收站、下载等接口
│  ├─ services/          # Swift 与本地存储服务
│  └─ utils.py           # Swift 相关工具函数
├─ frontend/             # React 前端源码
│  ├─ src/
│  │  ├─ pages/          # 登录、文件、分享、回收站、管理后台等页面
│  │  ├─ components/     # Header / Sidebar / 弹窗等组件
│  │  ├─ contexts/       # AuthContext 等
│  │  └─ services/       # API 封装
│  └─ package.json
├─ requirements.txt      # 后端依赖
└─ manage.py             # Django 管理脚本
```

---

### 核心 API（部分）

- **认证**
  - `POST /api/auth/register/`：用户注册
  - `POST /api/auth/login/`：登录并获取 Token
  - `POST /api/auth/logout/`：登出
  - `GET/PUT /api/auth/profile/`：获取 / 修改用户资料

- **文件**
  - `GET /api/files/`：文件列表
  - `POST /api/files/upload/`：上传文件
  - `DELETE /api/files/{id}/`：删除文件（进入回收站）

- **文件夹**
  - `GET /api/folders/`：文件夹列表
  - `POST /api/folders/`：创建文件夹
  - `DELETE /api/folders/{id}/`：删除文件夹

- **分享**
  - `POST /api/shares/`：创建分享
  - `GET /api/shares/`：我的分享
  - `DELETE /api/shares/{id}/`：删除分享

- **回收站 & 统计**
  - `GET /api/trash/`：回收站列表
  - `POST /api/trash/{id}/restore/`：恢复文件
  - `DELETE /api/trash/{id}/`：彻底删除
  - `GET /api/storage/stats/`：存储统计

---

### 部署建议（简要）

- 数据库：准备好 MySQL 实例，并配置好账号与库名
- 对象存储：确保 OpenStack Swift 可用，并按实际环境设置相关环境变量
- 消息队列：启动 Redis，供 Celery 使用
- 生产环境：建议使用 Nginx + Gunicorn / uWSGI 部署 Django，并将前端打包后由 Nginx 提供静态资源

---

### 许可证

本项目采用 **MIT License**。
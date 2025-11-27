# 云盘系统

基于 Django + React + MySQL + OpenStack Swift 的现代化云存储系统，采用赛璐璐风格设计。

## 功能特性

- 📁 文件和文件夹管理
- ☁️ OpenStack Swift 对象存储
- 🔐 用户认证和授权
- 📤 文件上传和下载
- 🔗 文件分享功能
- 📊 存储空间管理
- 🎨 赛璐璐风格UI设计
- 📱 响应式设计

## 技术栈

### 后端
- Django 4.2.7
- Django REST Framework
- MySQL
- OpenStack Swift
- Celery (异步任务)
- Redis (消息队列)

### 前端
- React 18
- Ant Design
- React Router
- React Query
- Styled Components

## 环境配置

### OpenStack Swift 配置

```bash
export OS_REGION_NAME=RegionOne
export OS_PROJECT_DOMAIN_ID=default
export OS_CACERT=
export OS_AUTH_URL=http://192.168.219.143/identity
export OS_USER_DOMAIN_ID=default
export OS_USERNAME=admin
export OS_AUTH_TYPE=password
export OS_PROJECT_NAME=admin
export OS_PASSWORD=devstack123
```

### 数据库配置

- 数据库类型: MySQL
- 端口: 3306
- 密码: 3306

## 安装和运行

### 1. 克隆项目

```bash
git clone <repository-url>
cd cloud-storage-system
```

### 2. 后端设置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入正确的配置

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动后端服务
python manage.py runserver
```

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动前端服务
npm start
```

### 4. 访问应用

- 前端地址: http://localhost:3000
- 后端API: http://localhost:8000
- 管理后台: http://localhost:8000/admin

## 项目结构

```
cloud-storage-system/
├── cloud_storage/          # Django项目配置
│   ├── settings.py        # 项目设置
│   ├── urls.py           # 主URL配置
│   └── wsgi.py           # WSGI配置
├── accounts/              # 用户认证应用
│   ├── models.py         # 用户模型
│   ├── views.py          # 认证视图
│   └── serializers.py    # 序列化器
├── files/                 # 文件管理应用
│   ├── models.py         # 文件和文件夹模型
│   ├── views.py          # 文件操作视图
│   ├── utils.py          # Swift工具函数
│   └── serializers.py    # 序列化器
├── frontend/              # React前端
│   ├── src/
│   │   ├── components/   # 通用组件
│   │   ├── pages/        # 页面组件
│   │   ├── contexts/     # React Context
│   │   └── services/     # API服务
│   └── package.json
├── requirements.txt       # Python依赖
├── .env                  # 环境变量
└── manage.py             # Django管理脚本
```

## API接口

### 认证相关
- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/logout/` - 用户登出
- `GET/PUT /api/auth/profile/` - 用户资料

### 文件管理
- `GET /api/files/` - 文件列表
- `POST /api/files/upload/` - 文件上传
- `DELETE /api/files/{id}/delete/` - 删除文件
- `GET /api/files/folders/` - 文件夹列表
- `POST /api/files/folders/create/` - 创建文件夹

### 分享功能
- `POST /api/files/{id}/share/` - 创建分享
- `GET /api/files/shares/` - 我的分享
- `DELETE /api/files/shares/{id}/delete/` - 删除分享

## 部署说明

1. 确保OpenStack Swift服务正常运行
2. 配置正确的数据库连接
3. 设置Redis服务用于Celery
4. 配置Nginx反向代理（生产环境）
5. 使用Gunicorn或uWSGI部署Django应用

## 开发说明

- 后端使用Django REST Framework提供API
- 前端使用React和Ant Design构建用户界面
- 采用赛璐璐风格设计，色彩鲜艳、圆润可爱
- 支持响应式设计，适配移动端

## 许可证

MIT License
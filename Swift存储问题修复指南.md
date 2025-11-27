# Swift存储问题修复指南

## 问题描述

当前云存储系统遇到Swift存储服务访问问题：
- 文件上传显示成功但实际未存储到Swift
- 下载时返回404错误：`Not Found The requested URL was not found on this server`

## 问题分析

### 1. Swift服务状态
- ✅ Swift认证服务正常（可连接到identity服务）
- ✅ Swift API连接成功
- ❌ Swift对象存储服务不可访问（8080端口返回404）
- ❌ 文件上传后实际未存储到Swift容器

### 2. 可能原因
1. **Swift服务未正确启动**：对象存储服务可能未运行
2. **端口配置错误**：Swift对象存储端口可能不是8080
3. **权限问题**：容器权限或用户权限配置不正确
4. **服务配置问题**：Swift代理服务配置有误

## 解决方案

### 方案1：检查并修复Swift服务

#### 1.1 检查Swift服务状态
```bash
# 检查Swift相关服务
ps aux | grep swift

# 检查端口占用
netstat -tulpn | grep 8080
netstat -tulpn | grep 80

# 检查Swift配置
cat /etc/swift/proxy-server.conf
```

#### 1.2 重启Swift服务
```bash
# 重启Swift服务
sudo systemctl restart swift-proxy
sudo systemctl restart swift-account
sudo systemctl restart swift-container
sudo systemctl restart swift-object

# 或使用service命令
sudo service swift-proxy restart
sudo service swift-account restart
sudo service swift-container restart
sudo service swift-object restart
```

#### 1.3 检查Swift配置文件
```bash
# 检查代理服务器配置
cat /etc/swift/proxy-server.conf

# 确认bind_port和bind_ip设置
[DEFAULT]
bind_port = 8080
bind_ip = 0.0.0.0

# 检查认证配置
[filter:authtoken]
auth_uri = http://192.168.219.143:5000
auth_url = http://192.168.219.143:35357
auth_plugin = password
project_name = admin
username = admin
password = devstack123
```

### 方案2：使用本地文件存储（临时解决方案）

如果Swift服务暂时无法修复，可以切换到本地文件存储：

#### 2.1 修改settings.py
```python
# 添加本地文件存储配置
LOCAL_STORAGE_ENABLED = True
LOCAL_STORAGE_PATH = os.path.join(BASE_DIR, 'local_storage')
```

#### 2.2 修改文件上传视图
```python
# 在files/views.py中添加本地存储支持
def upload_file_to_local(file_obj, user_id, filename):
    """上传文件到本地存储"""
    try:
        # 创建用户目录
        user_dir = Path(settings.LOCAL_STORAGE_PATH) / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        file_path = user_dir / filename
        with open(file_path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        
        return True, str(file_path)
    except Exception as e:
        return False, str(e)
```

### 方案3：修复Swift端口配置

#### 3.1 查找正确的Swift端口
```bash
# 查找Swift服务使用的端口
sudo netstat -tulpn | grep python
sudo lsof -i -P -n | grep LISTEN

# 检查常见的Swift端口
curl -I http://192.168.219.143:8080/
curl -I http://192.168.219.143:8888/
curl -I http://192.168.219.143:7480/
```

#### 3.2 更新Django配置
如果Swift使用其他端口，更新settings.py：
```python
SWIFT_CONFIG = {
    'auth_version': '3',
    'auth_url': 'http://192.168.219.143/identity',
    'username': 'admin',
    'password': 'devstack123',
    'project_name': 'admin',
    'project_domain_id': 'default',
    'user_domain_id': 'default',
    'region_name': 'RegionOne',
    'object_storage_url': 'http://192.168.219.143:8888/v1',  # 更新为正确端口
}
```

## 当前系统状态

### ✅ 正常功能
- 用户认证
- 文件信息管理（数据库）
- 下载功能（提供说明文件）
- 前端界面

### ❌ 受影响功能
- 实际文件存储到Swift
- 原始文件下载
- 文件预览

### 🔄 临时解决方案
- 下载时提供详细说明文件
- 错误信息友好显示
- 支持重试机制

## 推荐操作步骤

1. **立即检查**Swift服务状态和端口配置
2. **重启Swift服务**如果需要
3. **测试上传下载**功能
4. **如果Swift无法修复**，考虑启用本地文件存储
5. **更新系统配置**确保生产环境可用

## 测试命令

```bash
# 测试Swift连接
python scripts/check_swift.py

# 测试文件上传
python scripts/test_upload.py

# 测试文件下载
python scripts/test_download.py

# 测试前端功能
# 访问 http://localhost:3000 并登录测试
```

## 联系信息

如果问题持续存在，建议：
1. 检查系统日志：`/var/log/swift/`
2. 联系系统管理员检查Swift集群状态
3. 考虑使用其他对象存储方案（如MinIO）
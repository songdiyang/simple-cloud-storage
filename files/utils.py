import os
import hashlib
try:
    import magic
except ImportError:
    magic = None
from swiftclient.service import SwiftService, SwiftUploadObject
from swiftclient.exceptions import ClientException
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile


def get_swift_connection():
    """获取Swift连接"""
    swift_config = settings.SWIFT_CONFIG
    
    # 使用基础Connection而不是SwiftService
    from swiftclient import Connection
    return Connection(
        authurl=swift_config['auth_url'],
        user=swift_config['username'],
        key=swift_config['password'],
        tenant_name=swift_config['project_name'],
        auth_version=swift_config['auth_version'],
        os_options={
            'project_domain_id': swift_config['project_domain_id'],
            'user_domain_id': swift_config['user_domain_id'],
            'region_name': swift_config['region_name'],
        }
    )


def create_container_if_not_exists(container_name):
    """创建容器（如果不存在）"""
    try:
        swift = get_swift_connection()
        # 尝试获取容器信息，如果不存在会抛出异常
        swift.head_container(container_name)
        return True
    except Exception:
        # 容器不存在，创建容器
        try:
            swift.put_container(container_name)
            return True
        except Exception:
            return False


def upload_file_to_swift(file_obj, container_name, object_name=None):
    """上传文件到Swift"""
    if object_name is None:
        object_name = file_obj.name
    
    # 确保容器存在
    create_container_if_not_exists(container_name)
    
    try:
        swift = get_swift_connection()
        
        # 直接上传文件
        swift.put_object(
            container_name,
            object_name,
            contents=file_obj
        )
        
        return True, "Upload successful"
                
    except Exception as e:
        return False, str(e)


def delete_file_from_swift(container_name, object_name):
    """从Swift删除文件"""
    try:
        swift = get_swift_connection()
        swift.delete_object(container_name, object_name)
        return True
    except Exception as e:
        return False, str(e)


def download_file_from_swift(container_name, object_name):
    """从Swift下载文件"""
    try:
        swift = get_swift_connection()
        
        # 执行下载
        headers, file_content = swift.get_object(container_name, object_name)
        
        # 返回文件内容和头信息
        return True, (file_content, headers)
                
    except Exception as e:
        return False, str(e)


def download_file_from_local(file_obj):
    """从本地存储下载文件（Swift的备用方案）"""
    try:
        import os
        from pathlib import Path
        
        # 构建本地文件路径
        user_dir = Path(settings.LOCAL_STORAGE_PATH) / str(file_obj.owner.id)
        file_path = user_dir / file_obj.swift_object
        
        # 检查文件是否存在
        if not file_path.exists():
            return False, f"本地文件不存在: {file_path}"
        
        # 读取文件内容
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # 创建简单的头信息
        headers = {
            'Content-Length': str(len(file_content)),
            'Content-Type': file_obj.mime_type,
        }
        
        return True, (file_content, headers)
        
    except Exception as e:
        return False, str(e)


def upload_file_to_local(uploaded_file, user_id, filename):
    """上传文件到本地存储"""
    try:
        import os
        from pathlib import Path
        
        # 创建用户目录
        user_dir = Path(settings.LOCAL_STORAGE_PATH) / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        file_path = user_dir / filename
        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        return True, str(file_path)
        
    except Exception as e:
        return False, str(e)


def get_swift_temp_url(container_name, object_name, expires_in=3600):
    """获取Swift临时URL"""
    try:
        # 检查Swift服务是否可用
        swift = get_swift_connection()
        
        # 尝试列出容器来验证连接
        connection_ok = False
        for result in swift.list():
            if result.get('success', True):  # 如果没有错误，认为连接正常
                connection_ok = True
                break
        
        if not connection_ok:
            return None
            
        # 从Swift配置获取基础URL
        swift_config = settings.SWIFT_CONFIG
        auth_url = swift_config['auth_url']
        
        # 构建Swift对象存储的URL
        # 通常格式为: http://<swift-host>:<port>/v1/AUTH_<tenant-id>/<container>/<object>
        # 这里我们使用一个简化的方法，直接从auth_url推断
        if '/identity' in auth_url:
            base_url = auth_url.replace('/identity', '')
        else:
            base_url = auth_url.rstrip('/')
        
        # 添加Swift API路径
        swift_url = f"{base_url}/v1/AUTH_admin/{container_name}/{object_name}"
        
        # 由于临时URL需要密钥配置，这里先返回直接URL
        # 在生产环境中，应该配置TempURL密钥并生成签名
        return swift_url
        
    except Exception as e:
        print(f"Error generating Swift temp URL: {e}")
        return None


def get_file_mime_type(file_obj):
    """获取文件MIME类型"""
    if isinstance(file_obj, UploadedFile) and magic:
        # 对于上传的文件，尝试从内容检测
        content = file_obj.read(1024)
        file_obj.seek(0)
        try:
            mime_type = magic.from_buffer(content, mime=True)
            if mime_type:
                return mime_type
        except:
            pass
    
    # 回退到基于扩展名的检测
    filename = file_obj.name if hasattr(file_obj, 'name') else str(file_obj)
    ext = os.path.splitext(filename)[1].lower()
    
    mime_types = {
        '.txt': 'text/plain',
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.mp3': 'audio/mpeg',
        '.mp4': 'video/mp4',
        '.zip': 'application/zip',
        '.rar': 'application/x-rar-compressed',
    }
    
    return mime_types.get(ext, 'application/octet-stream')


def generate_share_code():
    """生成分享码"""
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
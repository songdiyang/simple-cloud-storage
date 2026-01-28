"""
Swift 对象存储服务

封装所有 Swift 相关操作
"""
from django.conf import settings

try:
    from swiftclient import Connection
    from swiftclient.exceptions import ClientException
    SWIFT_AVAILABLE = True
except ImportError:
    SWIFT_AVAILABLE = False
    Connection = None
    ClientException = Exception


class SwiftStorageService:
    """Swift 存储服务类"""
    
    def __init__(self):
        self._connection = None
    
    @property
    def is_available(self):
        """检查 Swift 是否可用"""
        return SWIFT_AVAILABLE
    
    def _get_config(self):
        """获取 Swift 配置"""
        return getattr(settings, 'SWIFT_CONFIG', {})
    
    def get_connection(self):
        """获取 Swift 连接"""
        if not SWIFT_AVAILABLE:
            raise RuntimeError("Swift client is not installed")
        
        swift_config = self._get_config()
        
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
    
    def create_container(self, container_name):
        """创建容器（如果不存在）"""
        try:
            swift = self.get_connection()
            # 尝试获取容器信息
            swift.head_container(container_name)
            return True
        except Exception:
            # 容器不存在，创建容器
            try:
                swift = self.get_connection()
                swift.put_container(container_name)
                return True
            except Exception:
                return False
    
    def upload_file(self, file_obj, container_name, object_name=None):
        """上传文件到 Swift
        
        Args:
            file_obj: 文件对象
            container_name: 容器名称
            object_name: 对象名称（可选）
            
        Returns:
            tuple: (success, message)
        """
        if object_name is None:
            object_name = file_obj.name
        
        # 确保容器存在
        self.create_container(container_name)
        
        try:
            swift = self.get_connection()
            swift.put_object(
                container_name,
                object_name,
                contents=file_obj
            )
            return True, "Upload successful"
        except Exception as e:
            return False, str(e)
    
    def download_file(self, container_name, object_name):
        """从 Swift 下载文件
        
        Args:
            container_name: 容器名称
            object_name: 对象名称
            
        Returns:
            tuple: (success, (content, headers) or error_message)
        """
        try:
            swift = self.get_connection()
            headers, file_content = swift.get_object(container_name, object_name)
            return True, (file_content, headers)
        except Exception as e:
            return False, str(e)
    
    def delete_file(self, container_name, object_name):
        """从 Swift 删除文件
        
        Args:
            container_name: 容器名称
            object_name: 对象名称
            
        Returns:
            tuple: (success, error_message or None)
        """
        try:
            swift = self.get_connection()
            swift.delete_object(container_name, object_name)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def get_temp_url(self, container_name, object_name, expires_in=3600):
        """获取临时访问 URL
        
        Args:
            container_name: 容器名称
            object_name: 对象名称
            expires_in: 过期时间（秒）
            
        Returns:
            str or None: 临时 URL
        """
        try:
            # 检查 Swift 服务是否可用
            swift = self.get_connection()
            
            # 验证连接
            connection_ok = False
            for result in swift.list():
                if result.get('success', True):
                    connection_ok = True
                    break
            
            if not connection_ok:
                return None
            
            # 从配置获取基础 URL
            swift_config = self._get_config()
            auth_url = swift_config['auth_url']
            
            # 构建 Swift 对象存储的 URL
            if '/identity' in auth_url:
                base_url = auth_url.replace('/identity', '')
            else:
                base_url = auth_url.rstrip('/')
            
            swift_url = f"{base_url}/v1/AUTH_admin/{container_name}/{object_name}"
            return swift_url
            
        except Exception as e:
            print(f"Error generating Swift temp URL: {e}")
            return None


# 单例实例
swift_service = SwiftStorageService()

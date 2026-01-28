"""
本地文件存储服务

作为 Swift 的备用存储方案
"""
import os
import uuid
from pathlib import Path
from django.conf import settings


class LocalStorageService:
    """本地存储服务类"""
    
    def __init__(self):
        self._storage_path = None
    
    @property
    def storage_path(self):
        """获取本地存储根路径"""
        if self._storage_path is None:
            self._storage_path = getattr(
                settings, 
                'LOCAL_STORAGE_PATH', 
                os.path.join(settings.BASE_DIR, 'local_storage')
            )
        return self._storage_path
    
    @property
    def is_enabled(self):
        """检查本地存储是否启用"""
        return getattr(settings, 'LOCAL_STORAGE_ENABLED', False)
    
    def _ensure_user_dir(self, user_id):
        """确保用户目录存在"""
        user_dir = Path(self.storage_path) / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def upload_file(self, file_obj, user_id, filename=None):
        """上传文件到本地存储
        
        Args:
            file_obj: 文件对象
            user_id: 用户 ID
            filename: 文件名（可选）
            
        Returns:
            tuple: (success, file_path or error_message)
        """
        try:
            user_dir = self._ensure_user_dir(user_id)
            
            # 生成唯一文件名
            if filename is None:
                filename = file_obj.name
            
            # 添加 UUID 前缀防止重名
            unique_name = f"{uuid.uuid4()}_{filename}"
            file_path = user_dir / unique_name
            
            # 保存文件
            with open(file_path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)
            
            return True, str(file_path)
            
        except Exception as e:
            return False, str(e)
    
    def download_file(self, file_path):
        """从本地存储下载文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            tuple: (success, (content, headers) or error_message)
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return False, f"文件不存在: {file_path}"
            
            # 读取文件内容
            with open(path, 'rb') as f:
                file_content = f.read()
            
            # 创建简单的头信息
            headers = {
                'Content-Length': str(len(file_content)),
            }
            
            return True, (file_content, headers)
            
        except Exception as e:
            return False, str(e)
    
    def delete_file(self, file_path):
        """从本地存储删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            tuple: (success, error_message or None)
        """
        try:
            path = Path(file_path)
            
            if path.exists():
                path.unlink()
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def get_file_url(self, file_path):
        """获取文件访问 URL
        
        Args:
            file_path: 文件路径
            
        Returns:
            str or None: 文件 URL
        """
        if file_path:
            media_url = getattr(settings, 'MEDIA_URL', '/media/')
            return f"{media_url}{file_path}"
        return None
    
    def get_file_size(self, file_path):
        """获取文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            int: 文件大小（字节）
        """
        try:
            path = Path(file_path)
            if path.exists():
                return path.stat().st_size
            return 0
        except Exception:
            return 0


# 单例实例
local_service = LocalStorageService()

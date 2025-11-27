"""
本地文件存储工具函数（作为Swift的备选方案）
"""
import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


def upload_file_locally(file_obj, user_id, object_name=None):
    """本地文件上传"""
    if object_name is None:
        object_name = f"{user_id}/{uuid.uuid4()}/{file_obj.name}"
    
    # 确保上传目录存在
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', str(user_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成唯一文件名
    file_extension = os.path.splitext(file_obj.name)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join('uploads', str(user_id), unique_filename)
    
    try:
        # 保存文件
        path = default_storage.save(file_path, ContentFile(file_obj.read()))
        return True, path
    except Exception as e:
        return False, str(e)


def delete_file_locally(file_path):
    """本地文件删除"""
    try:
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
        return True, None
    except Exception as e:
        return False, str(e)


def get_file_url(file_path):
    """获取文件访问URL"""
    if file_path:
        return f"{settings.MEDIA_URL}{file_path}"
    return None
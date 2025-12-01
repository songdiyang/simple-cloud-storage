import os
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Folder(models.Model):
    """文件夹模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name='文件夹名称')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='children', verbose_name='父文件夹')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所有者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '文件夹'
        verbose_name_plural = '文件夹'
        unique_together = ['parent', 'name', 'owner']
    
    def __str__(self):
        return self.name
    
    @property
    def full_path(self):
        """获取完整路径"""
        if self.parent:
            return f"{self.parent.full_path}/{self.name}"
        return f"/{self.name}"
    
    def get_ancestors(self):
        """获取所有祖先文件夹"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors[::-1]  # 反转顺序，从根到当前


class File(models.Model):
    """文件模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name='文件名')
    original_name = models.CharField(max_length=255, verbose_name='原始文件名')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True,
                              related_name='files', verbose_name='所属文件夹')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所有者')
    size = models.BigIntegerField(verbose_name='文件大小(字节)')
    file_type = models.CharField(max_length=100, verbose_name='文件类型')
    mime_type = models.CharField(max_length=200, verbose_name='MIME类型')
    swift_container = models.CharField(max_length=255, null=True, blank=True, verbose_name='Swift容器')
    swift_object = models.CharField(max_length=255, null=True, blank=True, verbose_name='Swift对象名')
    local_path = models.CharField(max_length=500, null=True, blank=True, verbose_name='本地存储路径')
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    download_count = models.IntegerField(default=0, verbose_name='下载次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '文件'
        verbose_name_plural = '文件'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def file_extension(self):
        """获取文件扩展名"""
        return os.path.splitext(self.name)[1].lower()
    
    @property
    def size_display(self):
        """格式化文件大小显示"""
        if self.size == 0:
            return "0 B"
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size_value = self.size
        while size_value >= 1024 and unit_index < len(units) - 1:
            size_value /= 1024
            unit_index += 1
        return f"{size_value:.2f} {units[unit_index]}"
    
    def get_swift_url(self):
        """获取Swift临时URL"""
        from .utils import get_swift_temp_url
        return get_swift_temp_url(self.swift_container, self.swift_object)


class FileShare(models.Model):
    """文件分享模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='shares', 
                            verbose_name='分享的文件')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='分享者')
    share_code = models.CharField(max_length=32, unique=True, verbose_name='分享码')
    password = models.CharField(max_length=128, blank=True, null=True, verbose_name='访问密码')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    expire_at = models.DateTimeField(null=True, blank=True, verbose_name='过期时间')
    max_downloads = models.IntegerField(null=True, blank=True, verbose_name='最大下载次数')
    download_count = models.IntegerField(default=0, verbose_name='下载次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '文件分享'
        verbose_name_plural = '文件分享'
    
    def __str__(self):
        return f"{self.file.name} - {self.share_code}"
    
    def is_expired(self):
        """检查是否过期"""
        from django.utils import timezone
        if self.expire_at and self.expire_at < timezone.now():
            return True
        if self.max_downloads and self.download_count >= self.max_downloads:
            return True
        return False
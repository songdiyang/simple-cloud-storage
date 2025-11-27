from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """扩展用户模型"""
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    storage_quota = models.BigIntegerField(default=5*1024*1024*1024, verbose_name='存储配额(字节)')  # 默认5GB
    used_storage = models.BigIntegerField(default=0, verbose_name='已使用存储(字节)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    @property
    def available_storage(self):
        """可用存储空间"""
        return max(0, self.storage_quota - self.used_storage)

    @property
    def storage_usage_percentage(self):
        """存储使用率"""
        if self.storage_quota == 0:
            return 0
        return min(100, (self.used_storage / self.storage_quota) * 100)
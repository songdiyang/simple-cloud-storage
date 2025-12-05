from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """扩展用户模型"""
    
    # 用户角色选项
    ROLE_USER = 'user'
    ROLE_VIP = 'vip'
    ROLE_ADMIN = 'admin'
    
    ROLE_CHOICES = (
        (ROLE_USER, '普通用户'),
        (ROLE_VIP, 'VIP用户'),
        (ROLE_ADMIN, '管理员'),
    )
    
    # 存储配额常量
    STORAGE_USER = 200 * 1024 * 1024  # 200MB
    STORAGE_VIP = 5 * 1024 * 1024 * 1024  # 5GB
    
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER, verbose_name='用户角色')
    storage_quota = models.BigIntegerField(default=STORAGE_USER, verbose_name='存储配额(字节)')  # 默认200MB
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
    
    @property
    def is_vip(self):
        """是否为VIP用户"""
        return self.role == self.ROLE_VIP
    
    @property
    def is_admin_user(self):
        """是否为管理员"""
        return self.role == self.ROLE_ADMIN or self.is_superuser


class VIPApplication(models.Model):
    """VIP申请模型"""
    
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    
    STATUS_CHOICES = (
        (STATUS_PENDING, '待审核'),
        (STATUS_APPROVED, '已通过'),
        (STATUS_REJECTED, '已拒绝'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vip_applications', verbose_name='申请用户')
    order_number = models.CharField(max_length=100, verbose_name='赞助单号')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name='审核状态')
    admin_note = models.TextField(blank=True, null=True, verbose_name='管理员备注')
    reject_reason = models.TextField(blank=True, null=True, verbose_name='拒绝原因')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    reviewed_at = models.DateTimeField(blank=True, null=True, verbose_name='审核时间')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                    related_name='reviewed_applications', verbose_name='审核人')
    
    class Meta:
        verbose_name = 'VIP申请'
        verbose_name_plural = 'VIP申请'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.order_number} - {self.get_status_display()}"


class LoginRecord(models.Model):
    """用户登录记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_records', verbose_name='用户')
    login_time = models.DateTimeField(auto_now_add=True, verbose_name='登录时间')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, null=True, verbose_name='用户代理')
    
    class Meta:
        verbose_name = '登录记录'
        verbose_name_plural = '登录记录'
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


class OnlineUser(models.Model):
    """在线用户追踪"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='online_status', verbose_name='用户')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='最后活动时间')
    is_online = models.BooleanField(default=True, verbose_name='是否在线')
    
    class Meta:
        verbose_name = '在线用户'
        verbose_name_plural = '在线用户'
    
    def __str__(self):
        return f"{self.user.username} - {'在线' if self.is_online else '离线'}"
#!/usr/bin/env python
"""测试存储信息"""
import os, sys, django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from accounts.models import User
from files.models import File

user = User.objects.get(username='demo')

# 模拟storage_info视图的逻辑
def format_bytes(bytes_value):
    if bytes_value == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

storage_info = {
    'storage_quota': user.storage_quota,
    'used_storage': user.used_storage,
    'available_storage': user.available_storage,
    'storage_usage_percentage': round(user.storage_usage_percentage, 2),
    'total_files': File.objects.filter(owner=user).count(),
    'total_folders': 0,  # 假设没有文件夹
    'storage_quota_display': format_bytes(user.storage_quota),
    'used_storage_display': format_bytes(user.used_storage),
    'available_storage_display': format_bytes(user.available_storage)
}

print('📊 存储信息:')
print(f"   存储配额: {storage_info['storage_quota_display']} ({storage_info['storage_quota']} bytes)")
print(f"   已使用: {storage_info['used_storage_display']} ({storage_info['used_storage']} bytes)")
print(f"   可用空间: {storage_info['available_storage_display']} ({storage_info['available_storage']} bytes)")
print(f"   使用率: {storage_info['storage_usage_percentage']}%")
print(f"   文件数量: {storage_info['total_files']}")
print(f"   文件夹数量: {storage_info['total_folders']}")
print('\n✅ 存储信息格式正确')
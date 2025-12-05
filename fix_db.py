import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# 添加 role 字段
try:
    cursor.execute("ALTER TABLE accounts_user ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL")
    print("role 字段添加成功")
except Exception as e:
    if 'Duplicate column' in str(e):
        print("role 字段已存在")
    else:
        print(f"role 字段添加失败: {e}")

# 创建管理员用户
from accounts.models import User

try:
    user = User.objects.filter(username='123').first()
    if user:
        print(f"用户 123 已存在，更新为管理员")
        user.role = 'admin'
        user.storage_quota = 5 * 1024 * 1024 * 1024
        user.save()
    else:
        user = User.objects.create_user(username='123', password='123')
        user.role = 'admin'
        user.storage_quota = 5 * 1024 * 1024 * 1024
        user.save()
        print(f"管理员账号创建成功: 用户名=123, 密码=123")
    
    print(f"用户角色: {user.get_role_display()}")
except Exception as e:
    print(f"创建用户失败: {e}")

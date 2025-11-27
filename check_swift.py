#!/usr/bin/env python
"""检查Swift状态"""
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from files.utils import get_swift_connection
from accounts.models import User
from files.models import File

try:
    swift = get_swift_connection()
    print('✅ Swift连接成功')
    
    containers = swift.get_account()[1]
    print(f'📦 找到 {len(containers)} 个容器')
    for container in containers:
        print(f'   - {container["name"]}')
    
    user = User.objects.get(username='demo')
    files = File.objects.filter(owner=user)
    print(f'\n📁 Demo用户有 {files.count()} 个文件')
    
    for file_obj in files[:3]:
        print(f'\n🔍 检查文件: {file_obj.original_name}')
        print(f'   容器: {file_obj.swift_container}')
        print(f'   对象: {file_obj.swift_object}')
        
        try:
            metadata = swift.head_object(file_obj.swift_container, file_obj.swift_object)
            print(f'   ✅ 对象存在，大小: {metadata.get("content-length", "未知")} bytes')
        except Exception as e:
            print(f'   ❌ 对象不存在或无法访问: {str(e)}')

except Exception as e:
    print(f'❌ Swift连接失败: {str(e)}')
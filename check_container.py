#!/usr/bin/env python
"""检查容器内容"""
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from files.utils import get_swift_connection

swift = get_swift_connection()
container_name = 'user_1_files'

try:
    objects = swift.get_container(container_name)[1]
    print(f'容器 {container_name} 中有 {len(objects)} 个对象:')
    for obj in objects:
        print(f'   - {obj["name"]} ({obj.get("bytes", 0)} bytes)')
        
except Exception as e:
    print(f'获取容器对象失败: {str(e)}')
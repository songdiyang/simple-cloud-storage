#!/usr/bin/env python
"""检查下载问题"""
import os, sys, django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from accounts.models import User
from files.models import File
from files.utils import download_file_from_swift

user = User.objects.get(username='demo')
files = File.objects.filter(owner=user)

print(f'用户文件列表:')
for file_obj in files:
    print(f'  - {file_obj.original_name} ({file_obj.mime_type}, {file_obj.size} bytes)')
    
    # 测试下载
    success, result = download_file_from_swift(file_obj.swift_container, file_obj.swift_object)
    if success:
        content, headers = result
        print(f'    实际内容长度: {len(content)} bytes')
        print(f'    Content-Type: {headers.get("content-type", "未知")}')
        
        # 检查内容前几个字节
        if len(content) >= 10:
            print(f'    内容前10字节: {content[:10]}')
        
        # 检查是否是图片文件
        if file_obj.mime_type.startswith('image/'):
            # 检查图片文件头
            if content.startswith(b'\xFF\xD8\xFF'):
                print('    ✅ JPEG文件头正确')
            elif content.startswith(b'\x89PNG'):
                print('    ✅ PNG文件头正确')
            else:
                print('    ❌ 图片文件头不正确')
    else:
        print(f'    ❌ 下载失败: {result}')
    print()
#!/usr/bin/env python
"""测试图片下载"""
import os, sys, django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from accounts.models import User
from files.models import File
from files.utils import download_file_from_swift

user = User.objects.get(username='demo')
file_obj = File.objects.filter(owner=user, mime_type__startswith='image/').first()

if file_obj:
    print(f'测试下载图片: {file_obj.original_name}')
    
    success, result = download_file_from_swift(file_obj.swift_container, file_obj.swift_object)
    if success:
        content, headers = result
        
        # 保存到临时文件测试
        temp_path = f'temp_{file_obj.original_name}'
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        print(f'✅ 下载成功，保存为: {temp_path}')
        print(f'   文件大小: {len(content)} bytes')
        
        # 验证文件
        if file_obj.mime_type == 'image/png':
            if content.startswith(b'\x89PNG'):
                print('   ✅ PNG文件验证成功')
            else:
                print('   ❌ PNG文件验证失败')
        elif file_obj.mime_type == 'image/jpeg':
            if content.startswith(b'\xFF\xD8\xFF'):
                print('   ✅ JPEG文件验证成功')
            else:
                print('   ❌ JPEG文件验证失败')
    else:
        print(f'❌ 下载失败: {result}')
else:
    print('❌ 没有找到图片文件')
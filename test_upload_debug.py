#!/usr/bin/env python
"""
测试文件上传的完整流程
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from accounts.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from files.utils import upload_file_to_swift
from files.models import File, Folder

def test_upload():
    print("=== 开始测试文件上传流程 ===")
    
    # 1. 检查用户
    try:
        user = User.objects.first()
        if not user:
            print("❌ 没有找到用户，请先创建用户")
            return False
        print(f"✅ 找到用户: {user.username}")
    except Exception as e:
        print(f"❌ 用户检查失败: {e}")
        return False
    
    # 2. 创建测试文件
    try:
        test_file = SimpleUploadedFile(
            "test_upload.txt", 
            b"This is a test file for upload testing", 
            content_type="text/plain"
        )
        print(f"✅ 创建测试文件: {test_file.name} ({test_file.size} bytes)")
    except Exception as e:
        print(f"❌ 创建测试文件失败: {e}")
        return False
    
    # 3. 测试Swift上传
    try:
        container_name = f"user_{user.id}_files"
        object_name = f"{user.id}/test-uuid/{test_file.name}"
        
        success, result = upload_file_to_swift(test_file, container_name, object_name)
        if success:
            print(f"✅ Swift上传成功: {result}")
        else:
            print(f"❌ Swift上传失败: {result}")
            return False
    except Exception as e:
        print(f"❌ Swift上传异常: {e}")
        return False
    
    # 4. 测试数据库记录创建
    try:
        file_obj = File.objects.create(
            name=test_file.name,
            original_name=test_file.name,
            folder=None,
            owner=user,
            size=test_file.size,
            file_type='.txt',
            mime_type='text/plain',
            swift_container=container_name,
            swift_object=object_name
        )
        print(f"✅ 数据库记录创建成功: {file_obj.id}")
    except Exception as e:
        print(f"❌ 数据库记录创建失败: {e}")
        # 清理Swift文件
        try:
            from files.utils import delete_file_from_swift
            delete_file_from_swift(container_name, object_name)
        except:
            pass
        return False
    
    # 5. 测试文件下载
    try:
        from files.utils import download_file_from_swift
        success, result = download_file_from_swift(container_name, object_name)
        if success:
            content, headers = result
            print(f"✅ 文件下载成功: {len(content)} bytes")
        else:
            print(f"❌ 文件下载失败: {result}")
    except Exception as e:
        print(f"❌ 文件下载异常: {e}")
    
    # 6. 清理测试数据
    try:
        file_obj.delete()
        from files.utils import delete_file_from_swift
        delete_file_from_swift(container_name, object_name)
        print("✅ 测试数据清理完成")
    except Exception as e:
        print(f"⚠️ 清理失败: {e}")
    
    print("=== 测试完成 ===")
    return True

if __name__ == "__main__":
    test_upload()
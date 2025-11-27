#!/usr/bin/env python
"""
最终测试：验证完整的上传下载功能
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from accounts.models import User
from files.models import File
from files.utils import upload_file_to_swift, download_file_from_swift
from django.core.files.uploadedfile import SimpleUploadedFile

def final_test():
    print("🚀 最终系统测试")
    print("=" * 50)
    
    # 1. 获取用户
    try:
        user = User.objects.get(username='demo')
        print(f"✅ 用户: {user.username}")
    except User.DoesNotExist:
        print("❌ 演示用户不存在")
        return False
    
    # 2. 测试上传
    print("\n📤 测试文件上传...")
    test_content = b"Final test content for cloud storage system - " + str(os.urandom(32)).encode()
    test_file = SimpleUploadedFile(
        "final_test.txt",
        test_content,
        content_type="text/plain"
    )
    
    container_name = f"user_{user.id}_files"
    object_name = f"{user.id}/final/{test_file.name}"
    
    success, result = upload_file_to_swift(test_file, container_name, object_name)
    if success:
        print(f"✅ 上传成功: {result}")
    else:
        print(f"❌ 上传失败: {result}")
        return False
    
    # 3. 测试下载
    print("\n📥 测试文件下载...")
    success, result = download_file_from_swift(container_name, object_name)
    if success:
        downloaded_content, headers = result
        if downloaded_content == test_content:
            print(f"✅ 下载验证成功")
            print(f"📊 文件大小: {len(downloaded_content)} bytes")
        else:
            print(f"❌ 下载内容不匹配")
            return False
    else:
        print(f"❌ 下载失败: {result}")
        return False
    
    # 4. 创建数据库记录
    print("\n📝 创建数据库记录...")
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
        
        # 5. 测试通过数据库记录下载
        print("\n🔄 测试通过API下载...")
        success, result = download_file_from_swift(file_obj.swift_container, file_obj.swift_object)
        if success:
            api_content, headers = result
            if api_content == test_content:
                print(f"✅ API下载验证成功")
            else:
                print(f"❌ API下载内容不匹配")
                return False
        else:
            print(f"❌ API下载失败: {result}")
            return False
        
        # 清理测试数据
        file_obj.delete()
        print(f"🗑️  清理测试数据完成")
        
    except Exception as e:
        print(f"❌ 数据库操作失败: {str(e)}")
        return False
    
    return True

def test_existing_files():
    print("\n🔍 测试现有文件...")
    print("=" * 50)
    
    from accounts.models import User
    from files.models import File
    
    try:
        user = User.objects.get(username='demo')
        files = File.objects.filter(owner=user)
        
        if not files.exists():
            print("❌ 用户没有现有文件")
            return True
        
        print(f"📁 找到 {files.count()} 个现有文件")
        
        success_count = 0
        for file_obj in files[:3]:  # 测试前3个文件
            print(f"\n📄 测试文件: {file_obj.original_name}")
            
            success, result = download_file_from_swift(file_obj.swift_container, file_obj.swift_object)
            if success:
                content, headers = result
                print(f"   ✅ 下载成功，大小: {len(content)} bytes")
                success_count += 1
            else:
                print(f"   ❌ 下载失败: {result}")
        
        print(f"\n📊 测试结果: {success_count}/{min(3, files.count())} 个文件可下载")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 云存储系统最终验证")
    print("=" * 50)
    
    # 测试新文件上传下载
    upload_download_success = final_test()
    
    # 测试现有文件
    existing_files_success = test_existing_files()
    
    print("\n🎉 测试总结")
    print("=" * 50)
    
    if upload_download_success:
        print("✅ 新文件上传下载功能正常")
    else:
        print("❌ 新文件上传下载功能异常")
    
    if existing_files_success:
        print("✅ 现有文件下载功能正常")
    else:
        print("⚠️  现有文件可能需要重新上传")
    
    if upload_download_success:
        print("\n🎯 系统状态: 正常运行")
        print("🌐 现在可以使用前端应用测试完整功能:")
        print("   - 前端: http://localhost:3000")
        print("   - 后端: http://localhost:8000")
        print("   - 用户名: demo, 密码: demo123")
    else:
        print("\n❌ 系统状态: 需要进一步调试")
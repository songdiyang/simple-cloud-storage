#!/usr/bin/env python
"""
测试下载功能修复效果
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
from files.utils import download_file_from_swift, download_file_from_local

def test_download_functionality():
    print("🔧 测试下载功能修复效果")
    print("=" * 50)
    
    # 获取演示用户
    try:
        user = User.objects.get(username='demo')
        print(f"✅ 找到用户: {user.username}")
    except User.DoesNotExist:
        print("❌ 演示用户不存在")
        return
    
    # 获取用户的文件
    files = File.objects.filter(owner=user)
    if not files.exists():
        print("❌ 用户没有文件")
        return
    
    print(f"📁 找到 {files.count()} 个文件")
    
    for file_obj in files[:3]:  # 测试前3个文件
        print(f"\n📄 测试文件: {file_obj.original_name}")
        print(f"   大小: {file_obj.size} bytes")
        print(f"   Swift容器: {file_obj.swift_container}")
        print(f"   Swift对象: {file_obj.swift_object}")
        
        # 测试Swift下载
        print("   🔄 测试Swift下载...")
        swift_success, swift_result = download_file_from_swift(file_obj.swift_container, file_obj.swift_object)
        if swift_success:
            file_content, headers = swift_result
            print(f"   ✅ Swift下载成功，内容大小: {len(file_content)} bytes")
        else:
            print(f"   ❌ Swift下载失败: {swift_result}")
        
        # 测试本地下载
        print("   🔄 测试本地下载...")
        local_success, local_result = download_file_from_local(file_obj)
        if local_success:
            file_content, headers = local_result
            print(f"   ✅ 本地下载成功，内容大小: {len(file_content)} bytes")
        else:
            print(f"   ❌ 本地下载失败: {local_result}")
        
        # 总结
        if swift_success or local_success:
            print("   🎉 至少有一种下载方式可用")
        else:
            print("   ⚠️  所有下载方式都不可用")

def test_upload_functionality():
    print("\n🔧 测试上传功能修复效果")
    print("=" * 50)
    
    from io import BytesIO
    from django.core.files.uploadedfile import SimpleUploadedFile
    from files.utils import upload_file_to_local
    from accounts.models import User
    
    # 获取演示用户
    try:
        user = User.objects.get(username='demo')
    except User.DoesNotExist:
        print("❌ 演示用户不存在")
        return
    
    # 创建测试文件
    test_content = "This is a test file content for upload verification.".encode('utf-8')
    test_file = SimpleUploadedFile(
        "test_download_fix.txt",
        test_content,
        content_type="text/plain"
    )
    
    print(f"📤 测试上传文件: {test_file.name}")
    print(f"   文件大小: {test_file.size} bytes")
    
    # 测试本地上传
    object_name = f"{user.id}/test/{test_file.name}"
    local_success, local_result = upload_file_to_local(test_file, user.id, object_name)
    
    if local_success:
        print(f"   ✅ 本地上传成功: {local_result}")
        
        # 立即测试下载
        print("   🔄 立即测试下载...")
        from files.utils import download_file_from_local
        from files.models import File
        
        # 创建临时文件记录用于测试
        temp_file = File(
            owner=user,
            original_name=test_file.name,
            swift_object=object_name,
            size=test_file.size,
            mime_type="text/plain"
        )
        
        download_success, download_result = download_file_from_local(temp_file)
        if download_success:
            downloaded_content, headers = download_result
            if downloaded_content == test_content:
                print("   ✅ 下载验证成功，内容匹配")
            else:
                print("   ❌ 下载验证失败，内容不匹配")
        else:
            print(f"   ❌ 下载验证失败: {download_result}")
    else:
        print(f"   ❌ 本地上传失败: {local_result}")

if __name__ == "__main__":
    test_download_functionality()
    test_upload_functionality()
    
    print("\n🎉 测试完成")
    print("=" * 50)
    print("💡 提示:")
    print("   - 如果Swift下载失败但本地下载成功，说明修复生效")
    print("   - 新上传的文件会同时保存到Swift和本地")
    print("   - 下载时会优先尝试Swift，失败后自动切换到本地")
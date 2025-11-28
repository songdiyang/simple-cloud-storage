#!/usr/bin/env python
"""测试分享功能"""
import os, sys, django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from accounts.models import User
from files.models import File, FileShare
from files.utils import generate_share_code

def test_share_functionality():
    print("🔗 测试分享功能")
    print("=" * 50)
    
    user = User.objects.get(username='demo')
    file_obj = File.objects.filter(owner=user).first()
    
    if not file_obj:
        print("❌ 没有找到文件")
        return
    
    print(f"📄 测试文件: {file_obj.original_name}")
    
    # 1. 创建分享
    share = FileShare.objects.create(
        file=file_obj,
        owner=user,
        share_code=generate_share_code(),
        max_downloads=10
    )
    
    print(f"✅ 分享创建成功: {share.share_code}")
    print(f"🔗 分享链接: http://localhost:3000/share/{share.share_code}")
    
    # 2. 测试分享信息获取
    from files.views import get_share_info
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.get(f'/api/files/share/{share.share_code}/')
    
    try:
        response = get_share_info(request, share.share_code)
        if response.status_code == 200:
            data = response.data
            print(f"✅ 分享信息获取成功:")
            print(f"   文件名: {data['file_name']}")
            print(f"   文件大小: {data['file_size']} bytes")
            print(f"   下载次数: {data['download_count']}/{data['max_downloads']}")
            print(f"   是否过期: {data['is_expired']}")
        else:
            print(f"❌ 分享信息获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    # 3. 显示所有分享
    print(f"\n📋 用户的所有分享:")
    shares = FileShare.objects.filter(owner=user)
    for s in shares:
        status = "✅ 有效" if s.is_active and not s.is_expired() else "❌ 无效"
        print(f"   {s.file.original_name} - {s.share_code} - {status}")

if __name__ == "__main__":
    test_share_functionality()
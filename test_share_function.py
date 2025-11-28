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
    
    try:
        # 获取用户和文件
        user = User.objects.get(username='demo')
        file_obj = File.objects.filter(owner=user).first()
        
        if not file_obj:
            print("❌ 没有找到测试文件")
            return False
        
        print(f"✅ 找到测试文件: {file_obj.original_name}")
        
        # 1. 测试创建分享
        print("\n📤 创建分享...")
        share = FileShare.objects.create(
            file=file_obj,
            owner=user,
            share_code=generate_share_code(),
            max_downloads=10,
            is_active=True
        )
        
        print(f"✅ 分享创建成功")
        print(f"   分享码: {share.share_code}")
        print(f"   分享链接: http://localhost:3000/share/{share.share_code}")
        
        # 2. 测试分享信息获取
        print("\n🔍 测试分享信息获取...")
        from django.test import RequestFactory
        from files.views import get_share_info
        
        factory = RequestFactory()
        request = factory.get(f'/api/files/share/{share.share_code}/')
        
        response = get_share_info(request, share.share_code)
        
        if response.status_code == 200:
            data = response.data
            print(f"✅ 分享信息获取成功")
            print(f"   文件名: {data['file_name']}")
            print(f"   文件大小: {data['file_size']} bytes")
            print(f"   下载次数: {data['download_count']}/{data['max_downloads']}")
        else:
            print(f"❌ 分享信息获取失败: {response.data}")
            return False
        
        # 3. 测试分享下载
        print("\n⬇️ 测试分享下载...")
        from files.views import download_shared_file
        
        request = factory.post(f'/api/files/share/{share.share_code}/download/')
        response = download_shared_file(request, share.share_code)
        
        if response.status_code == 200:
            print("✅ 分享下载成功")
            print(f"   响应类型: {type(response)}")
            print(f"   Content-Type: {response.get('Content-Type')}")
            print(f"   Content-Disposition: {response.get('Content-Disposition')}")
        else:
            print(f"❌ 分享下载失败: {response.data}")
            return False
        
        # 4. 检查下载次数更新
        share.refresh_from_db()
        print(f"\n📊 下载统计更新: {share.download_count} 次")
        
        # 5. 测试分享列表
        print("\n📋 测试分享列表...")
        from files.views import my_shares
        
        # 模拟已认证的请求
        request = factory.get('/api/files/shares/')
        request.user = user
        
        response = my_shares(request)
        
        if response.status_code == 200:
            shares = response.data
            print(f"✅ 分享列表获取成功，共 {len(shares)} 个分享")
            for s in shares:
                print(f"   - {s['file_name']} ({s['share_code']})")
        else:
            print(f"❌ 分享列表获取失败: {response.data}")
            return False
        
        # 清理测试数据
        share.delete()
        print("\n🗑️ 测试数据清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_share_functionality()
    
    if success:
        print("\n🎉 分享功能测试通过！")
        print("\n📱 前端测试步骤:")
        print("1. 访问 http://localhost:3000")
        print("2. 登录 demo/demo123")
        print("3. 进入文件管理页面")
        print("4. 点击文件操作菜单中的'分享'按钮")
        print("5. 创建分享并复制链接")
        print("6. 在新窗口中打开分享链接测试下载")
    else:
        print("\n❌ 分享功能测试失败")
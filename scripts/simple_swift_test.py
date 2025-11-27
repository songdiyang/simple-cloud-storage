#!/usr/bin/env python
"""
简单的Swift测试
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from files.utils import get_swift_connection, upload_file_to_swift, download_file_from_swift

def test_simple_swift():
    print("🚀 简单Swift测试")
    print("=" * 50)
    
    try:
        # 测试连接
        print("🔄 测试Swift连接...")
        swift = get_swift_connection()
        print("✅ Swift连接成功!")
        
        # 获取账户信息
        account_info = swift.get_account()
        print(f"📊 容器数: {account_info[0].get('x-account-container-count', 'N/A')}")
        print(f"📊 对象数: {account_info[0].get('x-account-object-count', 'N/A')}")
        
        # 测试上传下载
        print("\n🔄 测试上传下载...")
        from io import BytesIO
        
        test_content = b"Simple Swift test content - " + str(os.urandom(16)).encode()
        test_file = BytesIO(test_content)
        
        # 上传
        success, result = upload_file_to_swift(test_file, "simple_test", "test.txt")
        if success:
            print("✅ 上传成功!")
            
            # 下载
            success, result = download_file_from_swift("simple_test", "test.txt")
            if success:
                downloaded_content, headers = result
                if downloaded_content == test_content:
                    print("✅ 下载验证成功!")
                    print("🎉 Swift功能完全正常!")
                    return True
                else:
                    print("❌ 下载内容不匹配")
            else:
                print(f"❌ 下载失败: {result}")
        else:
            print(f"❌ 上传失败: {result}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)[:200]}")
        import traceback
        traceback.print_exc()
    
    return False

if __name__ == "__main__":
    success = test_simple_swift()
    
    if success:
        print("\n🎯 Swift服务已修复!")
        print("请重启Django服务并测试上传下载功能")
    else:
        print("\n❌ Swift服务仍有问题")
        print("请检查Swift配置和服务状态")
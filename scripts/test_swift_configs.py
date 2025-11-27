#!/usr/bin/env python
"""
测试不同的Swift配置
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from swiftclient.service import SwiftService, SwiftUploadObject

def test_swift_config(auth_url, object_storage_url):
    """测试特定Swift配置"""
    config = {
        'auth_version': '3',
        'auth_url': auth_url,
        'username': 'admin',
        'password': 'devstack123',
        'project_name': 'admin',
        'project_domain_id': 'default',
        'user_domain_id': 'default',
        'region_name': 'RegionOne',
        'object_storage_url': object_storage_url,
    }
    
    print(f"\n🔍 测试配置:")
    print(f"   认证URL: {auth_url}")
    print(f"   对象存储URL: {object_storage_url}")
    
    try:
        with SwiftService(options=config) as swift:
            # 测试基本连接
            print("   🔄 测试认证...")
            auth_success = False
            
            for stat in swift.stat():
                if stat['success']:
                    auth_success = True
                    headers = stat['headers']
                    print("   ✅ 认证成功")
                    print(f"   📊 容器数: {headers.get('x-account-container-count', 'N/A')}")
                    print(f"   📊 对象数: {headers.get('x-account-object-count', 'N/A')}")
                    break
                else:
                    print(f"   ❌ 认证失败: {stat.get('error', 'Unknown')}")
                    return False
            
            if not auth_success:
                return False
            
            # 测试上传下载
            print("   🔄 测试上传下载...")
            test_content = b"Test Swift functionality - " + str(os.urandom(16))
            test_container = "test_config_container"
            test_object = "test_config.txt"
            
            # 创建容器
            try:
                for result in swift.post(container=test_container):
                    if not result['success']:
                        print(f"      ❌ 容器创建失败: {result.get('error', 'Unknown')}")
                        return False
            except Exception as e:
                print(f"      ⚠️  容器创建异常: {str(e)[:50]}")
            
            # 上传
            upload_obj = SwiftUploadObject(test_content, object_name=test_object)
            upload_success = False
            
            for result in swift.upload(container=test_container, objects=[upload_obj]):
                if result['success']:
                    upload_success = True
                    print(f"      ✅ 上传成功")
                else:
                    print(f"      ❌ 上传失败: {result.get('error', 'Unknown')}")
                    return False
            
            if not upload_success:
                return False
            
            # 下载
            download_success = False
            for result in swift.download(container=test_container, objects=[test_object]):
                if result['success']:
                    downloaded_content = result['contents']
                    if downloaded_content == test_content:
                        download_success = True
                        print(f"      ✅ 下载验证成功")
                    else:
                        print(f"      ❌ 下载内容不匹配")
                else:
                    print(f"      ❌ 下载失败: {result.get('error', 'Unknown')}")
            
            # 清理
            try:
                for result in swift.delete(container=test_container, objects=[test_object]):
                    pass
            except:
                pass
            
            if download_success:
                print(f"   🎉 配置测试成功!")
                return True
            else:
                return False
                
    except Exception as e:
        print(f"   ❌ 测试异常: {str(e)[:100]}")
        return False

def main():
    print("🚀 Swift配置测试工具")
    print("=" * 50)
    
    # 测试不同的配置组合
    auth_urls = [
        'http://192.168.219.143/identity',
        'http://192.168.219.143:5000/v3',
        'http://192.168.219.143:35357/v3',
    ]
    
    object_storage_urls = [
        'http://192.168.219.143:8080/v1',
        'http://192.168.219.143:8888/v1',
        'http://192.168.219.143:80/v1',
        'http://192.168.219.143/v1',
    ]
    
    working_configs = []
    
    for auth_url in auth_urls:
        for obj_url in object_storage_urls:
            if test_swift_config(auth_url, obj_url):
                working_configs.append({
                    'auth_url': auth_url,
                    'object_storage_url': obj_url
                })
    
    if working_configs:
        print(f"\n🎉 找到 {len(working_configs)} 个可用配置:")
        
        for i, config in enumerate(working_configs, 1):
            print(f"\n配置 {i}:")
            print(f"  认证URL: {config['auth_url']}")
            print(f"  对象存储URL: {config['object_storage_url']}")
            
            print(f"\n📝 更新settings.py配置:")
            print(f"SWIFT_CONFIG = {{")
            print(f"    'auth_version': '3',")
            print(f"    'auth_url': '{config['auth_url']}',")
            print(f"    'username': 'admin',")
            print(f"    'password': 'devstack123',")
            print(f"    'project_name': 'admin',")
            print(f"    'project_domain_id': 'default',")
            print(f"    'user_domain_id': 'default',")
            print(f"    'region_name': 'RegionOne',")
            print(f"    'object_storage_url': '{config['object_storage_url']}',")
            print(f"}}")
            
            if i == 1:  # 只显示第一个配置的详细设置
                print(f"\n🔧 请将上述配置复制到 settings.py，然后重启Django服务")
                
    else:
        print(f"\n❌ 未找到可用的Swift配置")
        print("\n💡 可能的问题:")
        print("1. Swift代理服务未正确配置")
        print("2. 防火墙阻止了端口访问")
        print("3. Swift服务未完全启动")
        print("4. 认证信息不正确")

if __name__ == "__main__":
    main()
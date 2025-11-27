#!/usr/bin/env python
"""
找到正确的Swift对象存储URL
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from swiftclient.service import SwiftService, SwiftUploadObject
from swiftclient.exceptions import ClientException
import requests

def find_swift_endpoints():
    """找到Swift的所有端点"""
    
    # 基础配置
    config = {
        'auth_version': '3',
        'auth_url': 'http://192.168.219.143/identity',
        'username': 'admin',
        'password': 'devstack123',
        'project_name': 'admin',
        'project_domain_id': 'default',
        'user_domain_id': 'default',
        'region_name': 'RegionOne',
    }
    
    print("🔍 查找Swift服务端点")
    print("=" * 50)
    
    try:
        with SwiftService(options=config) as swift:
            # 获取认证信息
            for stat in swift.stat():
                if stat['success']:
                    headers = stat['headers']
                    print("✅ 认证成功")
                    print(f"📊 账户信息:")
                    for key, value in headers.items():
                        if key.startswith('x-account'):
                            print(f"   {key}: {value}")
                    
                    # 从响应头中查找存储URL
                    storage_url = headers.get('x-storage-url')
                    if storage_url:
                        print(f"\n🎯 找到存储URL: {storage_url}")
                        
                        # 测试这个URL
                        test_storage_url(storage_url, config)
                        return storage_url
                    else:
                        print("\n❌ 未找到x-storage-url头")
                        
                        # 尝试手动构建URL
                        print("\n🔧 尝试手动构建存储URL...")
                        auth_url = config['auth_url']
                        
                        # 从认证URL推断存储URL
                        if '/identity' in auth_url:
                            base_url = auth_url.replace('/identity', '')
                        elif ':5000' in auth_url:
                            base_url = auth_url.replace(':5000', '')
                        else:
                            base_url = auth_url
                        
                        possible_urls = [
                            f"{base_url}:8080/v1",
                            f"{base_url}:8888/v1", 
                            f"{base_url}:80/v1",
                            f"{base_url}/v1",
                            f"http://192.168.219.143:8080/v1",
                            f"http://192.168.219.143:8888/v1",
                            f"http://192.168.219.143:80/v1",
                        ]
                        
                        for url in possible_urls:
                            print(f"\n🔍 测试URL: {url}")
                            test_storage_url(url, config)
                            
                else:
                    print(f"❌ 认证失败: {stat.get('error', 'Unknown error')}")
                    
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")

def test_storage_url(storage_url, config):
    """测试存储URL"""
    try:
        # 直接HTTP测试
        response = requests.get(storage_url, timeout=5)
        print(f"   HTTP状态: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ URL有效（需要认证）")
            
            # 尝试使用这个URL进行Swift操作
            test_config = config.copy()
            test_config['object_storage_url'] = storage_url
            
            if test_swift_operations(test_config):
                print(f"   🎉 这个URL可用!")
                
                # 生成最终配置
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
                print(f"    'object_storage_url': '{storage_url}',")
                print(f"}}")
                
                return True
                
        elif response.status_code == 404:
            print("   ❌ URL不存在")
        elif response.status_code == 200:
            print("   ✅ URL可访问")
            
            # 测试Swift操作
            test_config = config.copy()
            test_config['object_storage_url'] = storage_url
            
            if test_swift_operations(test_config):
                print(f"   🎉 这个URL可用!")
                return True
        else:
            print(f"   ⚠️  状态码: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("   ❌ 连接错误")
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)[:50]}")
    
    return False

def test_swift_operations(config):
    """测试Swift操作"""
    try:
        test_content = b"Test content for Swift verification"
        test_container = "test_url_container"
        test_object = "test_url.txt"
        
        with SwiftService(options=config) as swift:
            # 创建容器
            try:
                for result in swift.post(container=test_container):
                    if not result['success']:
                        print(f"      ❌ 容器创建失败: {result.get('error', 'Unknown')}")
                        return False
            except:
                pass
            
            # 上传测试
            upload_obj = SwiftUploadObject(test_content, object_name=test_object)
            upload_success = False
            
            for result in swift.upload(container=test_container, objects=[upload_obj]):
                if result['success']:
                    upload_success = True
                    print(f"      ✅ 上传成功")
                else:
                    print(f"      ❌ 上传失败: {result.get('error', 'Unknown')}")
                    return False
            
            if upload_success:
                # 下载测试
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
                
                return download_success
            
    except Exception as e:
        print(f"      ❌ Swift操作失败: {str(e)[:50]}")
    
    return False

if __name__ == "__main__":
    print("🚀 Swift端点查找工具")
    print("=" * 50)
    
    find_swift_endpoints()
    
    print("\n🎯 下一步操作")
    print("=" * 50)
    print("1. 如果找到可用的URL，请更新settings.py")
    print("2. 重启Django服务")
    print("3. 测试上传下载功能")
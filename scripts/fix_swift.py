#!/usr/bin/env python
"""
修复Swift存储服务
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

def test_swift_ports():
    """测试不同的Swift端口"""
    import socket
    
    host = "192.168.219.143"
    ports = [80, 8080, 8888, 7480, 5000, 35357]
    
    print("🔍 测试Swift服务端口")
    print("=" * 40)
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ 端口 {port} 开放")
                
                # 测试HTTP响应
                try:
                    import urllib.request
                    url = f"http://{host}:{port}"
                    response = urllib.request.urlopen(url, timeout=3)
                    status = response.getcode()
                    print(f"   HTTP状态: {status}")
                    
                    # 读取响应头
                    headers = dict(response.headers)
                    if 'server' in headers:
                        print(f"   服务器: {headers['server']}")
                        
                except Exception as e:
                    print(f"   HTTP测试失败: {str(e)[:50]}")
            else:
                print(f"❌ 端口 {port} 关闭")
                
        except Exception as e:
            print(f"❌ 端口 {port} 测试异常: {str(e)[:50]}")
    
    print()

def test_swift_with_different_configs():
    """测试不同的Swift配置"""
    from cloud_storage import settings
    
    # 基础配置
    base_config = {
        'auth_version': '3',
        'username': 'admin',
        'password': 'devstack123',
        'project_name': 'admin',
        'project_domain_id': 'default',
        'user_domain_id': 'default',
        'region_name': 'RegionOne',
    }
    
    # 不同的auth_url配置
    auth_urls = [
        'http://192.168.219.143/identity',
        'http://192.168.219.143:5000/v3',
        'http://192.168.219.143:35357/v3',
    ]
    
    # 不同的object_storage_url配置
    object_storage_urls = [
        'http://192.168.219.143:8080/v1',
        'http://192.168.219.143:8888/v1',
        'http://192.168.219.143:80/v1',
        'http://192.168.219.143:7480/v1',
    ]
    
    print("🔧 测试Swift配置组合")
    print("=" * 40)
    
    for auth_url in auth_urls:
        print(f"\n🔍 测试认证URL: {auth_url}")
        
        config = base_config.copy()
        config['auth_url'] = auth_url
        
        try:
            # 测试认证
            with SwiftService(options=config) as swift:
                # 尝试获取账户信息
                stats = swift.stat()
                print(f"   ✅ 认证成功")
                
                # 获取account信息
                for stat in stats:
                    if stat['success']:
                        headers = stat['headers']
                        account = headers.get('x-account-container-count', 'N/A')
                        objects = headers.get('x-account-object-count', 'N/A')
                        bytes_used = headers.get('x-account-bytes-used', 'N/A')
                        print(f"   📊 容器数: {account}, 对象数: {objects}, 字节数: {bytes_used}")
                        
                        # 如果认证成功，测试不同的对象存储URL
                        for obj_url in object_storage_urls:
                            print(f"      🔍 测试对象存储URL: {obj_url}")
                            test_swift_upload_download(config, obj_url)
                    else:
                        print(f"   ❌ 账户信息获取失败: {stat.get('error', 'Unknown error')}")
                        
        except Exception as e:
            print(f"   ❌ 认证失败: {str(e)[:100]}")

def test_swift_upload_download(auth_config, object_storage_url):
    """测试Swift上传下载"""
    try:
        # 创建临时配置
        config = auth_config.copy()
        config['object_storage_url'] = object_storage_url
        
        test_content = b"Test content for Swift verification"
        test_container = "test_fix_container"
        test_object = "test_fix.txt"
        
        with SwiftService(options=config) as swift:
            # 创建容器
            try:
                for result in swift.post(container=test_container):
                    if not result['success']:
                        print(f"         ❌ 容器创建失败: {result.get('error', 'Unknown')}")
                        return
            except:
                pass  # 容器可能已存在
            
            # 上传测试文件
            upload_obj = SwiftUploadObject(test_content, object_name=test_object)
            for result in swift.upload(container=test_container, objects=[upload_obj]):
                if result['success']:
                    print(f"         ✅ 上传成功")
                else:
                    print(f"         ❌ 上传失败: {result.get('error', 'Unknown')}")
                    return
            
            # 下载测试文件
            for result in swift.download(container=test_container, objects=[test_object]):
                if result['success']:
                    downloaded_content = result['contents']
                    if downloaded_content == test_content:
                        print(f"         ✅ 下载验证成功")
                        
                        # 清理测试文件
                        for del_result in swift.delete(container=test_container, objects=[test_object]):
                            pass  # 忽略删除错误
                        
                        return True
                    else:
                        print(f"         ❌ 下载内容不匹配")
                else:
                    print(f"         ❌ 下载失败: {result.get('error', 'Unknown')}")
                    return False
                    
    except Exception as e:
        print(f"         ❌ 测试异常: {str(e)[:50]}")
        return False
    
    return False

def find_working_swift_config():
    """找到可用的Swift配置"""
    from cloud_storage import settings
    
    print("🎯 寻找可用的Swift配置")
    print("=" * 40)
    
    # 基础配置
    base_config = {
        'auth_version': '3',
        'username': 'admin',
        'password': 'devstack123',
        'project_name': 'admin',
        'project_domain_id': 'default',
        'user_domain_id': 'default',
        'region_name': 'RegionOne',
    }
    
    auth_urls = [
        'http://192.168.219.143/identity',
        'http://192.168.219.143:5000/v3',
    ]
    
    object_storage_urls = [
        'http://192.168.219.143:8080/v1',
        'http://192.168.219.143:8888/v1',
        'http://192.168.219.143:80/v1',
    ]
    
    working_configs = []
    
    for auth_url in auth_urls:
        for obj_url in object_storage_urls:
            print(f"\n🔍 测试: {auth_url} + {obj_url}")
            
            config = base_config.copy()
            config['auth_url'] = auth_url
            config['object_storage_url'] = obj_url
            
            if test_swift_upload_download(config, obj_url):
                working_configs.append({
                    'auth_url': auth_url,
                    'object_storage_url': obj_url,
                    'config': config
                })
                print(f"   🎉 找到可用配置!")
    
    if working_configs:
        print(f"\n🎉 找到 {len(working_configs)} 个可用配置:")
        for i, wc in enumerate(working_configs, 1):
            print(f"{i}. 认证: {wc['auth_url']}")
            print(f"   对象存储: {wc['object_storage_url']}")
            
            # 生成更新后的配置
            print(f"\n📝 建议的settings.py配置:")
            print(f"SWIFT_CONFIG = {{")
            print(f"    'auth_version': '3',")
            print(f"    'auth_url': '{wc['auth_url']}',")
            print(f"    'username': 'admin',")
            print(f"    'password': 'devstack123',")
            print(f"    'project_name': 'admin',")
            print(f"    'project_domain_id': 'default',")
            print(f"    'user_domain_id': 'default',")
            print(f"    'region_name': 'RegionOne',")
            print(f"    'object_storage_url': '{wc['object_storage_url']}',")
            print(f"}}")
            
    else:
        print(f"\n❌ 未找到可用的Swift配置")
        print("\n💡 可能的解决方案:")
        print("1. 检查OpenStack服务状态")
        print("2. 重启Swift代理服务")
        print("3. 检查防火墙设置")
        print("4. 验证Swift配置文件")

if __name__ == "__main__":
    print("🚀 Swift服务修复工具")
    print("=" * 50)
    
    # 1. 测试端口
    test_swift_ports()
    
    # 2. 测试不同配置
    test_swift_with_different_configs()
    
    # 3. 寻找可用配置
    find_working_swift_config()
    
    print("\n🎯 修复建议")
    print("=" * 50)
    print("1. 如果找到可用配置，请更新settings.py中的SWIFT_CONFIG")
    print("2. 如果没有找到可用配置，需要修复Swift服务")
    print("3. 重启Django服务以应用新配置")
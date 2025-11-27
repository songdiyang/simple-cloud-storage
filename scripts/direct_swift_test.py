#!/usr/bin/env python
"""
直接测试Swift连接
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

import swiftclient
from swiftclient import Connection

def test_direct_swift_connection():
    """直接测试Swift连接"""
    
    print("🚀 直接Swift连接测试")
    print("=" * 50)
    
    # 测试不同的认证URL
    auth_urls = [
        'http://192.168.219.143/identity/v3',
        'http://192.168.219.143:5000/v3',
        'http://192.168.219.143/identity',
    ]
    
    for auth_url in auth_urls:
        print(f"\n🔍 测试认证URL: {auth_url}")
        
        try:
            # 创建连接
            conn = Connection(
                authurl=auth_url,
                user='admin',
                key='devstack123',
                tenant_name='admin',
                auth_version='3',
                os_options={
                    'project_domain_id': 'default',
                    'user_domain_id': 'default',
                }
            )
            
            # 测试连接
            print("   🔄 测试连接...")
            
            # 获取账户信息
            account_info = conn.get_account()
            print("   ✅ 连接成功!")
            print(f"   📊 容器数: {account_info[0].get('x-account-container-count', 'N/A')}")
            print(f"   📊 对象数: {account_info[0].get('x-account-object-count', 'N/A')}")
            print(f"   📊 字节数: {account_info[0].get('x-account-bytes-used', 'N/A')}")
            
            # 获取存储URL
            storage_url = account_info[0].get('x-storage-url')
            if storage_url:
                print(f"   🎯 存储URL: {storage_url}")
                
                # 测试容器操作
                test_container_operations(conn, storage_url)
                
                return {
                    'auth_url': auth_url,
                    'storage_url': storage_url,
                    'connection': conn
                }
            
        except Exception as e:
            print(f"   ❌ 连接失败: {str(e)[:100]}")
    
    return None

def test_container_operations(conn, storage_url):
    """测试容器操作"""
    print("\n   🔄 测试容器操作...")
    
    test_container = "direct_test_container"
    
    try:
        # 创建容器
        conn.put_container(test_container)
        print(f"      ✅ 容器创建成功: {test_container}")
        
        # 上传测试文件
        test_content = b"Direct Swift test content - " + str(os.urandom(16)).encode()
        conn.put_object(test_container, "test.txt", contents=test_content)
        print(f"      ✅ 文件上传成功")
        
        # 下载测试文件
        downloaded_content = conn.get_object(test_container, "test.txt")[1]
        if downloaded_content == test_content:
            print(f"      ✅ 文件下载验证成功")
        else:
            print(f"      ❌ 文件下载内容不匹配")
        
        # 删除测试文件
        conn.delete_object(test_container, "test.txt")
        print(f"      ✅ 文件删除成功")
        
        # 删除容器
        conn.delete_container(test_container)
        print(f"      ✅ 容器删除成功")
        
        print(f"      🎉 Swift操作全部成功!")
        return True
        
    except Exception as e:
        print(f"      ❌ 容器操作失败: {str(e)[:100]}")
        return False

def update_settings_with_working_config(auth_url, storage_url):
    """更新settings.py配置"""
    print(f"\n📝 更新settings.py配置")
    print("=" * 50)
    
    settings_content = f"""# OpenStack Swift settings
SWIFT_CONFIG = {{
    'auth_version': '3',
    'auth_url': '{auth_url}',
    'username': 'admin',
    'password': 'devstack123',
    'project_name': 'admin',
    'project_domain_id': 'default',
    'user_domain_id': 'default',
    'region_name': 'RegionOne',
    'object_storage_url': '{storage_url}',
    'cacert': None,
}}

# Local file storage settings (fallback for Swift)
LOCAL_STORAGE_ENABLED = False
LOCAL_STORAGE_PATH = os.path.join(BASE_DIR, 'local_storage')
"""
    
    print("请将以下配置复制到 cloud_storage/settings.py:")
    print(settings_content)
    
    # 尝试自动更新settings.py
    settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cloud_storage', 'settings.py')
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到SWIFT_CONFIG部分并替换
        import re
        pattern = r'# OpenStack Swift settings.*?SWIFT_CONFIG = \{[^}]*\}'
        new_content = re.sub(pattern, settings_content.strip(), content, flags=re.DOTALL)
        
        if new_content != content:
            with open(settings_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ 自动更新settings.py成功!")
        else:
            print(f"⚠️  无法自动更新，请手动复制配置")
            
    except Exception as e:
        print(f"❌ 自动更新失败: {str(e)}")
        print(f"请手动复制上述配置到settings.py")

def main():
    result = test_direct_swift_connection()
    
    if result:
        print(f"\n🎉 Swift连接测试成功!")
        update_settings_with_working_config(result['auth_url'], result['storage_url'])
        
        print(f"\n🎯 下一步:")
        print("1. 重启Django服务")
        print("2. 测试上传下载功能")
        
    else:
        print(f"\n❌ 所有Swift连接测试失败")
        print(f"\n💡 可能的解决方案:")
        print("1. 检查OpenStack服务状态")
        print("2. 重启Swift服务:")
        print("   sudo systemctl restart swift-*")
        print("3. 检查Swift配置文件:")
        print("   /etc/swift/proxy-server.conf")
        print("4. 检查防火墙设置")

if __name__ == "__main__":
    main()
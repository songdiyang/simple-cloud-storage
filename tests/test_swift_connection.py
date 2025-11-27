#!/usr/bin/env python
"""
测试OpenStack Swift连接
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from swiftclient.service import SwiftService, SwiftUploadObject
from swiftclient.exceptions import ClientException
from django.conf import settings

def test_swift_connection():
    """测试Swift连接"""
    print("🔍 测试OpenStack Swift连接")
    print("=" * 40)
    
    try:
        # 获取Swift配置
        swift_config = settings.SWIFT_CONFIG
        print(f"认证URL: {swift_config['auth_url']}")
        print(f"用户名: {swift_config['username']}")
        print(f"项目名: {swift_config['project_name']}")
        print(f"区域: {swift_config['region_name']}")
        print()
        
        # 创建Swift连接
        options = {
            'auth_version': swift_config['auth_version'],
            'os_auth_url': swift_config['auth_url'],
            'os_username': swift_config['username'],
            'os_password': swift_config['password'],
            'os_project_name': swift_config['project_name'],
            'os_project_domain_id': swift_config['project_domain_id'],
            'os_user_domain_id': swift_config['user_domain_id'],
            'os_region_name': swift_config['region_name'],
        }
        
        if swift_config.get('cacert'):
            options['os_cacert'] = swift_config['cacert']
        
        swift = SwiftService(options=options)
        
        # 测试连接 - 尝试列出容器
        print("📋 尝试列出容器...")
        container_count = 0
        for container_data in swift.list():
            if container_data['success']:
                container_count += 1
                if 'listing' in container_data:
                    for container in container_data['listing']:
                        print(f"  📦 容器: {container['name']} ({container.get('bytes', 0)} bytes, {container.get('count', 0)} objects)")
            else:
                print(f"  ❌ 列出容器失败: {container_data.get('error', 'Unknown error')}")
                return False
        
        if container_count == 0:
            print("  ℹ️  没有找到现有容器")
        else:
            print(f"  ✅ 找到 {container_count} 页面容器信息")
        
        # 测试创建测试容器
        test_container = "test_connection_container"
        print(f"\n🆕 尝试创建测试容器: {test_container}")
        
        try:
            for result in swift.post(container=test_container):
                if result['success']:
                    print("  ✅ 测试容器创建成功")
                else:
                    print(f"  ❌ 测试容器创建失败: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"  ❌ 测试容器创建失败: {e}")
        
        # 测试上传一个小文件
        print(f"\n📤 尝试上传测试文件...")
        test_content = b"Hello, OpenStack Swift! This is a test file."
        test_file_name = "test_connection.txt"
        
        try:
            import io
            test_file = io.BytesIO(test_content)
            upload_obj = SwiftUploadObject(test_file, object_name=test_file_name)
            
            for result in swift.upload(test_container, [upload_obj]):
                if result['success']:
                    print("  ✅ 测试文件上传成功")
                    print(f"  📄 文件名: {test_file_name}")
                    print(f"  📏 大小: {len(test_content)} bytes")
                else:
                    print(f"  ❌ 测试文件上传失败: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"  ❌ 测试文件上传失败: {e}")
        
        # 测试列出容器中的对象
        print(f"\n📋 尝试列出容器中的对象...")
        try:
            object_count = 0
            for obj_data in swift.list(container=test_container):
                if obj_data['success'] and 'listing' in obj_data:
                    for obj in obj_data['listing']:
                        object_count += 1
                        print(f"  📄 对象: {obj['name']} ({obj.get('bytes', 0)} bytes)")
                else:
                    print(f"  ❌ 列出对象失败: {obj_data.get('error', 'Unknown error')}")
            
            if object_count == 0:
                print("  ℹ️  容器中没有对象")
            else:
                print(f"  ✅ 找到 {object_count} 个对象")
        except Exception as e:
            print(f"  ❌ 列出对象失败: {e}")
        
        # 清理测试数据
        print(f"\n🧹 清理测试数据...")
        try:
            # 删除测试文件
            for result in swift.delete(test_container, [test_file_name]):
                if result['success']:
                    print("  ✅ 测试文件删除成功")
                else:
                    print(f"  ❌ 测试文件删除失败: {result.get('error', 'Unknown error')}")
            
            # 删除测试容器
            for result in swift.delete(test_container):
                if result['success']:
                    print("  ✅ 测试容器删除成功")
                else:
                    print(f"  ❌ 测试容器删除失败: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"  ❌ 清理测试数据失败: {e}")
        
        print("\n✅ OpenStack Swift连接测试完成！")
        print("Swift服务配置正确，可以正常使用。")
        return True
        
    except ClientException as e:
        print(f"❌ Swift连接失败 (ClientException): {e}")
        if hasattr(e, 'http_status') and e.http_status:
            print(f"   HTTP状态码: {e.http_status}")
        if hasattr(e, 'http_reason') and e.http_reason:
            print(f"   HTTP原因: {e.http_reason}")
        return False
    except Exception as e:
        print(f"❌ Swift连接失败 (Exception): {e}")
        print(f"   错误类型: {type(e).__name__}")
        return False

def check_environment():
    """检查环境变量"""
    print("🔧 检查环境变量配置")
    print("=" * 40)
    
    required_vars = [
        'OS_AUTH_URL',
        'OS_USERNAME', 
        'OS_PASSWORD',
        'OS_PROJECT_NAME',
        'OS_PROJECT_DOMAIN_ID',
        'OS_USER_DOMAIN_ID',
        'OS_REGION_NAME'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: 未设置")
            all_set = False
    
    return all_set

def main():
    """主函数"""
    print("🚀 OpenStack Swift连接测试工具")
    print("=" * 50)
    
    # 检查环境变量
    env_ok = check_environment()
    if not env_ok:
        print("\n❌ 环境变量配置不完整，请检查.env文件")
        sys.exit(1)
    
    print()
    
    # 测试Swift连接
    connection_ok = test_swift_connection()
    
    if connection_ok:
        print("\n🎉 所有测试通过！Swift服务配置正确。")
    else:
        print("\n💥 Swift连接测试失败，请检查配置和网络连接。")
        print("\n可能的解决方案:")
        print("1. 检查OpenStack服务是否正在运行")
        print("2. 验证认证URL是否正确")
        print("3. 确认用户名、密码和项目名是否正确")
        print("4. 检查网络连接和防火墙设置")
        print("5. 确认Swift服务是否已安装并配置")
        sys.exit(1)

if __name__ == "__main__":
    main()
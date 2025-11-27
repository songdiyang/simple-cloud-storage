#!/usr/bin/env python
"""
测试文件上传功能
"""
import os
import sys
import requests
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

def test_upload_apis():
    """测试文件上传功能"""
    base_url = "http://localhost:8000"
    
    print("🧪 测试文件上传功能")
    print("=" * 40)
    
    # 1. 测试登录获取token
    print("1. 测试用户登录...")
    login_data = {"username": "demo", "password": "demo123"}
    
    try:
        response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        if response.status_code == 200:
            token = response.json()['token']
            headers = {'Authorization': f'Token {token}'}
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("请确保后端服务正在运行在 http://localhost:8000")
        return
    
    # 2. 检查用户存储信息
    print("\n2. 检查用户存储信息...")
    try:
        response = requests.get(f"{base_url}/api/auth/profile/", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ 用户存储信息:")
            print(f"   存储配额: {user_data.get('storage_quota_display')}")
            print(f"   已使用: {user_data.get('used_storage_display')}")
            print(f"   可用空间: {user_data.get('available_storage_display')}")
        else:
            print(f"❌ 获取存储信息失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 3. 创建测试文件
    print("\n3. 创建测试文件...")
    test_file_path = "test_upload.txt"
    test_content = "这是一个测试文件内容\n" * 100  # 约2KB
    
    try:
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print(f"✅ 测试文件创建成功: {test_file_path}")
        print(f"   文件大小: {os.path.getsize(test_file_path)} 字节")
    except Exception as e:
        print(f"❌ 创建测试文件失败: {e}")
        return
    
    # 4. 测试文件上传
    print("\n4. 测试文件上传...")
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'folder_id': None}  # 上传到根目录
            response = requests.post(
                f"{base_url}/api/files/upload/", 
                headers=headers, 
                files=files,
                data=data
            )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ 文件上传成功")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 文件上传失败")
            print(f"   错误信息: {response.text}")
            
            # 分析常见错误
            error_text = response.text.lower()
            if "swift" in error_text:
                print("   💡 可能是Swift存储配置问题")
            elif "storage" in error_text:
                print("   💡 可能是存储空间不足")
            elif "permission" in error_text:
                print("   💡 可能是权限问题")
            elif "network" in error_text or "connection" in error_text:
                print("   💡 可能是网络连接问题")
                
    except Exception as e:
        print(f"❌ 上传请求失败: {e}")
    
    # 5. 测试获取文件列表
    print("\n5. 测试获取文件列表...")
    try:
        response = requests.get(f"{base_url}/api/files/", headers=headers)
        if response.status_code == 200:
            files_data = response.json()
            print(f"✅ 文件列表获取成功")
            print(f"   文件数量: {len(files_data.get('results', files_data))}")
            for file_item in files_data.get('results', files_data)[:3]:  # 显示前3个文件
                print(f"   - {file_item.get('name')} ({file_item.get('size_display', 'N/A')})")
        else:
            print(f"❌ 获取文件列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 6. 检查Swift连接状态
    print("\n6. 检查Swift配置...")
    try:
        # 导入Django设置
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
        import django
        django.setup()
        
        from django.conf import settings
        swift_config = getattr(settings, 'SWIFT_CONFIG', {})
        
        print("   Swift配置:")
        for key, value in swift_config.items():
            if 'password' in key.lower():
                print(f"   {key}: {'*' * len(str(value))}")
            else:
                print(f"   {key}: {value}")
                
        # 尝试连接Swift
        try:
            from files.utils import get_swift_connection
            swift = get_swift_connection()
            print("   ✅ Swift连接对象创建成功")
            
            # 尝试列出容器
            for _ in swift.list():
                break
            print("   ✅ Swift连接测试成功")
            
        except Exception as swift_error:
            print(f"   ❌ Swift连接失败: {swift_error}")
            
    except Exception as e:
        print(f"   ❌ 检查Swift配置失败: {e}")
    
    # 清理测试文件
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print("\n🧹 清理测试文件完成")
    
    print("\n🎉 文件上传测试完成！")
    print("\n💡 如果上传失败，请检查:")
    print("   1. Swift存储服务是否正常运行")
    print("   2. Swift配置是否正确")
    print("   3. 网络连接是否正常")
    print("   4. 用户存储空间是否足够")

if __name__ == "__main__":
    test_upload_apis()
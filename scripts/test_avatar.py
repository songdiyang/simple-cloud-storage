#!/usr/bin/env python
"""
测试头像上传功能
"""
import os
import sys
import requests
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

def test_avatar_apis():
    """测试头像相关API"""
    base_url = "http://localhost:8000"
    
    print("🧪 测试头像API功能")
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
            return
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("请确保后端服务正在运行在 http://localhost:8000")
        return
    
    # 2. 测试获取用户信息
    print("\n2. 测试获取用户信息...")
    try:
        response = requests.get(f"{base_url}/api/auth/profile/", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ 用户信息获取成功")
            print(f"   用户名: {user_data.get('username')}")
            print(f"   头像: {user_data.get('avatar') or '无'}")
        else:
            print(f"❌ 获取用户信息失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 3. 测试头像上传API（需要真实文件）
    print("\n3. 测试头像上传API...")
    
    # 创建一个测试图片文件
    test_image_path = "test_avatar.png"
    if not os.path.exists(test_image_path):
        print("📝 创建测试图片文件...")
        # 创建一个简单的PNG图片（1x1像素的透明PNG）
        import base64
        png_data = base64.b64decode("""
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==
""")
        with open(test_image_path, 'wb') as f:
            f.write(png_data)
        print("✅ 测试图片创建成功")
    
    try:
        with open(test_image_path, 'rb') as f:
            files = {'avatar': f}
            response = requests.post(
                f"{base_url}/api/auth/upload-avatar/", 
                headers=headers, 
                files=files
            )
        
        if response.status_code == 200:
            print("✅ 头像上传成功")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 头像上传失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"❌ 上传失败: {e}")
    
    # 4. 测试删除头像API
    print("\n4. 测试删除头像API...")
    try:
        response = requests.delete(f"{base_url}/api/auth/delete-avatar/", headers=headers)
        if response.status_code == 200:
            print("✅ 头像删除成功")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 头像删除失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"❌ 删除失败: {e}")
    
    # 清理测试文件
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
        print("\n🧹 清理测试文件完成")
    
    print("\n🎉 头像API测试完成！")

if __name__ == "__main__":
    test_avatar_apis()
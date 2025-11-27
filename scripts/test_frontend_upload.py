#!/usr/bin/env python
"""
测试前端文件上传修复
"""
import os
import sys
import requests
import json
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

def test_upload_fix():
    """测试文件上传修复"""
    base_url = "http://localhost:8000"
    
    print("🧪 测试前端文件上传修复")
    print("=" * 40)
    
    # 1. 登录获取token
    print("1. 用户登录...")
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
        return
    
    # 2. 创建测试文件
    print("\n2. 创建测试文件...")
    test_file_path = "frontend_test.txt"
    test_content = "前端上传测试文件\n" * 30  # 约1.2KB
    
    try:
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        file_size = os.path.getsize(test_file_path)
        print(f"✅ 测试文件创建成功: {file_size} 字节")
    except Exception as e:
        print(f"❌ 创建测试文件失败: {e}")
        return
    
    # 3. 测试正确的文件上传（模拟前端修复后的行为）
    print("\n3. 测试修复后的文件上传...")
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            # 不设置Content-Type，让requests自动设置multipart/form-data
            response = requests.post(
                f"{base_url}/api/files/upload/", 
                headers=headers, 
                files=files
            )
        
        print(f"   状态码: {response.status_code}")
        print(f"   响应头: {dict(response.headers)}")
        
        if response.status_code == 201:
            upload_data = response.json()
            print("✅ 文件上传成功")
            print(f"   文件ID: {upload_data.get('id')}")
            print(f"   文件名: {upload_data.get('name')}")
            print(f"   文件大小: {upload_data.get('size')}")
            print(f"   MIME类型: {upload_data.get('mime_type')}")
            
            # 测试删除刚上传的文件
            file_id = upload_data.get('id')
            if file_id:
                print(f"\n4. 测试删除文件 {file_id}...")
                delete_response = requests.delete(
                    f"{base_url}/api/files/{file_id}/delete/",
                    headers=headers
                )
                if delete_response.status_code == 200:
                    print("✅ 文件删除成功")
                else:
                    print(f"❌ 文件删除失败: {delete_response.status_code}")
                    print(f"   错误信息: {delete_response.text}")
        else:
            print(f"❌ 文件上传失败")
            print(f"   响应内容: {response.text}")
            
            # 分析错误
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"   错误详情: {error_data['error']}")
            except:
                pass
            
    except Exception as e:
        print(f"❌ 上传请求失败: {e}")
    
    # 4. 测试头像上传
    print("\n5. 测试头像上传...")
    try:
        # 创建一个简单的PNG图片
        import base64
        png_data = base64.b64decode("""
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==
""")
        avatar_path = "test_avatar.png"
        with open(avatar_path, 'wb') as f:
            f.write(png_data)
        
        with open(avatar_path, 'rb') as f:
            files = {'avatar': f}
            response = requests.post(
                f"{base_url}/api/auth/upload-avatar/", 
                headers=headers, 
                files=files
            )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 头像上传成功")
            avatar_data = response.json()
            print(f"   消息: {avatar_data.get('message')}")
        else:
            print(f"❌ 头像上传失败")
            print(f"   响应内容: {response.text}")
        
        # 清理头像文件
        os.remove(avatar_path)
        
    except Exception as e:
        print(f"❌ 头像上传测试失败: {e}")
    
    # 清理测试文件
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print("\n🧹 清理测试文件完成")
    
    print("\n🎉 前端上传修复测试完成！")
    
    print("\n💡 修复要点:")
    print("   1. 前端上传时移除Content-Type头")
    print("   2. 后端添加@parser_classes([MultiPartParser, FormParser])")
    print("   3. 让浏览器自动设置multipart/form-data")
    
    print("\n📋 测试结果:")
    print("   - 如果所有测试通过，说明上传功能已修复")
    print("   - 可以打开 frontend/test_upload.html 进行浏览器测试")

if __name__ == "__main__":
    test_upload_fix()
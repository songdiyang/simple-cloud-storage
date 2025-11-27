#!/usr/bin/env python
"""
测试文件上传和删除功能
"""
import os
import sys
import requests
import time
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

def get_auth_headers(base_url="http://localhost:8000"):
    """获取认证头"""
    login_data = {"username": "demo", "password": "demo123"}
    response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
    if response.status_code == 200:
        token = response.json()['token']
        return {'Authorization': f'Token {token}'}
    else:
        raise Exception("登录失败")

def test_file_operations():
    """测试完整的文件操作流程"""
    base_url = "http://localhost:8000"
    
    print("🧪 测试文件上传和删除功能")
    print("=" * 50)
    
    try:
        headers = get_auth_headers(base_url)
        print("✅ 用户认证成功")
    except Exception as e:
        print(f"❌ 认证失败: {e}")
        return
    
    # 1. 创建测试文件
    print("\n1. 创建测试文件...")
    test_file_path = "test_operations.txt"
    test_content = "测试文件内容\n" * 50  # 约1.5KB
    
    try:
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        file_size = os.path.getsize(test_file_path)
        print(f"✅ 测试文件创建成功: {file_size} 字节")
    except Exception as e:
        print(f"❌ 创建测试文件失败: {e}")
        return
    
    uploaded_file_id = None
    
    # 2. 测试文件上传
    print("\n2. 测试文件上传...")
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'folder_id': None}
            response = requests.post(
                f"{base_url}/api/files/upload/", 
                headers=headers, 
                files=files,
                data=data
            )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 201:
            upload_data = response.json()
            uploaded_file_id = upload_data.get('id')
            print(f"✅ 文件上传成功")
            print(f"   文件ID: {uploaded_file_id}")
            print(f"   文件名: {upload_data.get('name')}")
            print(f"   文件大小: {upload_data.get('size_display')}")
            print(f"   Swift容器: {upload_data.get('swift_container')}")
            print(f"   Swift对象: {upload_data.get('swift_object')}")
        else:
            print(f"❌ 文件上传失败")
            print(f"   错误信息: {response.text}")
            return
    except Exception as e:
        print(f"❌ 上传请求失败: {e}")
        return
    
    # 3. 等待一秒确保文件完全上传
    time.sleep(1)
    
    # 4. 验证文件列表中包含上传的文件
    print("\n3. 验证文件列表...")
    try:
        response = requests.get(f"{base_url}/api/files/", headers=headers)
        if response.status_code == 200:
            files_data = response.json()
            files_list = files_data.get('results', files_data)
            
            found_file = None
            for file_item in files_list:
                if file_item.get('id') == uploaded_file_id:
                    found_file = file_item
                    break
            
            if found_file:
                print(f"✅ 文件在列表中找到")
                print(f"   文件名: {found_file.get('name')}")
                print(f"   大小: {found_file.get('size_display')}")
            else:
                print(f"❌ 文件未在列表中找到")
                return
        else:
            print(f"❌ 获取文件列表失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 获取文件列表失败: {e}")
        return
    
    # 5. 测试文件删除
    print("\n4. 测试文件删除...")
    if uploaded_file_id:
        try:
            delete_url = f"{base_url}/api/files/{uploaded_file_id}/delete/"
            response = requests.delete(delete_url, headers=headers)
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ 文件删除成功")
                print(f"   响应: {response.json()}")
            else:
                print(f"❌ 文件删除失败")
                print(f"   错误信息: {response.text}")
                
                # 分析错误
                error_text = response.text.lower()
                if "404" in error_text:
                    print("   💡 可能原因: Swift中对象不存在")
                elif "403" in error_text:
                    print("   💡 可能原因: 权限不足")
                elif "500" in error_text:
                    print("   💡 可能原因: 服务器内部错误")
        except Exception as e:
            print(f"❌ 删除请求失败: {e}")
    
    # 6. 再次验证文件列表
    print("\n5. 验证文件已删除...")
    try:
        response = requests.get(f"{base_url}/api/files/", headers=headers)
        if response.status_code == 200:
            files_data = response.json()
            files_list = files_data.get('results', files_data)
            
            found_file = None
            for file_item in files_list:
                if file_item.get('id') == uploaded_file_id:
                    found_file = file_item
                    break
            
            if not found_file:
                print(f"✅ 文件已从列表中移除")
            else:
                print(f"❌ 文件仍在列表中，删除可能失败")
        else:
            print(f"❌ 获取文件列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取文件列表失败: {e}")
    
    # 7. 检查用户存储空间变化
    print("\n6. 检查用户存储空间...")
    try:
        response = requests.get(f"{base_url}/api/auth/profile/", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ 当前存储状态:")
            print(f"   存储配额: {user_data.get('storage_quota_display')}")
            print(f"   已使用: {user_data.get('used_storage_display')}")
            print(f"   可用空间: {user_data.get('available_storage_display')}")
    except Exception as e:
        print(f"❌ 获取存储信息失败: {e}")
    
    # 清理测试文件
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print("\n🧹 清理测试文件完成")
    
    print("\n🎉 文件操作测试完成！")
    
    # 提供修复建议
    print("\n💡 如果删除失败，可能的原因:")
    print("   1. Swift容器或对象不存在")
    print("   2. Swift权限配置问题")
    print("   3. 网络连接问题")
    print("   4. 文件路径编码问题")
    
    print("\n🔧 修复建议:")
    print("   1. 检查Swift服务状态")
    print("   2. 验证容器权限")
    print("   3. 考虑使用本地存储备选方案")

if __name__ == "__main__":
    test_file_operations()
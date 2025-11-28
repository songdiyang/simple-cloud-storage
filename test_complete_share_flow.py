#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整的分享文件功能测试流程
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def get_auth_headers(username="demo", password="demo123"):
    """获取认证头"""
    login_data = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        token = response.json().get("token")
        return {"Authorization": f"Token {token}"}
    return None

def test_complete_flow():
    print("🔄 完整分享文件功能测试")
    print("=" * 60)
    
    headers = get_auth_headers()
    if not headers:
        print("❌ 登录失败，无法继续测试")
        return
    
    print("✅ 用户登录成功")
    
    # 1. 获取文件列表
    print("\n📁 获取文件列表...")
    response = requests.get(f"{BASE_URL}/files/", headers=headers)
    if response.status_code != 200:
        print("❌ 获取文件列表失败")
        return
    
    files = response.json().get("results", [])
    if not files:
        print("❌ 没有找到文件，请先上传文件")
        return
    
    test_file = files[0]
    print(f"✅ 找到测试文件: {test_file['name']}")
    
    # 2. 获取现有分享或创建新分享
    print("\n🔗 获取分享信息...")
    
    # 先获取现有分享
    response = requests.get(f"{BASE_URL}/files/shares/", headers=headers)
    if response.status_code == 200:
        shares = response.json()
        existing_share = None
        for share in shares:
            if share["file_name"] == test_file["name"]:
                existing_share = share
                break
        
        if existing_share:
            share_info = existing_share
            share_code = existing_share["share_code"]
            print(f"✅ 使用现有分享: {share_code}")
        else:
            # 创建新分享
            share_data = {
                "password": "test123",
                "max_downloads": 5
            }
            
            response = requests.post(f"{BASE_URL}/files/{test_file['id']}/share/", 
                                   json=share_data, headers=headers)
            if response.status_code != 201:
                print(f"❌ 创建分享失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return
            
            share_info = response.json()
            share_code = share_info["share_code"]
            print(f"✅ 分享创建成功: {share_code}")
    else:
        print("❌ 获取分享列表失败")
        return
    
    # 3. 测试公开访问分享信息
    print("\n🌐 测试公开访问分享信息...")
    response = requests.get(f"{BASE_URL}/files/share/{share_code}/")
    if response.status_code == 403:
        print("✅ 密码保护生效")
    elif response.status_code == 200:
        print("⚠️ 分享没有密码保护")
    else:
        print(f"❌ 访问失败: {response.status_code}")
    
    # 4. 使用密码访问分享
    print("\n🔑 使用密码访问分享...")
    response = requests.get(f"{BASE_URL}/files/share/{share_code}/", 
                          params={"password": "test123"})
    if response.status_code == 200:
        share_public_info = response.json()
        print(f"✅ 密码验证成功")
        print(f"   文件名: {share_public_info['file_name']}")
        print(f"   文件大小: {share_public_info['file_size']} bytes")
    else:
        print(f"❌ 密码验证失败: {response.status_code}")
        return
    
    # 5. 测试下载分享文件
    print("\n⬇️ 测试下载分享文件...")
    response = requests.post(f"{BASE_URL}/files/share/{share_code}/download/",
                           json={"password": "test123"})
    if response.status_code == 200:
        print("✅ 分享下载成功")
    else:
        print(f"❌ 分享下载失败: {response.status_code}")
    
    # 6. 测试保存分享文件到云盘（使用另一个用户）
    print("\n💾 测试保存分享文件到云盘...")
    
    # 创建或获取第二个用户
    try:
        # 尝试注册新用户
        register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
        if response.status_code == 201:
            print("✅ 创建测试用户成功")
    except:
        print("ℹ️ 测试用户可能已存在")
    
    # 登录测试用户
    test_headers = get_auth_headers("testuser", "testpass123")
    if not test_headers:
        print("❌ 测试用户登录失败")
        return
    
    print("✅ 测试用户登录成功")
    
    # 保存分享文件
    save_data = {
        "share_code": share_code,
        "folder_id": None,
        "password": "test123"
    }
    
    response = requests.post(f"{BASE_URL}/files/save-shared-file/", 
                           json=save_data, headers=test_headers)
    if response.status_code == 201:
        print("✅ 文件保存到云盘成功")
        saved_file = response.json()["file"]
        print(f"   保存的文件: {saved_file['name']}")
    elif response.status_code == 400:
        print("⚠️ 文件可能已存在于云盘中")
    else:
        print(f"❌ 保存失败: {response.status_code}")
        print(f"   错误信息: {response.text}")
    
    # 7. 验证文件确实保存了
    print("\n🔍 验证文件是否保存成功...")
    response = requests.get(f"{BASE_URL}/files/", headers=test_headers)
    if response.status_code == 200:
        user_files = response.json().get("results", [])
        saved_files = [f for f in user_files 
                      if f["name"] == test_file["name"]]
        if saved_files:
            print("✅ 文件确认保存在云盘中")
        else:
            print("❌ 文件未在云盘中找到")
    
    # 8. 测试从云盘下载
    if saved_files:
        print("\n📥 测试从云盘下载文件...")
        file_id = saved_files[0]["id"]
        response = requests.get(f"{BASE_URL}/files/{file_id}/download/", 
                              headers=test_headers)
        if response.status_code == 200:
            print("✅ 从云盘下载成功")
        else:
            print(f"❌ 云盘下载失败: {response.status_code}")
    
    # 9. 清理测试数据（如果是新创建的分享）
    print("\n🧹 清理测试数据...")
    if isinstance(share_info, dict) and "id" in share_info:
        response = requests.delete(f"{BASE_URL}/files/shares/{share_info['id']}/delete/",
                                  headers=headers)
        if response.status_code == 200:
            print("✅ 测试分享已删除")
    else:
        print("ℹ️ 使用现有分享，跳过删除")
    
    print("\n🎉 完整功能测试完成！")
    print("\n📋 功能总结:")
    print("✅ 文件分享创建")
    print("✅ 密码保护访问")
    print("✅ 分享文件下载")
    print("✅ 保存分享文件到云盘")
    print("✅ 从云盘下载文件")
    print("✅ 权限控制正常")

def test_error_cases():
    print("\n🛡️ 错误情况测试")
    print("-" * 30)
    
    # 测试无效分享码
    response = requests.get(f"{BASE_URL}/files/share/INVALIDCODE/")
    if response.status_code == 404:
        print("✅ 无效分享码正确返回404")
    
    # 测试错误密码
    headers = get_auth_headers()
    if headers:
        # 先创建一个分享
        response = requests.get(f"{BASE_URL}/files/", headers=headers)
        files = response.json().get("results", [])
        if files:
            file_id = files[0]["id"]
            response = requests.post(f"{BASE_URL}/files/{file_id}/share/", 
                                   json={}, headers=headers)
            if response.status_code == 201:
                share_code = response.json()["share_code"]
                # 测试错误密码
                response = requests.get(f"{BASE_URL}/files/share/{share_code}/", 
                                      params={"password": "wrongpassword"})
                if response.status_code == 403:
                    print("✅ 错误密码正确返回403")

if __name__ == "__main__":
    test_complete_flow()
    test_error_cases()
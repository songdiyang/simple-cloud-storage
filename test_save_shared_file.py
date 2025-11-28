#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试保存分享文件到云盘功能
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_save_shared_file():
    print("🚀 测试保存分享文件到云盘功能")
    print("=" * 50)
    
    # 1. 登录获取token
    print("🔑 登录用户...")
    login_data = {
        "username": "demo",
        "password": "demo123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        return
    
    token = response.json().get("token")
    headers = {"Authorization": f"Token {token}"}
    print("✅ 登录成功")
    
    # 2. 获取用户的分享列表
    print("\n📋 获取分享列表...")
    response = requests.get(f"{BASE_URL}/files/shares/", headers=headers)
    if response.status_code != 200:
        print(f"❌ 获取分享列表失败: {response.status_code}")
        return
    
    shares = response.json()
    if not shares:
        print("❌ 没有找到分享，请先创建一个分享")
        return
    
    share = shares[0]  # 使用第一个分享
    share_code = share["share_code"]
    print(f"✅ 找到分享: {share['file_name']} (分享码: {share_code})")
    
    # 3. 测试保存分享文件到云盘
    print(f"\n💾 保存分享文件到云盘...")
    save_data = {
        "share_code": share_code,
        "folder_id": None  # 保存到根目录
    }
    
    response = requests.post(f"{BASE_URL}/files/save-shared-file/", 
                           json=save_data, headers=headers)
    
    if response.status_code == 201:
        result = response.json()
        print("✅ 文件保存成功!")
        print(f"   文件名: {result['file']['name']}")
        print(f"   文件大小: {result['file']['size']} bytes")
        print(f"   保存位置: 根目录")
    elif response.status_code == 400:
        error = response.json().get("error", "未知错误")
        if "已存在" in error:
            print(f"⚠️ 文件已存在于云盘中: {error}")
        else:
            print(f"❌ 保存失败: {error}")
    else:
        print(f"❌ 保存失败: {response.status_code}")
        print(f"   错误信息: {response.text}")
    
    # 4. 验证文件是否真的保存了
    print("\n🔍 验证文件列表...")
    response = requests.get(f"{BASE_URL}/files/", headers=headers)
    if response.status_code == 200:
        files = response.json().get("results", [])
        saved_files = [f for f in files if f["name"] == share["file_name"]]
        if saved_files:
            print("✅ 文件已成功保存到云盘!")
            print(f"   找到 {len(saved_files)} 个同名文件")
        else:
            print("❌ 文件未在云盘中找到")
    
    print("\n🎉 测试完成!")

def test_public_share_access():
    print("\n🌐 测试公开分享访问...")
    print("-" * 30)
    
    # 1. 获取一个分享码（这里需要手动提供一个）
    share_code = input("请输入分享码进行测试 (或按回车跳过): ").strip()
    if not share_code:
        print("跳过公开分享测试")
        return
    
    # 2. 获取分享信息
    response = requests.get(f"{BASE_URL}/files/share/{share_code}/")
    if response.status_code == 200:
        share_info = response.json()
        print("✅ 分享信息获取成功:")
        print(f"   文件名: {share_info['file_name']}")
        print(f"   文件大小: {share_info['file_size']} bytes")
        print(f"   下载次数: {share_info['download_count']}")
    else:
        print(f"❌ 获取分享信息失败: {response.status_code}")

if __name__ == "__main__":
    test_save_shared_file()
    test_public_share_access()
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
云存储系统功能验证脚本
"""

import requests
import json
import time
import os

# API基础URL
BASE_URL = "http://localhost:8000/api"

def print_status(message, status="info"):
    """打印状态信息"""
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    print(f"{icons.get(status, '•')} {message}")

def test_backend_connection():
    """测试后端连接"""
    print_status("测试后端连接...")
    try:
        response = requests.get(f"{BASE_URL}/auth/login/", timeout=5)
        if response.status_code == 200 or response.status_code == 405:
            print_status("后端服务运行正常", "success")
            return True
        else:
            print_status(f"后端服务异常: {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"后端连接失败: {e}", "error")
        return False

def test_frontend_connection():
    """测试前端连接"""
    print_status("测试前端连接...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print_status("前端服务运行正常", "success")
            return True
        else:
            print_status(f"前端服务异常: {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"前端连接失败: {e}", "error")
        return False

def test_login():
    """测试登录功能"""
    print_status("测试用户登录...")
    try:
        login_data = {
            "username": "demo",
            "password": "demo123"
        }
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data:
                print_status("登录功能正常", "success")
                return data["token"]
            else:
                print_status("登录响应格式异常", "error")
                print(f"响应内容: {data}")
                return None
        else:
            print_status(f"登录失败: {response.status_code}", "error")
            print(f"响应内容: {response.text}")
            return None
    except Exception as e:
        print_status(f"登录测试失败: {e}", "error")
        return None

def test_file_operations(token):
    """测试文件操作"""
    print_status("测试文件操作...")
    try:
        headers = {"Authorization": f"Token {token}"}
        
        # 测试文件夹列表
        response = requests.get(f"{BASE_URL}/files/folders/", headers=headers, timeout=5)
        if response.status_code == 200:
            print_status("文件夹列表获取正常", "success")
        else:
            print_status(f"文件夹列表获取失败: {response.status_code}", "error")
            
        # 测试文件列表
        response = requests.get(f"{BASE_URL}/files/", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "results" in data:
                print_status(f"文件列表获取正常，共 {len(data['results'])} 个文件", "success")
            else:
                print_status("文件列表获取正常", "success")
        else:
            print_status(f"文件列表获取失败: {response.status_code}", "error")
            
    except Exception as e:
        print_status(f"文件操作测试失败: {e}", "error")

def test_share_functionality(token):
    """测试分享功能"""
    print_status("测试分享功能...")
    try:
        headers = {"Authorization": f"Token {token}"}
        
        # 获取文件列表
        response = requests.get(f"{BASE_URL}/files/", headers=headers, timeout=5)
        if response.status_code != 200:
            print_status("无法获取文件列表，跳过分享测试", "warning")
            return
            
        files = response.json().get("results", [])
        if not files:
            print_status("没有文件，跳过分享测试", "warning")
            return
            
        # 测试获取分享列表
        response = requests.get(f"{BASE_URL}/files/shares/", headers=headers, timeout=5)
        if response.status_code == 200:
            shares = response.json()
            print_status(f"分享列表获取正常，共 {len(shares)} 个分享", "success")
        else:
            print_status(f"分享列表获取失败: {response.status_code}", "error")
            
    except Exception as e:
        print_status(f"分享功能测试失败: {e}", "error")

def main():
    """主测试函数"""
    print("🚀 云存储系统功能验证")
    print("=" * 50)
    
    # 测试服务连接
    backend_ok = test_backend_connection()
    frontend_ok = test_frontend_connection()
    
    if not backend_ok:
        print_status("后端服务异常，无法继续测试", "error")
        return
        
    if not frontend_ok:
        print_status("前端服务异常，但可以继续测试后端功能", "warning")
    
    print()
    
    # 测试认证功能
    token = test_login()
    if not token:
        print_status("登录失败，无法继续测试", "error")
        return
        
    print()
    
    # 测试文件操作
    test_file_operations(token)
    print()
    
    # 测试分享功能
    test_share_functionality(token)
    print()
    
    print("🎉 功能验证完成！")
    print()
    print("📱 使用说明:")
    print("1. 前端地址: http://localhost:3000")
    print("2. 后端API: http://localhost:8000/api")
    print("3. 登录账号: demo / demo123")
    print("4. 主要功能: 文件管理、分享、上传下载")

if __name__ == "__main__":
    main()
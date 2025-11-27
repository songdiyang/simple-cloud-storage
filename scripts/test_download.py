#!/usr/bin/env python3
"""
测试文件下载功能
"""
import os
import requests
import json
from pathlib import Path

# API基础URL
BASE_URL = "http://localhost:8000/api"

def login():
    """登录获取token"""
    print("🔐 正在登录...")
    login_data = {
        "username": "demo",
        "password": "demo123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    
    if response.status_code == 200:
        token = response.json().get("token")
        print(f"✅ 登录成功！")
        return token
    else:
        print(f"❌ 登录失败: {response.text}")
        return None

def get_file_list(token):
    """获取文件列表"""
    print("📄 获取文件列表...")
    
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(f"{BASE_URL}/files/", headers=headers)
    
    if response.status_code == 200:
        files = response.json().get("results", [])
        print(f"✅ 找到 {len(files)} 个文件")
        return files
    else:
        print(f"❌ 获取文件列表失败: {response.text}")
        return []

def test_download_url(token, file_id, filename):
    """测试获取下载URL"""
    print(f"🔗 获取文件下载URL (ID: {file_id})...")
    
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(f"{BASE_URL}/files/{file_id}/download-url/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        download_url = data.get("download_url")
        print(f"✅ 获取下载URL成功")
        print(f"   文件名: {data.get('filename')}")
        print(f"   大小: {data.get('size')} bytes")
        print(f"   下载URL: {download_url}")
        return download_url
    else:
        print(f"❌ 获取下载URL失败: {response.text}")
        return None

def test_direct_download(token, file_id, filename):
    """测试直接下载"""
    print(f"⬇️  直接下载文件 (ID: {file_id})...")
    
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(f"{BASE_URL}/files/{file_id}/download/", headers=headers)
    
    if response.status_code == 200:
        # 保存下载的文件
        download_dir = Path("downloads")
        download_dir.mkdir(exist_ok=True)
        
        file_path = download_dir / f"downloaded_{filename}"
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ 文件下载成功")
        print(f"   保存路径: {file_path.absolute()}")
        print(f"   文件大小: {len(response.content)} bytes")
        
        # 检查响应头
        content_type = response.headers.get('content-type')
        content_disposition = response.headers.get('content-disposition')
        print(f"   Content-Type: {content_type}")
        print(f"   Content-Disposition: {content_disposition}")
        
        return True
    else:
        print(f"❌ 直接下载失败: {response.text}")
        return False

def test_download_from_url(download_url, filename):
    """从URL下载文件"""
    if not download_url:
        return False
        
    print(f"🌐 从URL下载文件...")
    
    try:
        response = requests.get(download_url)
        
        if response.status_code == 200:
            # 保存下载的文件
            download_dir = Path("downloads")
            download_dir.mkdir(exist_ok=True)
            
            file_path = download_dir / f"url_downloaded_{filename}"
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ URL下载成功")
            print(f"   保存路径: {file_path.absolute()}")
            print(f"   文件大小: {len(response.content)} bytes")
            
            return True
        else:
            print(f"❌ URL下载失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ URL下载异常: {e}")
        return False

def main():
    print("🧪 测试文件下载功能")
    print("=" * 50)
    
    # 1. 登录
    token = login()
    if not token:
        return
    
    # 2. 获取文件列表
    files = get_file_list(token)
    if not files:
        print("❌ 没有找到文件，请先上传一些文件")
        return
    
    # 3. 选择第一个文件进行测试
    test_file = files[0]
    file_id = test_file["id"]
    filename = test_file["original_name"]
    
    print(f"\n📋 选择测试文件:")
    print(f"   ID: {file_id}")
    print(f"   名称: {filename}")
    print(f"   大小: {test_file['size_display']}")
    print(f"   类型: {test_file['file_type']}")
    
    # 4. 测试获取下载URL
    print(f"\n" + "=" * 50)
    download_url = test_download_url(token, file_id, filename)
    
    # 5. 测试从URL下载
    if download_url:
        print(f"\n" + "=" * 50)
        test_download_from_url(download_url, filename)
    
    # 6. 测试直接下载
    print(f"\n" + "=" * 50)
    test_direct_download(token, file_id, filename)
    
    print(f"\n" + "=" * 50)
    print("🎉 下载功能测试完成！")
    
    # 7. 显示下载目录
    download_dir = Path("downloads")
    if download_dir.exists():
        print(f"\n📁 下载目录: {download_dir.absolute()}")
        downloaded_files = list(download_dir.glob("*"))
        if downloaded_files:
            print("📄 下载的文件:")
            for file_path in downloaded_files:
                size = file_path.stat().st_size
                print(f"   - {file_path.name} ({size} bytes)")

if __name__ == "__main__":
    main()
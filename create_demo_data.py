#!/usr/bin/env python
"""
创建演示数据脚本
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum
from files.models import Folder, File

User = get_user_model()

def create_demo_user():
    """创建演示用户"""
    username = "demo"
    password = "demo123"
    email = "demo@example.com"
    
    if User.objects.filter(username=username).exists():
        print(f"演示用户 {username} 已存在")
        return User.objects.get(username=username)
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name="演示",
        last_name="用户"
    )
    print(f"创建演示用户: {username}/{password}")
    return user

def create_demo_folders(user):
    """创建演示文件夹"""
    folders_data = [
        {"name": "文档", "parent": None},
        {"name": "图片", "parent": None},
        {"name": "视频", "parent": None},
        {"name": "工作文档", "parent": "文档"},
        {"name": "个人照片", "parent": "图片"},
    ]
    
    created_folders = {}
    
    for folder_data in folders_data:
        parent_name = folder_data["parent"]
        parent = created_folders.get(parent_name) if parent_name else None
        
        folder, created = Folder.objects.get_or_create(
            name=folder_data["name"],
            parent=parent,
            owner=user,
            defaults={'owner': user}
        )
        
        if created:
            print(f"创建文件夹: {folder_data['name']}")
        
        created_folders[folder_data["name"]] = folder
    
    return created_folders

def create_demo_files(user, folders):
    """创建演示文件"""
    files_data = [
        {"name": "项目计划.docx", "folder": "工作文档", "size": 1024*1024},
        {"name": "会议记录.pdf", "folder": "工作文档", "size": 512*1024},
        {"name": "产品演示.pptx", "folder": "工作文档", "size": 2*1024*1024},
        {"name": "风景照.jpg", "folder": "个人照片", "size": 3*1024*1024},
        {"name": "家庭聚会.png", "folder": "个人照片", "size": 2.5*1024*1024},
        {"name": "预算表.xlsx", "folder": "文档", "size": 800*1024},
        {"name": "教程视频.mp4", "folder": "视频", "size": 50*1024*1024},
    ]
    
    for file_data in files_data:
        folder_name = file_data["folder"]
        folder = folders.get(folder_name)
        
        if folder:
            file_obj, created = File.objects.get_or_create(
                name=file_data["name"],
                folder=folder,
                owner=user,
                defaults={
                    'original_name': file_data["name"],
                    'size': file_data["size"],
                    'file_type': os.path.splitext(file_data["name"])[1],
                    'mime_type': 'application/octet-stream',
                    'swift_container': f'demo_container',
                    'swift_object': f'demo/{file_data["name"]}',
                }
            )
            
            if created:
                print(f"创建文件: {file_data['name']}")
    
    # 更新用户存储使用量
    total_size = File.objects.filter(owner=user).aggregate(
        total=models.Sum('size')
    )['total'] or 0
    
    user.used_storage = total_size
    user.save()

def main():
    """主函数"""
    print("🎯 创建演示数据")
    print("=" * 30)
    
    try:
        # 创建演示用户
        demo_user = create_demo_user()
        
        # 创建演示文件夹
        folders = create_demo_folders(demo_user)
        
        # 创建演示文件
        create_demo_files(demo_user, folders)
        
        print("\n✅ 演示数据创建完成！")
        print(f"登录信息: demo/demo123")
        print("访问地址: http://localhost:3000")
        
    except Exception as e:
        print(f"❌ 创建演示数据失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
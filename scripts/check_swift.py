#!/usr/bin/env python3
"""
检查Swift存储状态
"""
import os
import sys
import django

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from files.utils import get_swift_connection
from cloud_storage.settings import SWIFT_CONFIG

def check_swift_status():
    print('Swift配置信息:')
    for key, value in SWIFT_CONFIG.items():
        print(f'  {key}: {value}')

    print('\n测试Swift连接...')
    try:
        swift = get_swift_connection()
        print('✅ Swift连接成功')
        
        # 检查容器详情
        for result in swift.list():
            if result.get('listing'):
                for container in result['listing']:
                    print(f'容器: {container["name"]}')
                    print(f'  对象数量: {container["count"]}')
                    print(f'  总大小: {container["bytes"]} bytes')
                    
                    # 检查容器内容
                    try:
                        for obj_result in swift.list(container['name']):
                            if obj_result.get('listing'):
                                for obj in obj_result['listing']:
                                    print(f'    对象: {obj["name"]} ({obj["bytes"]} bytes)')
                    except Exception as e:
                        print(f'    无法列出对象: {e}')
                        
    except Exception as e:
        print(f'❌ Swift连接失败: {e}')

def test_swift_upload():
    print('\n测试Swift上传...')
    try:
        swift = get_swift_connection()
        
        # 创建测试文件
        test_content = b"This is a test file for Swift upload"
        container_name = "test_container"
        
        # 创建容器
        try:
            swift.post(container=container_name)
            print(f'✅ 创建容器: {container_name}')
        except Exception as e:
            print(f'容器可能已存在: {e}')
        
        # 上传文件
        from swiftclient.service import SwiftUploadObject
        import tempfile
        import uuid
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file.flush()
            
            object_name = f"test_{uuid.uuid4().hex[:8]}.txt"
            upload_obj = SwiftUploadObject(temp_file.name, object_name=object_name)
            
            for result in swift.upload(container_name, [upload_obj]):
                if result['success']:
                    print(f'✅ 上传成功: {object_name}')
                    
                    # 测试下载
                    for download_result in swift.download(container_name, [object_name]):
                        if download_result['success']:
                            content = download_result['contents'].read()
                            if content == test_content:
                                print(f'✅ 下载验证成功: {object_name}')
                            else:
                                print(f'❌ 下载内容不匹配')
                        else:
                            print(f'❌ 下载失败: {download_result.get("error")}')
                            
                    # 清理测试文件
                    for delete_result in swift.delete(container_name, [object_name]):
                        if delete_result['success']:
                            print(f'✅ 清理测试文件: {object_name}')
                        else:
                            print(f'❌ 清理失败: {delete_result.get("error")}')
                else:
                    print(f'❌ 上传失败: {result.get("error")}')
                    
            os.unlink(temp_file.name)
            
    except Exception as e:
        print(f'❌ Swift上传测试失败: {e}')

if __name__ == "__main__":
    check_swift_status()
    test_swift_upload()
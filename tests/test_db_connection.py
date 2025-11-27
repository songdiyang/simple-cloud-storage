#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试数据库连接
"""
import os
import sys
import django
import pymysql

# 设置控制台输出编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')

def test_mysql_connection():
    """测试MySQL连接"""
    print("🔍 测试MySQL数据库连接...")
    
    try:
        # 读取环境变量
        from dotenv import load_dotenv
        load_dotenv()
        
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', '3306'),
            'database': os.getenv('DB_NAME', 'cloud_storage'),
            'charset': 'utf8mb4'
        }
        
        print(f"连接配置: {db_config['host']}:{db_config['port']}")
        print(f"数据库: {db_config['database']}")
        print(f"用户: {db_config['user']}")
        
        # 测试连接
        connection = pymysql.connect(**db_config)
        print("✅ MySQL连接成功！")
        
        # 检查数据库是否存在
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES LIKE %s", (db_config['database'],))
            result = cursor.fetchone()
            if result:
                print(f"✅ 数据库 '{db_config['database']}' 存在")
            else:
                print(f"❌ 数据库 '{db_config['database']}' 不存在")
                print("请运行: CREATE DATABASE cloud_storage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        
        connection.close()
        return True
        
    except ImportError:
        print("❌ PyMySQL未安装，请运行: pip install PyMySQL")
        return False
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_django_connection():
    """测试Django数据库连接"""
    print("\n🔍 测试Django数据库连接...")
    
    try:
        django.setup()
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✅ Django数据库连接成功！")
                return True
    except Exception as e:
        print(f"❌ Django数据库连接失败: {e}")
        return False

def main():
    """主函数"""
    print("🗄️  数据库连接测试")
    print("=" * 30)
    
    # 测试MySQL连接
    mysql_ok = test_mysql_connection()
    
    if mysql_ok:
        # 测试Django连接
        django_ok = test_django_connection()
        
        if django_ok:
            print("\n🎉 所有数据库连接测试通过！")
            print("现在可以运行数据库迁移:")
            print("python manage.py makemigrations")
            print("python manage.py migrate")
        else:
            print("\n❌ Django连接失败，请检查配置")
    else:
        print("\n❌ MySQL连接失败，请检查数据库服务")

if __name__ == "__main__":
    main()
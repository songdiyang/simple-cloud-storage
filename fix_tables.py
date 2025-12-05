import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_storage.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# 创建 VIPApplication 表
try:
    cursor.execute("""
        CREATE TABLE `accounts_vipapplication` (
            `id` char(32) NOT NULL PRIMARY KEY, 
            `order_number` varchar(100) NOT NULL, 
            `status` varchar(20) NOT NULL DEFAULT 'pending', 
            `admin_note` longtext NULL, 
            `created_at` datetime(6) NOT NULL, 
            `reviewed_at` datetime(6) NULL, 
            `reviewed_by_id` bigint NULL, 
            `user_id` bigint NOT NULL,
            CONSTRAINT `accounts_vipapplication_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
            CONSTRAINT `accounts_vipapplication_reviewed_by_id_fk` FOREIGN KEY (`reviewed_by_id`) REFERENCES `accounts_user` (`id`)
        )
    """)
    print("VIPApplication 表创建成功")
except Exception as e:
    if 'already exists' in str(e):
        print("VIPApplication 表已存在")
    else:
        print(f"VIPApplication 创建失败: {e}")

# 创建 LoginRecord 表
try:
    cursor.execute("""
        CREATE TABLE `accounts_loginrecord` (
            `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
            `login_time` datetime(6) NOT NULL,
            `ip_address` char(39) NULL,
            `user_agent` longtext NULL,
            `user_id` bigint NOT NULL,
            CONSTRAINT `accounts_loginrecord_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
        )
    """)
    print("LoginRecord 表创建成功")
except Exception as e:
    if 'already exists' in str(e):
        print("LoginRecord 表已存在")
    else:
        print(f"LoginRecord 创建失败: {e}")

# 创建 OnlineUser 表
try:
    cursor.execute("""
        CREATE TABLE `accounts_onlineuser` (
            `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
            `last_activity` datetime(6) NOT NULL,
            `is_online` bool NOT NULL DEFAULT TRUE,
            `user_id` bigint NOT NULL UNIQUE,
            CONSTRAINT `accounts_onlineuser_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
        )
    """)
    print("OnlineUser 表创建成功")
except Exception as e:
    if 'already exists' in str(e):
        print("OnlineUser 表已存在")
    else:
        print(f"OnlineUser 创建失败: {e}")

print("数据库表修复完成！")

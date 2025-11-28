from django.core.management.base import BaseCommand
from django.db import models
from accounts.models import User
from files.models import File


class Command(BaseCommand):
    help = '同步所有用户的存储使用量'

    def handle(self, *args, **options):
        users = User.objects.all()
        updated_count = 0
        
        for user in users:
            # 计算用户实际文件总大小
            actual_used_storage = File.objects.filter(owner=user).aggregate(
                total_size=models.Sum('size')
            )['total_size'] or 0
            
            # 检查是否需要更新
            if user.used_storage != actual_used_storage:
                old_usage = user.used_storage
                user.used_storage = actual_used_storage
                user.save()
                
                self.stdout.write(
                    self.style.WARNING(
                        f'用户 {user.username}: {old_usage} -> {actual_used_storage} bytes'
                    )
                )
                updated_count += 1
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'用户 {user.username}: 存储信息正确 ({actual_used_storage} bytes)'
                    )
                )
        
        if updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✅ 已更新 {updated_count} 个用户的存储信息')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ 所有用户的存储信息都是正确的')
            )
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 
                   'storage_quota_display', 'used_storage_display', 
                   'storage_usage_percentage', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('存储信息', {
            'fields': ('avatar', 'storage_quota', 'used_storage')
        }),
    )
    
    def storage_quota_display(self, obj):
        return f"{obj.storage_quota / (1024**3):.2f} GB"
    storage_quota_display.short_description = '存储配额'
    
    def used_storage_display(self, obj):
        return f"{obj.used_storage / (1024**3):.2f} GB"
    used_storage_display.short_description = '已使用存储'
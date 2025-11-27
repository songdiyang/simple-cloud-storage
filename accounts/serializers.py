from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    storage_quota_display = serializers.SerializerMethodField()
    used_storage_display = serializers.SerializerMethodField()
    available_storage_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'avatar', 'storage_quota', 'used_storage', 'available_storage',
                 'storage_quota_display', 'used_storage_display', 
                 'available_storage_display', 'storage_usage_percentage',
                 'date_joined', 'created_at', 'updated_at']
        read_only_fields = ['id', 'date_joined', 'created_at', 'updated_at', 
                           'used_storage', 'available_storage', 'storage_usage_percentage']
    
    def get_storage_quota_display(self, obj):
        """格式化存储配额显示"""
        return self.format_bytes(obj.storage_quota)
    
    def get_used_storage_display(self, obj):
        """格式化已使用存储显示"""
        return self.format_bytes(obj.used_storage)
    
    def get_available_storage_display(self, obj):
        """格式化可用存储显示"""
        return self.format_bytes(obj.available_storage)
    
    def format_bytes(self, bytes_value):
        """格式化字节数为可读格式"""
        if bytes_value == 0:
            return "0 B"
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        while bytes_value >= 1024 and unit_index < len(units) - 1:
            bytes_value /= 1024
            unit_index += 1
        return f"{bytes_value:.2f} {units[unit_index]}"


class RegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("密码确认不匹配")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, VIPApplication


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    storage_quota_display = serializers.SerializerMethodField()
    used_storage_display = serializers.SerializerMethodField()
    available_storage_display = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'avatar', 'role', 'role_display', 'storage_quota', 'used_storage', 'available_storage',
                 'storage_quota_display', 'used_storage_display', 
                 'available_storage_display', 'storage_usage_percentage',
                 'is_vip', 'is_admin_user',
                 'date_joined', 'created_at', 'updated_at']
        read_only_fields = ['id', 'date_joined', 'created_at', 'updated_at', 
                           'used_storage', 'available_storage', 'storage_usage_percentage',
                           'role', 'is_vip', 'is_admin_user']
    
    def get_role_display(self, obj):
        """获取角色显示名称"""
        return obj.get_role_display()
    
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


class VIPApplicationSerializer(serializers.ModelSerializer):
    """VIP申请序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = VIPApplication
        fields = ['id', 'username', 'order_number', 'status', 'status_display', 
                 'admin_note', 'created_at', 'reviewed_at']
        read_only_fields = ['id', 'status', 'admin_note', 'created_at', 'reviewed_at']
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class VIPApplicationCreateSerializer(serializers.Serializer):
    """VIP申请创建序列化器"""
    order_number = serializers.CharField(max_length=100, required=True)
    
    def validate_order_number(self, value):
        if not value.strip():
            raise serializers.ValidationError("赞助单号不能为空")
        return value.strip()
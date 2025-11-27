from rest_framework import serializers
from .models import Folder, File, FileShare


class FolderSerializer(serializers.ModelSerializer):
    """文件夹序列化器"""
    full_path = serializers.ReadOnlyField()
    children_count = serializers.SerializerMethodField()
    files_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Folder
        fields = ['id', 'name', 'parent', 'full_path', 'children_count', 
                 'files_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children_count(self, obj):
        return obj.children.count()
    
    def get_files_count(self, obj):
        return obj.files.count()


class CreateFolderSerializer(serializers.Serializer):
    """创建文件夹序列化器"""
    name = serializers.CharField(max_length=255)
    parent_id = serializers.UUIDField(required=False, allow_null=True)


class FileSerializer(serializers.ModelSerializer):
    """文件序列化器"""
    size_display = serializers.ReadOnlyField()
    file_extension = serializers.ReadOnlyField()
    swift_url = serializers.SerializerMethodField()
    folder_name = serializers.SerializerMethodField()
    
    class Meta:
        model = File
        fields = ['id', 'name', 'original_name', 'folder', 'folder_name', 
                 'size', 'size_display', 'file_type', 'mime_type', 
                 'file_extension', 'is_public', 'download_count', 
                 'swift_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'download_count']
    
    def get_swift_url(self, obj):
        if obj.is_public:
            return obj.get_swift_url()
        return None
    
    def get_folder_name(self, obj):
        return obj.folder.name if obj.folder else '根目录'


class UploadFileSerializer(serializers.Serializer):
    """文件上传序列化器"""
    file = serializers.FileField()
    folder_id = serializers.UUIDField(required=False, allow_null=True)


class FileShareSerializer(serializers.ModelSerializer):
    """文件分享序列化器"""
    file_name = serializers.SerializerMethodField()
    file_size_display = serializers.SerializerMethodField()
    is_expired = serializers.ReadOnlyField()
    share_url = serializers.SerializerMethodField()
    
    class Meta:
        model = FileShare
        fields = ['id', 'file', 'file_name', 'file_size_display', 'share_code',
                 'password', 'is_active', 'is_expired', 'expire_at', 
                 'max_downloads', 'download_count', 'share_url', 'created_at']
        read_only_fields = ['id', 'share_code', 'download_count', 'created_at']
    
    def get_file_name(self, obj):
        return obj.file.name
    
    def get_file_size_display(self, obj):
        return obj.file.size_display
    
    def get_share_url(self, obj):
        # 返回前端分享链接
        return f"/share/{obj.share_code}"
from django.contrib import admin
from .models import Folder, File, FileShare


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'parent', 'created_at', 'updated_at']
    list_filter = ['created_at', 'owner']
    search_fields = ['name', 'owner__username']
    ordering = ['-created_at']


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'folder', 'size_display', 'file_type', 
                   'is_public', 'download_count', 'created_at']
    list_filter = ['file_type', 'is_public', 'created_at', 'owner']
    search_fields = ['name', 'original_name', 'owner__username']
    ordering = ['-created_at']
    readonly_fields = ['swift_container', 'swift_object', 'download_count']
    
    def size_display(self, obj):
        return obj.size_display
    size_display.short_description = '文件大小'


@admin.register(FileShare)
class FileShareAdmin(admin.ModelAdmin):
    list_display = ['file', 'owner', 'share_code', 'is_active', 'is_expired',
                   'download_count', 'expire_at', 'created_at']
    list_filter = ['is_active', 'created_at', 'owner']
    search_fields = ['file__name', 'share_code', 'owner__username']
    ordering = ['-created_at']
    readonly_fields = ['share_code', 'download_count']
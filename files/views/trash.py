"""
回收站相关视图
"""
import os
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import File
from ..serializers import FileSerializer
from ..utils import delete_file_from_swift
from .helpers import format_bytes


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trash_list(request):
    """获取回收站文件列表"""
    files = File.objects.filter(owner=request.user, is_deleted=True).order_by('-deleted_at')
    serializer = FileSerializer(files, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trash_stats(request):
    """获取回收站统计信息"""
    deleted_files = File.objects.filter(owner=request.user, is_deleted=True)
    count = deleted_files.count()
    total_size = sum(f.size for f in deleted_files)
    
    return Response({
        'count': count,
        'total_size': total_size,
        'total_size_display': format_bytes(total_size)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_file(request, file_id):
    """从回收站恢复文件"""
    file_obj = get_object_or_404(File, id=file_id, owner=request.user, is_deleted=True)
    
    try:
        # 恢复文件
        file_obj.is_deleted = False
        file_obj.deleted_at = None
        file_obj.save()
        
        return Response({
            'message': '文件已恢复',
            'file': FileSerializer(file_obj).data
        })
    except Exception as e:
        return Response({
            'error': f'恢复文件失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def permanent_delete_file(request, file_id):
    """彻底删除文件（从回收站）"""
    file_obj = get_object_or_404(File, id=file_id, owner=request.user, is_deleted=True)
    
    try:
        with transaction.atomic():
            # 尝试从Swift删除文件
            try:
                if file_obj.swift_container and file_obj.swift_object:
                    success, result = delete_file_from_swift(file_obj.swift_container, file_obj.swift_object)
                    if not success:
                        print(f"Warning: Swift deletion failed: {result}")
            except Exception as swift_error:
                print(f"Warning: Swift deletion error: {swift_error}")
            
            # 尝试删除本地文件
            if file_obj.local_path:
                try:
                    if os.path.exists(file_obj.local_path):
                        os.remove(file_obj.local_path)
                except Exception as local_error:
                    print(f"Warning: Local file deletion error: {local_error}")
            
            # 更新用户存储使用量
            request.user.used_storage -= file_obj.size
            request.user.save()
            
            # 删除文件记录
            file_obj.delete()
            
            return Response({'message': '文件已彻底删除'})
            
    except Exception as e:
        return Response({
            'error': f'删除文件失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def empty_trash(request):
    """清空回收站"""
    try:
        with transaction.atomic():
            deleted_files = File.objects.filter(owner=request.user, is_deleted=True)
            total_size = 0
            
            for file_obj in deleted_files:
                # 尝试从Swift删除文件
                try:
                    if file_obj.swift_container and file_obj.swift_object:
                        delete_file_from_swift(file_obj.swift_container, file_obj.swift_object)
                except Exception:
                    pass
                
                # 尝试删除本地文件
                if file_obj.local_path:
                    try:
                        if os.path.exists(file_obj.local_path):
                            os.remove(file_obj.local_path)
                    except Exception:
                        pass
                
                total_size += file_obj.size
            
            count = deleted_files.count()
            deleted_files.delete()
            
            # 更新用户存储使用量
            request.user.used_storage -= total_size
            request.user.save()
            
            return Response({
                'message': f'已清空回收站，共删除 {count} 个文件',
                'deleted_count': count,
                'freed_space': total_size
            })
            
    except Exception as e:
        return Response({
            'error': f'清空回收站失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

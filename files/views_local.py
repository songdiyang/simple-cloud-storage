"""
本地文件存储视图（作为Swift的备选方案）
"""
import os
import uuid
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from .models import Folder, File, FileShare
from .serializers import (
    FolderSerializer, FileSerializer, FileShareSerializer,
    CreateFolderSerializer, UploadFileSerializer
)
from .utils_local import upload_file_locally, delete_file_locally, get_file_url


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_file_local(request):
    """本地文件上传"""
    serializer = UploadFileSerializer(data=request.data)
    if serializer.is_valid():
        uploaded_file = serializer.validated_data['file']
        folder_id = serializer.validated_data.get('folder_id')
        
        folder = None
        if folder_id:
            folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
        
        # 检查存储空间
        if request.user.used_storage + uploaded_file.size > request.user.storage_quota:
            return Response({
                'error': '存储空间不足'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # 上传到本地存储
                success, file_path = upload_file_locally(uploaded_file, request.user.id)
                if not success:
                    return Response({
                        'error': f'文件上传失败: {file_path}'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # 创建文件记录
                file_obj = File.objects.create(
                    name=uploaded_file.name,
                    original_name=uploaded_file.name,
                    folder=folder,
                    owner=request.user,
                    size=uploaded_file.size,
                    file_type=os.path.splitext(uploaded_file.name)[1],
                    mime_type=uploaded_file.content_type or 'application/octet-stream',
                    swift_container='local_storage',  # 标识为本地存储
                    swift_object=file_path  # 存储本地文件路径
                )
                
                # 更新用户存储使用量
                request.user.used_storage += uploaded_file.size
                request.user.save()
                
                # 返回文件信息，包含访问URL
                file_data = FileSerializer(file_obj).data
                file_data['url'] = get_file_url(file_path)
                
                return Response(file_data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'error': f'文件上传过程中发生错误: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_file_local(request, file_id):
    """本地文件删除"""
    file_obj = get_object_or_404(File, id=file_id, owner=request.user)
    
    try:
        with transaction.atomic():
            # 从本地存储删除文件
            if file_obj.swift_object:
                success, error = delete_file_locally(file_obj.swift_object)
                if not success:
                    print(f"Warning: Failed to delete local file: {error}")
            
            # 更新用户存储使用量
            request.user.used_storage -= file_obj.size
            request.user.save()
            
            # 删除数据库记录
            file_obj.delete()
            
            return Response({'message': '文件删除成功'})
            
    except Exception as e:
        return Response({
            'error': f'文件删除过程中发生错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
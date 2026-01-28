"""
文件基础操作视图（上传、列表、详情、删除）
"""
import os
import uuid

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser

from ..models import Folder, File
from ..serializers import FileSerializer, UploadFileSerializer
from ..utils import upload_file_to_swift, upload_file_to_local


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def file_list(request):
    """获取文件列表"""
    folder_id = request.GET.get('folder_id')
    files = File.objects.filter(owner=request.user, is_deleted=False)
    
    if folder_id:
        files = files.filter(folder_id=folder_id)
    else:
        files = files.filter(folder__isnull=True)
    
    # 分页
    paginator = PageNumberPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(files, request)
    serializer = FileSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def file_detail(request, file_id):
    """获取文件详情"""
    file_obj = get_object_or_404(File, id=file_id, owner=request.user)
    serializer = FileSerializer(file_obj)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    """上传文件"""
    serializer = UploadFileSerializer(data=request.data)
    if serializer.is_valid():
        uploaded_file = serializer.validated_data['file']
        folder_id = serializer.validated_data.get('folder_id')
        
        folder = None
        if folder_id:
            folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
        
        try:
            with transaction.atomic():
                # 生成Swift对象名
                object_name = f"{request.user.id}/{uuid.uuid4()}/{uploaded_file.name}"
                container_name = f"user_{request.user.id}_files"
                
                # 尝试上传到Swift，如果失败则使用本地存储
                swift_success, swift_result = upload_file_to_swift(uploaded_file, container_name, object_name)
                
                if not swift_success:
                    # Swift失败，尝试本地存储
                    if getattr(settings, 'LOCAL_STORAGE_ENABLED', False):
                        try:
                            local_success, local_result = upload_file_to_local(uploaded_file, request.user.id, uploaded_file.name)
                            if local_success:
                                swift_container = None
                                swift_object = None
                                local_path = local_result
                            else:
                                return Response({
                                    'error': f'Swift和本地存储都失败: Swift错误({swift_result}), 本地错误({local_result})'
                                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                        except Exception as local_error:
                            return Response({
                                'error': f'Swift上传失败且本地存储异常: {swift_result}, 本地错误: {str(local_error)}'
                            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    else:
                        return Response({
                            'error': f'Swift上传失败: {swift_result}。请检查Swift服务状态。'
                        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                else:
                    # Swift成功
                    swift_container = container_name
                    swift_object = object_name
                    local_path = None
                
                # 创建文件记录
                file_obj = File.objects.create(
                    name=uploaded_file.name,
                    original_name=uploaded_file.name,
                    folder=folder,
                    owner=request.user,
                    size=uploaded_file.size,
                    file_type=os.path.splitext(uploaded_file.name)[1],
                    mime_type=uploaded_file.content_type or 'application/octet-stream',
                    swift_container=swift_container,
                    swift_object=swift_object,
                    local_path=local_path
                )
                
                # 更新用户存储使用量
                request.user.used_storage += uploaded_file.size
                request.user.save()
                
                return Response(FileSerializer(file_obj).data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'error': f'文件上传过程中发生错误: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_file(request, file_id):
    """删除文件（软删除，移动到回收站）"""
    file_obj = get_object_or_404(File, id=file_id, owner=request.user, is_deleted=False)
    
    try:
        # 软删除：标记为已删除
        file_obj.is_deleted = True
        file_obj.deleted_at = timezone.now()
        file_obj.save()
        
        return Response({'message': '文件已移至回收站'})
            
    except Exception as e:
        return Response({
            'error': f'文件删除过程中发生错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

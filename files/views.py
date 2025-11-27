import os
import uuid
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, StreamingHttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from .models import Folder, File, FileShare
from .serializers import (
    FolderSerializer, FileSerializer, FileShareSerializer,
    CreateFolderSerializer, UploadFileSerializer
)
from .utils import upload_file_to_swift, delete_file_from_swift, generate_share_code, download_file_from_swift


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def folder_list(request):
    """获取文件夹列表"""
    parent_id = request.GET.get('parent_id')
    folders = Folder.objects.filter(owner=request.user, parent_id=parent_id)
    serializer = FolderSerializer(folders, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_folder(request):
    """创建文件夹"""
    serializer = CreateFolderSerializer(data=request.data)
    if serializer.is_valid():
        parent_id = serializer.validated_data.get('parent_id')
        parent = None
        if parent_id:
            parent = get_object_or_404(Folder, id=parent_id, owner=request.user)
        
        folder = Folder.objects.create(
            name=serializer.validated_data['name'],
            parent=parent,
            owner=request.user
        )
        return Response(FolderSerializer(folder).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_folder(request, folder_id):
    """删除文件夹"""
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    
    # 检查文件夹是否为空
    if folder.children.exists() or folder.files.exists():
        return Response({
            'error': '文件夹不为空，无法删除'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    folder.delete()
    return Response({'message': '文件夹删除成功'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def file_list(request):
    """获取文件列表"""
    folder_id = request.GET.get('folder_id')
    files = File.objects.filter(owner=request.user)
    
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
                
                # 上传到Swift
                success, result = upload_file_to_swift(uploaded_file, container_name, object_name)
                if not success:
                    return Response({
                        'error': f'Swift上传失败: {result}。请检查Swift服务状态。'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
                # 创建文件记录
                file_obj = File.objects.create(
                    name=uploaded_file.name,
                    original_name=uploaded_file.name,
                    folder=folder,
                    owner=request.user,
                    size=uploaded_file.size,
                    file_type=os.path.splitext(uploaded_file.name)[1],
                    mime_type=uploaded_file.content_type or 'application/octet-stream',
                    swift_container=container_name,
                    swift_object=object_name
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
    """删除文件"""
    file_obj = get_object_or_404(File, id=file_id, owner=request.user)
    
    try:
        with transaction.atomic():
            # 尝试从Swift删除文件，但不阻止数据库删除
            try:
                success, result = delete_file_from_swift(file_obj.swift_container, file_obj.swift_object)
                if not success:
                    print(f"Warning: Swift deletion failed: {result}")
                    # 记录错误但不阻止删除
            except Exception as swift_error:
                print(f"Warning: Swift deletion error: {swift_error}")
                # 记录错误但不阻止删除
            
            # 更新用户存储使用量
            request.user.used_storage -= file_obj.size
            request.user.save()
            
            # 删除文件记录
            file_obj.delete()
            
            return Response({'message': '文件删除成功'})
            
    except Exception as e:
        return Response({
            'error': f'文件删除过程中发生错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def file_detail(request, file_id):
    """获取文件详情"""
    file_obj = get_object_or_404(File, id=file_id, owner=request.user)
    serializer = FileSerializer(file_obj)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_share(request, file_id):
    """创建文件分享"""
    file_obj = get_object_or_404(File, id=file_id, owner=request.user)
    
    # 检查是否已有活跃的分享
    existing_share = FileShare.objects.filter(
        file=file_obj,
        owner=request.user,
        is_active=True
    ).first()
    
    if existing_share and not existing_share.is_expired():
        return Response({
            'error': '该文件已有活跃的分享链接'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 创建新分享
    share = FileShare.objects.create(
        file=file_obj,
        owner=request.user,
        share_code=generate_share_code(),
        password=request.data.get('password', ''),
        expire_at=request.data.get('expire_at'),
        max_downloads=request.data.get('max_downloads')
    )
    
    return Response(FileShareSerializer(share).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_shares(request):
    """获取我的分享列表"""
    shares = FileShare.objects.filter(owner=request.user).order_by('-created_at')
    serializer = FileShareSerializer(shares, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_share(request, share_id):
    """删除分享"""
    share = get_object_or_404(FileShare, id=share_id, owner=request.user)
    share.is_active = False
    share.save()
    return Response({'message': '分享已取消'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def storage_info(request):
    """获取存储信息"""
    user = request.user
    return Response({
        'storage_quota': user.storage_quota,
        'used_storage': user.used_storage,
        'available_storage': user.available_storage,
        'storage_usage_percentage': user.storage_usage_percentage,
        'total_files': File.objects.filter(owner=user).count(),
        'total_folders': Folder.objects.filter(owner=user).count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_file(request, file_id):
    """下载文件"""
    file_obj = get_object_or_404(File, id=file_id, owner=request.user)
    
    try:
        # 从Swift下载文件
        success, result = download_file_from_swift(file_obj.swift_container, file_obj.swift_object)
        
        if success:
            # 更新下载次数
            file_obj.download_count += 1
            file_obj.save()
            
            # 获取文件内容
            file_content, headers = result
            
            # 对于二进制文件，使用HttpResponse而不是StreamingHttpResponse
            if file_obj.mime_type.startswith(('image/', 'video/', 'audio/', 'application/')):
                response = HttpResponse(
                    file_content,
                    content_type=file_obj.mime_type
                )
            else:
                # 对于文本文件，可以使用StreamingHttpResponse
                response = StreamingHttpResponse(
                    file_content,
                    content_type=file_obj.mime_type
                )
            
            # 设置下载头
            response['Content-Disposition'] = f'attachment; filename="{file_obj.original_name}"'
            response['Content-Length'] = file_obj.size
            
            # 复制其他必要的头信息
            if headers:
                for key, value in headers.items():
                    if key.lower() not in ['content-disposition', 'content-type', 'content-length']:
                        response[key] = value
            
            return response
        else:
            return Response({
                'error': f'Swift下载失败: {result}。请检查Swift服务状态。'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
    except Exception as e:
        return Response({
            'error': f'文件下载过程中发生错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_download_url(request, file_id):
    """获取文件下载URL（用于前端直接下载）"""
    file_obj = get_object_or_404(File, id=file_id, owner=request.user)
    
    try:
        # 生成临时下载URL
        temp_url = file_obj.get_swift_url()
        if temp_url:
            # 更新下载次数（预下载计数）
            file_obj.download_count += 1
            file_obj.save()
            
            return Response({
                'download_url': temp_url,
                'filename': file_obj.original_name,
                'size': file_obj.size,
                'method': 'swift'
            })
        else:
            # 如果Swift URL生成失败，返回直接下载API的URL
            direct_download_url = f"/api/files/{file_id}/download/"
            
            return Response({
                'download_url': direct_download_url,
                'filename': file_obj.original_name,
                'size': file_obj.size,
                'method': 'direct',  # 标识这是直接下载
                'message': 'Swift存储暂时不可用，使用直接下载方式'
            })
            
    except Exception as e:
        return Response({
            'error': f'生成下载链接时发生错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
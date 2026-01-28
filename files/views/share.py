"""
分享相关视图
"""
import uuid
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Folder, File, FileShare
from ..serializers import FileSerializer, FileShareSerializer
from ..utils import generate_share_code, download_file_from_swift, upload_file_to_swift
from .helpers import (
    check_password_attempts,
    record_failed_attempt,
    clear_password_attempts,
)


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
    shares = FileShare.objects.filter(owner=request.user, is_active=True).order_by('-created_at')
    serializer = FileShareSerializer(shares, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def deleted_shares(request):
    """获取已删除的分享列表"""
    shares = FileShare.objects.filter(owner=request.user, is_active=False).order_by('-created_at')
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
@permission_classes([])
def get_share_info(request, share_code):
    """获取分享信息（无需登录）"""
    try:
        share = FileShare.objects.get(
            share_code=share_code,
            is_active=True
        )
        
        # 检查是否过期
        if share.is_expired():
            return Response({
                'error': '分享已过期',
                'is_expired': True
            }, status=status.HTTP_410_GONE)
        
        # 检查密码尝试次数
        is_locked, attempts, remaining, lockout_time = check_password_attempts(share_code, request)
        
        if is_locked:
            return Response({
                'error': f'密码尝试次数过多，请{lockout_time // 60}分钟后再试',
                'is_locked': True,
                'lockout_time': lockout_time
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # 如果有密码保护，返回需要密码的提示
        if share.password:
            password = request.GET.get('password', '')
            if password != share.password:
                return Response({
                    'error': '需要密码',
                    'password_required': True,
                    'share_code': share.share_code,
                    'remaining_attempts': remaining
                }, status=status.HTTP_403_FORBIDDEN)
        
        return Response({
            'id': share.id,
            'file_name': share.file.original_name,
            'file_size': share.file.size,
            'file_type': share.file.file_type,
            'download_count': share.download_count,
            'max_downloads': share.max_downloads,
            'expire_at': share.expire_at.isoformat() if share.expire_at else None,
            'created_at': share.created_at.isoformat(),
            'is_expired': share.is_expired(),
            'share_code': share.share_code,
            'password_protected': bool(share.password)
        })
        
    except FileShare.DoesNotExist:
        return Response({
            'error': '分享不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([])
def verify_share_password(request, share_code):
    """验证分享文件密码"""
    try:
        share = FileShare.objects.get(
            share_code=share_code,
            is_active=True
        )
        
        # 检查是否过期
        if share.is_expired():
            return Response({
                'error': '分享已过期',
                'is_expired': True
            }, status=status.HTTP_410_GONE)
        
        # 如果没有密码保护，直接返回成功
        if not share.password:
            return Response({
                'success': True,
                'message': '该文件不需要密码'
            })
        
        # 检查密码尝试次数
        is_locked, attempts, remaining, lockout_time = check_password_attempts(share_code, request)
        
        if is_locked:
            return Response({
                'error': f'密码尝试次数过多，请{lockout_time // 60}分钟后再试',
                'is_locked': True,
                'lockout_time': lockout_time,
                'attempts': attempts,
                'remaining': 0
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # 验证密码
        password = request.data.get('password', '')
        if password == share.password:
            # 密码正确，清除尝试记录
            clear_password_attempts(share_code, request)
            return Response({
                'success': True,
                'message': '密码正确',
                'file_name': share.file.original_name,
                'file_size': share.file.size,
                'file_type': share.file.file_type,
                'download_count': share.download_count,
                'max_downloads': share.max_downloads,
                'expire_at': share.expire_at.isoformat() if share.expire_at else None,
                'created_at': share.created_at.isoformat(),
                'share_code': share.share_code
            })
        else:
            # 密码错误，记录失败尝试
            new_attempts = record_failed_attempt(share_code, request)
            max_attempts = getattr(settings, 'PASSWORD_MAX_ATTEMPTS', 3)
            new_remaining = max_attempts - new_attempts
            
            if new_remaining <= 0:
                return Response({
                    'error': f'密码错误，尝试次数已用完，请{lockout_time // 60}分钟后再试',
                    'is_locked': True,
                    'lockout_time': lockout_time,
                    'attempts': new_attempts,
                    'remaining': 0
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                return Response({
                    'error': f'密码错误，还剩{new_remaining}次尝试机会',
                    'success': False,
                    'attempts': new_attempts,
                    'remaining': new_remaining
                }, status=status.HTTP_403_FORBIDDEN)
                
    except FileShare.DoesNotExist:
        return Response({
            'error': '分享不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([])
def download_shared_file(request, share_code):
    """下载分享的文件（无需登录）"""
    try:
        share = FileShare.objects.get(
            share_code=share_code,
            is_active=True
        )
        
        # 检查是否过期
        if share.is_expired():
            return Response({
                'error': '分享已过期'
            }, status=status.HTTP_410_GONE)
        
        # 检查密码尝试次数
        is_locked, attempts, remaining, lockout_time = check_password_attempts(share_code, request)
        
        if is_locked:
            return Response({
                'error': f'密码尝试次数过多，请{lockout_time // 60}分钟后再试',
                'is_locked': True,
                'lockout_time': lockout_time
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # 检查密码
        password = request.data.get('password', '')
        if share.password and password != share.password:
            # 记录失败尝试
            new_attempts = record_failed_attempt(share_code, request)
            max_attempts = getattr(settings, 'PASSWORD_MAX_ATTEMPTS', 3)
            new_remaining = max_attempts - new_attempts
            
            if new_remaining <= 0:
                return Response({
                    'error': f'密码错误，尝试次数已用完，请{lockout_time // 60}分钟后再试',
                    'is_locked': True,
                    'remaining': 0
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                return Response({
                    'error': f'密码错误，还剩{new_remaining}次尝试机会',
                    'remaining': new_remaining
                }, status=status.HTTP_403_FORBIDDEN)
        
        # 密码正确，清除尝试记录
        if share.password:
            clear_password_attempts(share_code, request)
        
        # 检查下载次数
        if share.max_downloads and share.download_count >= share.max_downloads:
            return Response({
                'error': '下载次数已达上限'
            }, status=status.HTTP_410_GONE)
        
        # 从Swift下载文件
        success, result = download_file_from_swift(
            share.file.swift_container, 
            share.file.swift_object
        )
        
        if not success:
            return Response({
                'error': f'文件下载失败: {result}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # 更新下载次数
        share.download_count += 1
        share.save()
        
        # 获取文件内容
        file_content, headers = result
        
        # 直接返回文件内容进行下载
        response = HttpResponse(
            file_content,
            content_type=share.file.mime_type or 'application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{share.file.original_name}"'
        response['Content-Length'] = share.file.size
        
        return response
        
    except FileShare.DoesNotExist:
        return Response({
            'error': '分享不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_shared_file(request):
    """将分享的文件保存到用户云盘"""
    share_code = request.data.get('share_code')
    folder_id = request.data.get('folder_id')
    password = request.data.get('password', '')
    
    if not share_code:
        return Response({
            'error': '缺少分享码'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 获取分享信息
        share = get_object_or_404(FileShare, share_code=share_code, is_active=True)
        
        # 检查分享是否过期
        if share.is_expired():
            return Response({
                'error': '分享已过期'
            }, status=status.HTTP_410_GONE)
        
        # 检查密码
        if share.password and password != share.password:
            return Response({
                'error': '密码错误'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 检查用户是否已有同名文件
        folder = None
        if folder_id:
            folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
        
        existing_file = File.objects.filter(
            owner=request.user,
            folder=folder,
            name=share.file.original_name
        ).first()
        
        if existing_file:
            return Response({
                'error': f'文件 "{share.file.original_name}" 已存在于目标位置'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 从Swift下载原文件内容
        success, result = download_file_from_swift(
            share.file.swift_container,
            share.file.swift_object
        )
        
        if not success:
            return Response({
                'error': f'无法获取文件内容: {result}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        file_content, headers = result
        
        try:
            with transaction.atomic():
                # 生成新的Swift对象名
                object_name = f"{request.user.id}/{uuid.uuid4()}/{share.file.original_name}"
                container_name = f"user_{request.user.id}_files"
                
                # 将文件内容上传到用户的Swift容器
                from django.core.files.uploadedfile import SimpleUploadedFile
                temp_file = SimpleUploadedFile(
                    share.file.original_name,
                    file_content,
                    content_type=share.file.mime_type
                )
                
                upload_success, upload_result = upload_file_to_swift(
                    temp_file, container_name, object_name
                )
                
                if not upload_success:
                    return Response({
                        'error': f'文件上传失败: {upload_result}'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
                # 创建文件记录
                new_file = File.objects.create(
                    name=share.file.original_name,
                    original_name=share.file.original_name,
                    folder=folder,
                    owner=request.user,
                    size=share.file.size,
                    file_type=share.file.file_type,
                    mime_type=share.file.mime_type,
                    swift_container=container_name,
                    swift_object=object_name,
                    download_count=0
                )
                
                # 更新用户存储使用量
                request.user.used_storage += share.file.size
                request.user.save()
                
                return Response({
                    'message': '文件保存成功',
                    'file': FileSerializer(new_file).data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'error': f'保存过程中发生错误: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except FileShare.DoesNotExist:
        return Response({
            'error': '分享不存在'
        }, status=status.HTTP_404_NOT_FOUND)

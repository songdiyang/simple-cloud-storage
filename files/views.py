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
@permission_classes([])  # 公开访问，不需要认证
def get_share_info(request, share_code):
    """获取分享信息（公开访问）"""
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
        
        # 检查是否需要密码
        if share.password and not request.GET.get('password'):
            return Response({
                'error': '需要密码',
                'password_required': True
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 验证密码
        if share.password and request.GET.get('password') != share.password:
            return Response({
                'error': '密码错误'
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
            'is_expired': share.is_expired()
        })
        
    except FileShare.DoesNotExist:
        return Response({
            'error': '分享不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([])  # 公开访问，不需要认证
def download_shared_file(request, share_code):
    """下载分享的文件"""
    try:
        share = FileShare.objects.get(
            share_code=share_code,
            is_active=True
        )
        
        # 检查是否过期
        if share.is_expired():
            return Response({
                'error': '分享已过期或下载次数已达上限'
            }, status=status.HTTP_410_GONE)
        
        # 检查密码
        if share.password:
            password = request.data.get('password') or request.GET.get('password')
            if password != share.password:
                return Response({
                    'error': '密码错误'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # 从Swift下载文件
        success, result = download_file_from_swift(share.file.swift_container, share.file.swift_object)
        
        if success:
            file_content, headers = result
            
            # 更新下载次数
            share.download_count += 1
            share.save()
            
            # 创建临时下载URL（或者直接返回文件内容）
            # 这里我们返回一个签名的下载链接
            import tempfile
            import os
            from django.conf import settings
            from django.urls import reverse
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=share.file.file_type)
            temp_file.write(file_content)
            temp_file.close()
            
            # 返回下载链接（实际项目中可能需要更安全的处理方式）
            download_url = request.build_absolute_uri(
                reverse('download_shared_file_temp', kwargs={'share_code': share_code})
            ) + f'?temp_file={os.path.basename(temp_file.name)}'
            
            return Response({
                'download_url': download_url,
                'file_name': share.file.original_name
            })
        else:
            return Response({
                'error': f'文件下载失败: {result}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
    except FileShare.DoesNotExist:
        return Response({
            'error': '分享不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([])  # 公开访问，不需要认证
def download_shared_file_temp(request, share_code):
    """临时下载分享文件"""
    try:
        import tempfile
        import os
        from django.http import HttpResponse, Http404
        
        temp_file_name = request.GET.get('temp_file')
        if not temp_file_name:
            raise Http404('临时文件不存在')
        
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, temp_file_name)
        
        if not os.path.exists(temp_file_path):
            raise Http404('临时文件不存在')
        
        # 获取分享信息
        share = FileShare.objects.get(
            share_code=share_code,
            is_active=True
        )
        
        # 读取文件内容
        with open(temp_file_path, 'rb') as f:
            file_content = f.read()
        
        # 删除临时文件
        os.unlink(temp_file_path)
        
        # 返回文件响应
        response = HttpResponse(
            file_content,
            content_type=share.file.mime_type
        )
        
        response['Content-Disposition'] = f'attachment; filename="{share.file.original_name}"'
        response['Content-Length'] = len(file_content)
        
        return response
        
    except (FileShare.DoesNotExist, FileNotFoundError):
        raise Http404('文件不存在')


@api_view(['GET'])
@permission_classes([])  # 无需认证
def get_share_info(request, share_code):
    """获取分享信息（无需登录）"""
    try:
        share = get_object_or_404(FileShare, share_code=share_code, is_active=True)
        
        # 检查是否过期
        if share.is_expired():
            return Response({
                'error': '分享已过期',
                'is_expired': True
            }, status=status.HTTP_410_GONE)
        
        # 检查是否需要密码
        if share.password:
            password = request.GET.get('password', '')
            if password != share.password:
                return Response({
                    'error': '需要密码'
                }, status=status.HTTP_403_FORBIDDEN)
        
        return Response({
            'file_name': share.file.original_name,
            'file_size': share.file.size,
            'file_type': share.file.file_type,
            'download_count': share.download_count,
            'max_downloads': share.max_downloads,
            'expire_at': share.expire_at,
            'is_expired': share.is_expired(),
            'share_code': share.share_code
        })
        
    except Exception as e:
        return Response({
            'error': '分享不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([])  # 无需认证
def download_shared_file(request, share_code):
    """下载分享的文件（无需登录）"""
    try:
        share = get_object_or_404(FileShare, share_code=share_code, is_active=True)
        
        # 检查是否过期
        if share.is_expired():
            return Response({
                'error': '分享已过期'
            }, status=status.HTTP_410_GONE)
        
        # 检查是否需要密码
        if share.password:
            password = request.data.get('password', '')
            if password != share.password:
                return Response({
                    'error': '密码错误'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # 检查下载次数
        if share.max_downloads and share.download_count >= share.max_downloads:
            return Response({
                'error': '下载次数已达上限'
            }, status=status.HTTP_410_GONE)
        
        # 从Swift下载文件
        success, result = download_file_from_swift(share.file.swift_container, share.file.swift_object)
        
        if success:
            file_content, headers = result
            
            # 更新下载次数
            share.download_count += 1
            share.save()
            
            # 生成临时下载URL
            import tempfile
            import os
            from django.conf import settings
            from django.urls import reverse
            
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(file_content)
            temp_file.close()
            
            # 返回下载URL
            download_url = f'/api/files/share/{share_code}/temp_download/{os.path.basename(temp_file.name)}'
            
            # 将临时文件路径存储到session中
            if not hasattr(request, 'session'):
                from django.contrib.sessions.middleware import SessionMiddleware
                from django.http import HttpRequest
                SessionMiddleware().process_request(request)
                request.session.save()
            
            request.session[f'temp_file_{share_code}'] = temp_file.name
            request.session.save()
            
            return Response({
                'download_url': download_url,
                'file_name': share.file.original_name,
                'file_size': share.file.size
            })
            
        else:
            return Response({
                'error': f'文件下载失败: {result}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
    except Exception as e:
        return Response({
            'error': f'下载过程中发生错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def temp_download_shared_file(request, share_code, filename):
    """临时文件下载"""
    try:
        # 从session获取临时文件路径
        temp_file_path = request.session.get(f'temp_file_{share_code}')
        
        if not temp_file_path or not os.path.exists(temp_file_path):
            return Response({
                'error': '下载链接已过期'
            }, status=status.HTTP_410_GONE)
        
        # 读取文件内容
        with open(temp_file_path, 'rb') as f:
            file_content = f.read()
        
        # 删除临时文件
        os.unlink(temp_file_path)
        
        # 清理session
        if f'temp_file_{share_code}' in request.session:
            del request.session[f'temp_file_{share_code}']
            request.session.save()
        
        # 获取分享信息
        share = get_object_or_404(FileShare, share_code=share_code)
        
        # 创建响应
        if share.file.mime_type.startswith(('image/', 'video/', 'audio/', 'application/')):
            response = HttpResponse(
                file_content,
                content_type=share.file.mime_type
            )
        else:
            response = StreamingHttpResponse(
                file_content,
                content_type=share.file.mime_type
            )
        
        response['Content-Disposition'] = f'attachment; filename="{share.file.original_name}"'
        response['Content-Length'] = share.file.size
        
        return response
        
    except Exception as e:
        return Response({
            'error': f'下载失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def storage_info(request):
    """获取存储信息"""
    user = request.user
    
    def format_bytes(bytes_value):
        """格式化字节数为可读格式"""
        if bytes_value == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    return Response({
        'storage_quota': user.storage_quota,
        'used_storage': user.used_storage,
        'available_storage': user.available_storage,
        'storage_usage_percentage': round(user.storage_usage_percentage, 2),
        'total_files': File.objects.filter(owner=user).count(),
        'total_folders': Folder.objects.filter(owner=user).count(),
        'storage_quota_display': format_bytes(user.storage_quota),
        'used_storage_display': format_bytes(user.used_storage),
        'available_storage_display': format_bytes(user.available_storage)
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
@permission_classes([])  # 无需认证
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
                'error': '分享已过期'
            }, status=status.HTTP_410_GONE)
        
        # 检查是否需要密码
        password = request.GET.get('password', '')
        if share.password and password != share.password:
            return Response({
                'error': '需要密码'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return Response({
            'id': share.id,
            'file_name': share.file.original_name,
            'file_size': share.file.size,
            'file_type': share.file.file_type,
            'download_count': share.download_count,
            'max_downloads': share.max_downloads,
            'expire_at': share.expire_at,
            'created_at': share.created_at,
            'is_expired': share.is_expired()
        })
        
    except FileShare.DoesNotExist:
        return Response({
            'error': '分享不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([])  # 无需认证
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
        
        # 检查密码
        password = request.data.get('password', '')
        if share.password and password != share.password:
            return Response({
                'error': '密码错误'
            }, status=status.HTTP_403_FORBIDDEN)
        
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
        from django.http import HttpResponse
        
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


@api_view(['GET'])
@permission_classes([])  # 无需认证
def download_temp_file(request, filename):
    """下载临时文件"""
    temp_file_key = f'temp_file_{filename}'
    
    if temp_file_key not in request.session:
        return Response({
            'error': '文件不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    
    temp_file_path = request.session[temp_file_key]
    
    try:
        # 读取文件
        with open(temp_file_path, 'rb') as f:
            content = f.read()
        
        # 删除临时文件
        os.unlink(temp_file_path)
        del request.session[temp_file_key]
        
        # 创建响应
        response = HttpResponse(content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{request.GET.get("filename", "download")}"'
        
        return response
        
    except Exception as e:
        return Response({
            'error': f'下载失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                import uuid
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
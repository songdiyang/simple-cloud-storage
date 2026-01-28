"""
下载相关视图
"""
import os
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, StreamingHttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import File, FileShare
from ..utils import download_file_from_swift


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
            
            # 对于二进制文件，使用HttpResponse
            if file_obj.mime_type.startswith(('image/', 'video/', 'audio/', 'application/')):
                response = HttpResponse(
                    file_content,
                    content_type=file_obj.mime_type
                )
            else:
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
            # 更新下载次数
            file_obj.download_count += 1
            file_obj.save()
            
            return Response({
                'download_url': temp_url,
                'filename': file_obj.original_name,
                'size': file_obj.size,
                'method': 'swift'
            })
        else:
            # Swift URL生成失败，返回直接下载API的URL
            direct_download_url = f"/api/files/{file_id}/download/"
            
            return Response({
                'download_url': direct_download_url,
                'filename': file_obj.original_name,
                'size': file_obj.size,
                'method': 'direct',
                'message': 'Swift存储暂时不可用，使用直接下载方式'
            })
            
    except Exception as e:
        return Response({
            'error': f'生成下载链接时发生错误: {str(e)}'
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
@permission_classes([])
def download_shared_file_temp(request, share_code):
    """临时下载分享文件"""
    try:
        import tempfile
        from django.http import Http404
        
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
        from django.http import Http404
        raise Http404('文件不存在')


@api_view(['GET'])
@permission_classes([])
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

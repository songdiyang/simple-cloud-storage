"""
存储信息相关视图
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import File, Folder
from .helpers import format_bytes


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def storage_info(request):
    """获取存储信息"""
    user = request.user
    
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

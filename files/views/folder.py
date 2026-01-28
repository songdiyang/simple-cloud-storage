"""
文件夹相关视图
"""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Folder
from ..serializers import FolderSerializer, CreateFolderSerializer


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

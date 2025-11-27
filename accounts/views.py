from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from .serializers import UserSerializer, RegisterSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def api_status(request):
    """API状态检查"""
    return Response({
        'status': 'online',
        'message': 'API服务正常运行',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """用户注册"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """用户登录"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            })
        else:
            return Response({
                'error': '用户名或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({
            'error': '请提供用户名和密码'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout(request):
    """用户登出"""
    try:
        request.user.auth_token.delete()
        return Response({'message': '登出成功'})
    except:
        return Response({'error': '登出失败'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    """获取/更新用户资料"""
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_avatar(request):
    """上传用户头像"""
    try:
        avatar_file = request.FILES.get('avatar')
        if not avatar_file:
            return Response({'error': '请选择头像文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查文件大小 (限制为2MB)
        if avatar_file.size > 2 * 1024 * 1024:
            return Response({'error': '头像文件大小不能超过2MB'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        file_type = avatar_file.content_type or 'application/octet-stream'
        if file_type not in allowed_types:
            # 通过文件扩展名再次检查
            file_extension = avatar_file.name.lower().split('.')[-1]
            if file_extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                return Response({'error': '只支持 JPG、PNG、GIF、WebP 格式的图片'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 删除旧头像
        if request.user.avatar:
            request.user.avatar.delete(save=False)
        
        # 保存新头像
        request.user.avatar = avatar_file
        request.user.save()
        
        serializer = UserSerializer(request.user)
        return Response({
            'message': '头像上传成功',
            'user': serializer.data
        })
        
    except Exception as e:
        return Response({'error': f'上传失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_avatar(request):
    """删除用户头像"""
    try:
        if request.user.avatar:
            request.user.avatar.delete(save=False)
            request.user.avatar = None
            request.user.save()
        
        serializer = UserSerializer(request.user)
        return Response({
            'message': '头像删除成功',
            'user': serializer.data
        })
        
    except Exception as e:
        return Response({'error': f'删除失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from datetime import timedelta
from .models import User, VIPApplication, LoginRecord, OnlineUser
from .serializers import UserSerializer, RegisterSerializer, VIPApplicationSerializer, VIPApplicationCreateSerializer


# 管理员权限类
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin_user


def get_client_ip(request):
    """获取客户端IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


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
            
            # 记录登录信息
            LoginRecord.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            # 更新在线状态
            OnlineUser.objects.update_or_create(
                user=user,
                defaults={'is_online': True, 'last_activity': timezone.now()}
            )
            
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
        # 更新在线状态
        OnlineUser.objects.filter(user=request.user).update(is_online=False)
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_vip(request):
    """VIP申请 - 提交赞助单号"""
    # 检查是否已经是VIP
    if request.user.is_vip:
        return Response({
            'error': '您已经是VIP用户了'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 检查是否有待审核的申请
    pending_application = VIPApplication.objects.filter(
        user=request.user,
        status=VIPApplication.STATUS_PENDING
    ).first()
    
    if pending_application:
        return Response({
            'error': '您已有待审核的VIP申请，请耐心等待',
            'application': VIPApplicationSerializer(pending_application).data
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = VIPApplicationCreateSerializer(data=request.data)
    if serializer.is_valid():
        application = VIPApplication.objects.create(
            user=request.user,
            order_number=serializer.validated_data['order_number']
        )
        return Response({
            'message': '感谢您的支持！管理员审核后将为您扩容存储空间',
            'application': VIPApplicationSerializer(application).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_vip_applications(request):
    """获取我的VIP申请列表"""
    applications = VIPApplication.objects.filter(user=request.user)
    serializer = VIPApplicationSerializer(applications, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vip_status(request):
    """获取VIP状态"""
    pending_application = VIPApplication.objects.filter(
        user=request.user,
        status=VIPApplication.STATUS_PENDING
    ).first()
    
    return Response({
        'is_vip': request.user.is_vip,
        'role': request.user.role,
        'role_display': request.user.get_role_display(),
        'storage_quota': request.user.storage_quota,
        'has_pending_application': pending_application is not None,
        'pending_application': VIPApplicationSerializer(pending_application).data if pending_application else None
    })


# ==================== 管理员 API ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_check(request):
    """检查当前用户是否为管理员"""
    return Response({
        'is_admin': request.user.is_admin_user,
        'role': request.user.role
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard(request):
    """管理员仪表盘 - 系统统计"""
    now = timezone.now()
    today = now.date()
    
    # 用户统计
    total_users = User.objects.count()
    vip_users = User.objects.filter(role=User.ROLE_VIP).count()
    admin_users = User.objects.filter(role=User.ROLE_ADMIN).count()
    today_new_users = User.objects.filter(date_joined__date=today).count()
    
    # 在线用户（5分钟内有活动视为在线）
    online_threshold = now - timedelta(minutes=5)
    online_count = OnlineUser.objects.filter(
        is_online=True,
        last_activity__gte=online_threshold
    ).count()
    
    # 存储统计
    storage_stats = User.objects.aggregate(
        total_quota=Sum('storage_quota'),
        total_used=Sum('used_storage')
    )
    
    # VIP 申请统计
    pending_applications = VIPApplication.objects.filter(status=VIPApplication.STATUS_PENDING).count()
    
    # 最近 7 天登录趋势
    week_ago = today - timedelta(days=7)
    login_trend = LoginRecord.objects.filter(
        login_time__date__gte=week_ago
    ).annotate(
        date=TruncDate('login_time')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # 最近 7 天新用户趋势
    register_trend = User.objects.filter(
        date_joined__date__gte=week_ago
    ).annotate(
        date=TruncDate('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    return Response({
        'user_stats': {
            'total': total_users,
            'vip': vip_users,
            'admin': admin_users,
            'normal': total_users - vip_users - admin_users,
            'today_new': today_new_users,
            'online': online_count
        },
        'storage_stats': {
            'total_quota': storage_stats['total_quota'] or 0,
            'total_used': storage_stats['total_used'] or 0
        },
        'pending_vip_applications': pending_applications,
        'login_trend': list(login_trend),
        'register_trend': list(register_trend)
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users(request):
    """管理员 - 用户列表"""
    users = User.objects.all().order_by('-date_joined')
    
    # 简单搜索
    search = request.GET.get('search', '')
    if search:
        users = users.filter(username__icontains=search)
    
    # 角色筛选
    role = request.GET.get('role', '')
    if role:
        users = users.filter(role=role)
    
    data = []
    for user in users:
        # 获取在线状态
        online_status = getattr(user, 'online_status', None)
        is_online = False
        if online_status:
            online_threshold = timezone.now() - timedelta(minutes=5)
            is_online = online_status.is_online and online_status.last_activity >= online_threshold
        
        # 获取最后登录
        last_login_record = user.login_records.first()
        
        data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'role_display': user.get_role_display(),
            'storage_quota': user.storage_quota,
            'used_storage': user.used_storage,
            'storage_usage_percentage': user.storage_usage_percentage,
            'is_active': user.is_active,
            'is_online': is_online,
            'date_joined': user.date_joined,
            'last_login': last_login_record.login_time if last_login_record else None
        })
    
    return Response(data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def admin_update_user(request, user_id):
    """管理员 - 更新用户信息"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    # 不能修改自己
    if user.id == request.user.id:
        return Response({'error': '不能修改自己的权限'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 更新角色
    new_role = request.data.get('role')
    if new_role and new_role in [User.ROLE_USER, User.ROLE_VIP, User.ROLE_ADMIN]:
        old_role = user.role
        user.role = new_role
        
        # 如果升级为 VIP，自动扩容
        if new_role == User.ROLE_VIP and old_role != User.ROLE_VIP:
            user.storage_quota = User.STORAGE_VIP
        # 如果降级为普通用户，可选择是否调整配额
    
    # 更新存储配额
    new_quota = request.data.get('storage_quota')
    if new_quota is not None:
        user.storage_quota = int(new_quota)
    
    # 更新活动状态
    is_active = request.data.get('is_active')
    if is_active is not None:
        user.is_active = is_active
    
    user.save()
    
    return Response({
        'message': '用户信息更新成功',
        'user': {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'role_display': user.get_role_display(),
            'storage_quota': user.storage_quota,
            'is_active': user.is_active
        }
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_vip_applications(request):
    """管理员 - VIP申请列表"""
    status_filter = request.GET.get('status', '')
    
    applications = VIPApplication.objects.select_related('user', 'reviewed_by').all()
    
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    data = []
    for app in applications:
        data.append({
            'id': str(app.id),
            'username': app.user.username,
            'user_id': app.user.id,
            'order_number': app.order_number,
            'status': app.status,
            'status_display': app.get_status_display(),
            'admin_note': app.admin_note,
            'created_at': app.created_at,
            'reviewed_at': app.reviewed_at,
            'reviewed_by': app.reviewed_by.username if app.reviewed_by else None
        })
    
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_review_vip(request, application_id):
    """管理员 - 审核VIP申请"""
    try:
        application = VIPApplication.objects.get(id=application_id)
    except VIPApplication.DoesNotExist:
        return Response({'error': '申请不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    if application.status != VIPApplication.STATUS_PENDING:
        return Response({'error': '该申请已被处理'}, status=status.HTTP_400_BAD_REQUEST)
    
    action = request.data.get('action')  # 'approve' or 'reject'
    admin_note = request.data.get('admin_note', '')
    
    if action == 'approve':
        application.status = VIPApplication.STATUS_APPROVED
        # 升级用户为 VIP
        user = application.user
        user.role = User.ROLE_VIP
        user.storage_quota = User.STORAGE_VIP
        user.save()
        message = 'VIP申请已通过，用户已升级'
    elif action == 'reject':
        application.status = VIPApplication.STATUS_REJECTED
        message = 'VIP申请已拒绝'
    else:
        return Response({'error': '无效的操作'}, status=status.HTTP_400_BAD_REQUEST)
    
    application.admin_note = admin_note
    application.reviewed_at = timezone.now()
    application.reviewed_by = request.user
    application.save()
    
    return Response({'message': message})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_login_records(request):
    """管理员 - 登录记录"""
    records = LoginRecord.objects.select_related('user').all()[:100]
    
    data = []
    for record in records:
        data.append({
            'id': record.id,
            'username': record.user.username,
            'login_time': record.login_time,
            'ip_address': record.ip_address
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_online_users(request):
    """管理员 - 在线用户列表"""
    online_threshold = timezone.now() - timedelta(minutes=5)
    online_users = OnlineUser.objects.filter(
        is_online=True,
        last_activity__gte=online_threshold
    ).select_related('user')
    
    data = []
    for online in online_users:
        data.append({
            'username': online.user.username,
            'role': online.user.role,
            'role_display': online.user.get_role_display(),
            'last_activity': online.last_activity
        })
    
    return Response(data)
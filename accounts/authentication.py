"""
自定义令牌认证类 - 支持令牌过期和角色差异化过期时间
"""
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed


class ExpiringTokenAuthentication(TokenAuthentication):
    """
    支持过期的令牌认证
    
    管理员令牌过期时间较短（安全性优先）
    普通用户令牌过期时间较长（用户体验优先）
    """
    
    def authenticate_credentials(self, key):
        """验证令牌，检查是否过期"""
        try:
            token = Token.objects.select_related('user').get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed('无效的令牌')
        
        if not token.user.is_active:
            raise AuthenticationFailed('用户已被禁用')
        
        # 检查令牌是否过期
        if self.is_token_expired(token):
            token.delete()  # 删除过期令牌
            raise AuthenticationFailed('令牌已过期，请重新登录')
        
        return (token.user, token)
    
    def is_token_expired(self, token):
        """
        检查令牌是否过期
        根据用户角色返回不同的过期时间
        """
        user = token.user
        
        # 获取配置的过期时间
        token_config = getattr(settings, 'TOKEN_EXPIRE_CONFIG', {})
        
        # 判断用户类型并获取对应的过期时间（秒）
        if user.is_superuser or (hasattr(user, 'is_admin_user') and user.is_admin_user):
            # 管理员：默认2小时
            expire_seconds = token_config.get('ADMIN_TOKEN_EXPIRE_SECONDS', 2 * 60 * 60)
        else:
            # 普通用户：默认7天
            expire_seconds = token_config.get('USER_TOKEN_EXPIRE_SECONDS', 7 * 24 * 60 * 60)
        
        # 计算过期时间
        expire_time = token.created + timedelta(seconds=expire_seconds)
        
        return timezone.now() > expire_time
    
    @staticmethod
    def get_token_expire_info(user):
        """
        获取用户的令牌过期信息
        用于登录时返回给前端
        """
        token_config = getattr(settings, 'TOKEN_EXPIRE_CONFIG', {})
        
        if user.is_superuser or (hasattr(user, 'is_admin_user') and user.is_admin_user):
            expire_seconds = token_config.get('ADMIN_TOKEN_EXPIRE_SECONDS', 2 * 60 * 60)
            expire_label = '2小时'
        else:
            expire_seconds = token_config.get('USER_TOKEN_EXPIRE_SECONDS', 7 * 24 * 60 * 60)
            expire_label = '7天'
        
        return {
            'expire_seconds': expire_seconds,
            'expire_label': expire_label,
            'expire_at': (timezone.now() + timedelta(seconds=expire_seconds)).isoformat()
        }


def refresh_token(user):
    """
    刷新用户令牌
    删除旧令牌并创建新令牌
    """
    # 删除现有令牌
    Token.objects.filter(user=user).delete()
    # 创建新令牌
    token = Token.objects.create(user=user)
    return token

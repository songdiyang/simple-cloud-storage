"""
视图辅助函数模块
"""
from django.conf import settings
from django.core.cache import cache


def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_password_attempt_key(share_code, ip):
    """生成密码尝试缓存键"""
    return f'password_attempt_{share_code}_{ip}'


def check_password_attempts(share_code, request):
    """检查密码尝试次数，返回 (is_locked, attempts, remaining, lockout_time)"""
    ip = get_client_ip(request)
    cache_key = get_password_attempt_key(share_code, ip)
    
    max_attempts = getattr(settings, 'PASSWORD_MAX_ATTEMPTS', 3)
    lockout_time = getattr(settings, 'PASSWORD_LOCKOUT_TIME', 300)
    
    attempts = cache.get(cache_key, 0)
    remaining = max_attempts - attempts
    is_locked = attempts >= max_attempts
    
    return is_locked, attempts, remaining, lockout_time


def record_failed_attempt(share_code, request):
    """记录失败的密码尝试"""
    ip = get_client_ip(request)
    cache_key = get_password_attempt_key(share_code, ip)
    
    lockout_time = getattr(settings, 'PASSWORD_LOCKOUT_TIME', 300)
    
    attempts = cache.get(cache_key, 0)
    cache.set(cache_key, attempts + 1, lockout_time)
    
    return attempts + 1


def clear_password_attempts(share_code, request):
    """清除密码尝试记录（密码正确时调用）"""
    ip = get_client_ip(request)
    cache_key = get_password_attempt_key(share_code, ip)
    cache.delete(cache_key)


def format_bytes(bytes_value):
    """格式化字节数为可读格式"""
    if bytes_value == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

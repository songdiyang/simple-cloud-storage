"""
Files 应用服务层模块

提供存储服务的统一接口：
- swift_service: Swift 对象存储服务
- local_service: 本地文件存储服务
"""

from .swift_service import SwiftStorageService
from .local_service import LocalStorageService

__all__ = [
    'SwiftStorageService',
    'LocalStorageService',
]

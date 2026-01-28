"""
Files 应用视图模块

按功能拆分为多个子模块：
- folder: 文件夹操作
- file: 文件基础操作（上传、列表、详情、删除）
- download: 下载相关
- share: 分享相关
- trash: 回收站
- storage: 存储信息
"""

from .folder import (
    folder_list,
    create_folder,
    delete_folder,
)

from .file import (
    file_list,
    file_detail,
    upload_file,
    delete_file,
)

from .download import (
    download_file,
    get_download_url,
    temp_download_shared_file,
    download_shared_file_temp,
    download_temp_file,
)

from .share import (
    create_share,
    my_shares,
    deleted_shares,
    delete_share,
    get_share_info,
    verify_share_password,
    download_shared_file,
    save_shared_file,
)

from .trash import (
    trash_list,
    trash_stats,
    restore_file,
    permanent_delete_file,
    empty_trash,
)

from .storage import (
    storage_info,
)

__all__ = [
    # 文件夹
    'folder_list',
    'create_folder',
    'delete_folder',
    # 文件
    'file_list',
    'file_detail',
    'upload_file',
    'delete_file',
    # 下载
    'download_file',
    'get_download_url',
    'temp_download_shared_file',
    'download_shared_file_temp',
    'download_temp_file',
    # 分享
    'create_share',
    'my_shares',
    'deleted_shares',
    'delete_share',
    'get_share_info',
    'verify_share_password',
    'download_shared_file',
    'save_shared_file',
    # 回收站
    'trash_list',
    'trash_stats',
    'restore_file',
    'permanent_delete_file',
    'empty_trash',
    # 存储
    'storage_info',
]

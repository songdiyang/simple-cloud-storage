from django.urls import path
from .views import (
    # 文件夹
    folder_list, create_folder, delete_folder,
    # 文件
    file_list, file_detail, upload_file, delete_file,
    # 下载
    download_file, get_download_url, temp_download_shared_file,
    download_shared_file_temp, download_temp_file,
    # 分享
    create_share, my_shares, deleted_shares, delete_share,
    get_share_info, verify_share_password, download_shared_file, save_shared_file,
    # 回收站
    trash_list, trash_stats, restore_file, permanent_delete_file, empty_trash,
    # 存储
    storage_info,
)

urlpatterns = [
    # 文件夹相关
    path('folders/', folder_list, name='folder_list'),
    path('folders/create/', create_folder, name='create_folder'),
    path('folders/<uuid:folder_id>/delete/', delete_folder, name='delete_folder'),
    
    # 文件相关
    path('', file_list, name='file_list'),
    path('upload/', upload_file, name='upload_file'),
    path('<uuid:file_id>/', file_detail, name='file_detail'),
    path('<uuid:file_id>/delete/', delete_file, name='delete_file'),
    path('<uuid:file_id>/download/', download_file, name='download_file'),
    path('<uuid:file_id>/download-url/', get_download_url, name='get_download_url'),
    
    # 回收站相关
    path('trash/', trash_list, name='trash_list'),
    path('trash/stats/', trash_stats, name='trash_stats'),
    path('trash/empty/', empty_trash, name='empty_trash'),
    path('trash/<uuid:file_id>/restore/', restore_file, name='restore_file'),
    path('trash/<uuid:file_id>/delete/', permanent_delete_file, name='permanent_delete_file'),
    
    # 分享相关
    path('<uuid:file_id>/share/', create_share, name='create_share'),
    path('shares/', my_shares, name='my_shares'),
    path('shares/deleted/', deleted_shares, name='deleted_shares'),
    path('shares/<uuid:share_id>/delete/', delete_share, name='delete_share'),
    path('save-shared-file/', save_shared_file, name='save_shared_file'),
    # 公开分享访问
    path('share/<str:share_code>/', get_share_info, name='get_share_info'),
    path('share/<str:share_code>/verify-password/', verify_share_password, name='verify_share_password'),
    path('share/<str:share_code>/download/', download_shared_file, name='download_shared_file'),
    path('share/<str:share_code>/temp_download/<str:filename>/', temp_download_shared_file, name='temp_download_shared_file'),
    path('share/<str:share_code>/temp/', download_shared_file_temp, name='download_shared_file_temp'),
    
    # 存储信息
    path('storage/', storage_info, name='storage_info'),
]
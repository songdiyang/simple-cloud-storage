from django.urls import path
from . import views

urlpatterns = [
    # 文件夹相关
    path('folders/', views.folder_list, name='folder_list'),
    path('folders/create/', views.create_folder, name='create_folder'),
    path('folders/<uuid:folder_id>/delete/', views.delete_folder, name='delete_folder'),
    
    # 文件相关
    path('', views.file_list, name='file_list'),
    path('upload/', views.upload_file, name='upload_file'),
    path('<uuid:file_id>/', views.file_detail, name='file_detail'),
    path('<uuid:file_id>/delete/', views.delete_file, name='delete_file'),
    path('<uuid:file_id>/download/', views.download_file, name='download_file'),
    path('<uuid:file_id>/download-url/', views.get_download_url, name='get_download_url'),
    
    # 分享相关
    path('<uuid:file_id>/share/', views.create_share, name='create_share'),
    path('shares/', views.my_shares, name='my_shares'),
    path('shares/deleted/', views.deleted_shares, name='deleted_shares'),
    path('shares/<uuid:share_id>/delete/', views.delete_share, name='delete_share'),
    path('save-shared-file/', views.save_shared_file, name='save_shared_file'),
    # 公开分享访问
    path('share/<str:share_code>/', views.get_share_info, name='get_share_info'),
    path('share/<str:share_code>/download/', views.download_shared_file, name='download_shared_file'),
    path('share/<str:share_code>/temp_download/<str:filename>/', views.temp_download_shared_file, name='temp_download_shared_file'),
    path('share/<str:share_code>/temp/', views.download_shared_file_temp, name='download_shared_file_temp'),
    
    # 存储信息
    path('storage/', views.storage_info, name='storage_info'),
]
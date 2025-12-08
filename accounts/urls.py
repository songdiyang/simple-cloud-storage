from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_status, name='api_status'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('change-username/', views.change_username, name='change_username'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('delete-avatar/', views.delete_avatar, name='delete_avatar'),
    # VIP相关
    path('vip/apply/', views.apply_vip, name='apply_vip'),
    path('vip/status/', views.vip_status, name='vip_status'),
    path('vip/applications/', views.my_vip_applications, name='my_vip_applications'),
    # 管理员 API
    path('admin/check/', views.admin_check, name='admin_check'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/', views.admin_update_user, name='admin_update_user'),
    path('admin/vip-applications/', views.admin_vip_applications, name='admin_vip_applications'),
    path('admin/vip-applications/<str:application_id>/review/', views.admin_review_vip, name='admin_review_vip'),
    path('admin/login-records/', views.admin_login_records, name='admin_login_records'),
    path('admin/online-users/', views.admin_online_users, name='admin_online_users'),
]
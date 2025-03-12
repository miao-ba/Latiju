from django.urls import path
from Main import views

app_name = 'Main'  # 添加這一行
urlpatterns = [
    path('login/', views.view_login, name='login'),
    path('logout/', views.view_logout, name='logout'),
    path('register/', views.view_account_register, name='register'),
    path('manage/', views.view_account_manage_list, name='manage'),
    path('manage/<str:account_id>/', views.view_account_manage_info, name='manage_info'),
    path('delete/<str:username>/', views.delete_account, name='delete_account'),
    path('', views.view_account_manage_list, name='index'),
]

from django.urls import path
from . import views

app_name = 'waste_transport'

urlpatterns = [
    # 聯單清單
    path('', views.manifest_list, name='manifest_list'),
    
    # 聯單詳情 - AJAX
    path('disposal/<str:manifest_id>/<str:waste_id>', views.disposal_manifest_detail, name='disposal_manifest_detail'),
    path('reuse/<str:manifest_id>/<str:waste_id>', views.reuse_manifest_detail, name='reuse_manifest_detail'),
    
    # CSV匯入與匯出 - AJAX
    path('import/', views.import_csv, name='import_csv'),
    path('export/', views.export_manifests_csv, name='export_csv'),
    
    # 衝突解決處理 - AJAX
    path('resolve_conflicts/', views.handle_conflict_resolution, name='resolve_conflicts'),
]
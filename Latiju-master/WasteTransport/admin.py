from django.contrib import admin
from .models import (
    Company, Process, WasteSubstance, Carrier, Processor, Reuser, Vehicle,
    Manifest, Report, Transport, Processing, Recycling,
    DisposalManifestData, ReuseManifestData, ImportHistory
)

# 基礎實體類別的管理界面
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """事業機構管理界面"""
    list_display = ('company_id', 'company_name', 'company_type', 'company_contact', 'company_phone')
    search_fields = ('company_id', 'company_name', 'company_contact')
    list_filter = ('company_type',)

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    """製程管理界面"""
    list_display = ('process_code', 'process_name')
    search_fields = ('process_code', 'process_name')

@admin.register(WasteSubstance)
class WasteSubstanceAdmin(admin.ModelAdmin):
    """廢棄物/物質管理界面"""
    list_display = ('substance_id', 'substance_code', 'substance_name', 'substance_type')
    search_fields = ('substance_code', 'substance_name')
    list_filter = ('substance_type',)

@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    """清除者管理界面"""
    list_display = ('carrier_id', 'carrier_name', 'carrier_contact', 'carrier_phone')
    search_fields = ('carrier_id', 'carrier_name', 'carrier_contact')

@admin.register(Processor)
class ProcessorAdmin(admin.ModelAdmin):
    """處理者管理界面"""
    list_display = ('processor_id', 'processor_name', 'processor_contact', 'processor_phone')
    search_fields = ('processor_id', 'processor_name', 'processor_contact')

@admin.register(Reuser)
class ReuserAdmin(admin.ModelAdmin):
    """再利用者管理界面"""
    list_display = ('reuser_id', 'reuser_name', 'reuser_nature', 'reuser_contact', 'reuser_phone')
    search_fields = ('reuser_id', 'reuser_name', 'reuser_contact')
    list_filter = ('reuser_nature',)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """車輛管理界面"""
    list_display = ('vehicle_id', 'vehicle_type', 'vehicle_capacity', 'vehicle_owner_id', 'owner_type')
    search_fields = ('vehicle_id', 'vehicle_owner_id')
    list_filter = ('owner_type', 'vehicle_type')

# 聯單相關管理界面
class ReportInline(admin.StackedInline):
    """申報單內聯顯示"""
    model = Report
    can_delete = False
    verbose_name = '申報單'
    verbose_name_plural = '申報單'

class TransportInline(admin.StackedInline):
    """清運單內聯顯示"""
    model = Transport
    can_delete = False
    verbose_name = '清運單'
    verbose_name_plural = '清運單'

class ProcessingInline(admin.StackedInline):
    """處理單內聯顯示"""
    model = Processing
    can_delete = False
    verbose_name = '處理單'
    verbose_name_plural = '處理單'
    
class RecyclingInline(admin.StackedInline):
    """回收單內聯顯示"""
    model = Recycling
    can_delete = False
    verbose_name = '回收單'
    verbose_name_plural = '回收單'

class DisposalManifestDataInline(admin.StackedInline):
    """清除單內聯顯示"""
    model = DisposalManifestData
    can_delete = False
    verbose_name = '清除單資料'
    verbose_name_plural = '清除單資料'

class ReuseManifestDataInline(admin.StackedInline):
    """再利用單內聯顯示"""
    model = ReuseManifestData
    can_delete = False
    verbose_name = '再利用單資料'
    verbose_name_plural = '再利用單資料'

@admin.register(Manifest)
class ManifestAdmin(admin.ModelAdmin):
    """聯單基本資訊管理界面"""
    list_display = ('manifest_id', 'waste_id', 'company', 'manifest_type', 'manifest_confirmation', 'is_visible', 'created_at')
    search_fields = ('manifest_id', 'waste_id', 'company__company_name')
    list_filter = ('manifest_type', 'manifest_confirmation', 'is_visible', 'created_at')
    date_hierarchy = 'created_at'
    inlines = []
    
    def get_inlines(self, request, obj=None):
        """根據聯單類型動態顯示相關內聯"""
        if obj is None:
            return [ReportInline]
            
        inlines = [ReportInline, TransportInline]
        
        # 根據聯單類型添加不同的內聯
        if obj.manifest_type == 'disposal':
            inlines.extend([DisposalManifestDataInline, ProcessingInline])
        else:  # 再利用單
            inlines.extend([ReuseManifestDataInline, RecyclingInline])
            
        return inlines

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """申報單管理界面"""
    list_display = ('report_id', 'manifest', 'report_date', 'reported_weight')
    search_fields = ('manifest__manifest_id',)
    list_filter = ('report_date',)
    date_hierarchy = 'report_date'

@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    """清運單管理界面"""
    list_display = ('transport_id', 'manifest', 'carrier', 'delivery_date', 'carrier_confirmation')
    search_fields = ('manifest__manifest_id', 'carrier__carrier_name')
    list_filter = ('carrier_confirmation', 'delivery_date')
    date_hierarchy = 'delivery_date'

@admin.register(Processing)
class ProcessingAdmin(admin.ModelAdmin):
    """處理單管理界面"""
    list_display = ('processing_id', 'manifest', 'processor', 'receive_date', 'processor_confirmation')
    search_fields = ('manifest__manifest_id', 'processor__processor_name')
    list_filter = ('processor_confirmation', 'receive_date')
    date_hierarchy = 'receive_date'

@admin.register(Recycling)
class RecyclingAdmin(admin.ModelAdmin):
    """回收單管理界面"""
    list_display = ('recycling_id', 'manifest', 'reuser', 'recovery_date', 'reuser_confirmation')
    search_fields = ('manifest__manifest_id', 'reuser__reuser_name')
    list_filter = ('reuser_confirmation', 'recovery_date')
    date_hierarchy = 'recovery_date'

@admin.register(ImportHistory)
class ImportHistoryAdmin(admin.ModelAdmin):
    """匯入歷史記錄管理界面"""
    list_display = ('filename', 'import_date', 'import_type', 'total_records', 'imported_records', 'skipped_records')
    list_filter = ('import_date', 'import_type')
    search_fields = ('filename',)
    date_hierarchy = 'import_date'
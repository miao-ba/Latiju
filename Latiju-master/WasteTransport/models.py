from django.db import models
from django.core.validators import RegexValidator

class BaseManifest(models.Model):
    """廢棄物清運聯單的基本模型"""
    manifest_id = models.CharField(max_length=17,  verbose_name="聯單編號")
    company_id = models.CharField(max_length=10, verbose_name="事業機構代碼")
    company_name = models.CharField(max_length=100, verbose_name="事業機構名稱")
    report_date = models.DateField(verbose_name="申報日期")
    report_time = models.TimeField(verbose_name="申報時間")
    transport_date = models.DateField(null=True, blank=True, verbose_name="清運日期")
    transport_time = models.TimeField(null=True, blank=True, verbose_name="清運時間")
    waste_code = models.CharField(max_length=10, verbose_name="廢棄物代碼")
    waste_name = models.CharField(max_length=100, verbose_name="廢棄物名稱")
    waste_id = models.CharField(max_length=10, verbose_name="廢棄物ID")
    reported_weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="申報重量")
    process_code = models.CharField(max_length=10, verbose_name="製程代碼")
    process_name = models.CharField(max_length=100, verbose_name="製程名稱")
    from_storage = models.BooleanField(default=False, verbose_name="是否由貯存地起運")
    origin_location = models.CharField(max_length=100, null=True, blank=True, verbose_name="起運地")
    manifest_confirmation = models.BooleanField(default=False, verbose_name="聯單確認")
    carrier_vehicle = models.CharField(max_length=20, null=True, blank=True, verbose_name="運載車號")
    carrier_confirmation = models.BooleanField(default=False, verbose_name="清除者確認")

    # 共有欄位但名稱不同的欄位
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    
    class Meta:
        abstract = True

class DisposalManifest(BaseManifest):
    """廢棄物清除聯單模型"""
    
    # 清除單特有欄位
    carrier_id = models.CharField(max_length=10, verbose_name="清除者代碼")
    carrier_name = models.CharField(max_length=100, verbose_name="清除者名稱")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="運送日期")
    delivery_time = models.TimeField(null=True, blank=True, verbose_name="運送時間")
    carrier_vehicle_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="清除者運載車號")
    
    # 處理者相關欄位
    processor_id = models.CharField(max_length=10, verbose_name="處理者代碼")
    processor_name = models.CharField(max_length=100, verbose_name="處理者名稱")
    receive_date = models.DateField(null=True, blank=True, verbose_name="收受日期")
    receive_time = models.TimeField(null=True, blank=True, verbose_name="收受時間")
    intermediate_treatment = models.CharField(max_length=50, null=True, blank=True, verbose_name="中間處理方式")
    processing_completion_date = models.DateField(null=True, blank=True, verbose_name="處理完成日期")
    processing_completion_time = models.TimeField(null=True, blank=True, verbose_name="處理完成時間")
    final_disposal_method = models.CharField(max_length=50, null=True, blank=True, verbose_name="最終處置方式")
    processor_confirmation = models.BooleanField(default=False, verbose_name="處理者確認")
    processor_vehicle = models.CharField(max_length=20, null=True, blank=True, verbose_name="處理者運載車號")
    
    # 最終處置者相關欄位
    final_processor_id = models.CharField(max_length=10, null=True, blank=True, verbose_name="最終處置者代碼")
    final_processor_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="最終處置者名稱")
    entry_date = models.DateField(null=True, blank=True, verbose_name="進場日期")
    entry_time = models.TimeField(null=True, blank=True, verbose_name="進場時間")
    entry_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="進場編號")
    final_processor_confirmation = models.BooleanField(default=False, verbose_name="最終處置者確認")
    final_destination = models.CharField(max_length=50, null=True, blank=True, verbose_name="最終流向")
    
    class Meta:
        verbose_name = "清除聯單"
        verbose_name_plural = "清除聯單"
        
    def __str__(self):
        return f"清除聯單 {self.manifest_id} - {self.company_name}"

class ReuseManifest(BaseManifest):
    """廢棄物再利用聯單模型"""
    
    # 再利用單特有欄位
    reuse_purpose = models.CharField(max_length=50, null=True, blank=True, verbose_name="再利用用途")
    reuse_purpose_description = models.CharField(max_length=100, null=True, blank=True, verbose_name="再利用用途說明")
    reuse_method = models.CharField(max_length=50, null=True, blank=True, verbose_name="再利用方式")
    
    # 清除者相關欄位
    carrier_id = models.CharField(max_length=10, null=True, blank=True, verbose_name="清除者代碼")
    carrier_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="清除者名稱")
    other_carrier = models.CharField(max_length=100, null=True, blank=True, verbose_name="其它清除者")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="運送日期")
    delivery_time = models.TimeField(null=True, blank=True, verbose_name="運送時間")
    carrier_vehicle_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="清除者實際運載車號")
    carrier_rejection_reason = models.CharField(max_length=200, null=True, blank=True, verbose_name="清除者不接受原因")
    
    # 再利用者相關欄位
    reuser_id = models.CharField(max_length=10, null=True, blank=True, verbose_name="再利用者代碼")
    reuser_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="再利用者名稱")
    other_reuser = models.CharField(max_length=100, null=True, blank=True, verbose_name="其它再利用者")
    reuser_nature = models.CharField(max_length=50, null=True, blank=True, verbose_name="再利用者性質")
    recovery_date = models.DateField(null=True, blank=True, verbose_name="回收日期")
    recovery_time = models.TimeField(null=True, blank=True, verbose_name="回收時間")
    reuse_completion_time = models.DateTimeField(null=True, blank=True, verbose_name="再利用完成時間")
    reuser_confirmation = models.BooleanField(default=False, verbose_name="再利用者是否確認")
    reuser_vehicle = models.CharField(max_length=20, null=True, blank=True, verbose_name="再利用者實際運載車號")
    reuser_rejection_reason = models.CharField(max_length=200, null=True, blank=True, verbose_name="再利用者不接受原因")
    source_confirmed = models.BooleanField(default=False, verbose_name="產源是否已確認申報聯單內容")
    
    # 物質相關欄位，覆蓋基本模型中的廢棄物欄位，更改名稱
    substance_code = models.CharField(max_length=10, verbose_name="物質代碼")
    substance_name = models.CharField(max_length=100, verbose_name="物質名稱")
    
    class Meta:
        verbose_name = "再利用聯單"
        verbose_name_plural = "再利用聯單"
        
    def __str__(self):
        return f"再利用聯單 {self.manifest_id} - {self.company_name}"

# 匯入歷史記錄
class ImportHistory(models.Model):
    """CSV匯入歷史記錄"""
    filename = models.CharField(max_length=255, verbose_name="檔案名稱")
    import_date = models.DateTimeField(auto_now_add=True, verbose_name="匯入日期")
    import_type = models.CharField(max_length=20, choices=[('disposal', '清除單'), ('reuse', '再利用單')], verbose_name="匯入類型")
    total_records = models.IntegerField(default=0, verbose_name="總記錄數")
    imported_records = models.IntegerField(default=0, verbose_name="已匯入記錄數")
    skipped_records = models.IntegerField(default=0, verbose_name="略過記錄數")
    
    class Meta:
        verbose_name = "匯入歷史記錄"
        verbose_name_plural = "匯入歷史記錄"
        
    def __str__(self):
        return f"{self.filename} ({self.import_date.strftime('%Y-%m-%d %H:%M')})"
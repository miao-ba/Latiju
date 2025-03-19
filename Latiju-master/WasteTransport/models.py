from django.db import models

# 事業單位表
class Company(models.Model):
    """事業機構資料表，儲存所有事業單位的基本資訊"""
    company_id = models.CharField(max_length=10, primary_key=True, verbose_name="事業機構代碼")
    company_name = models.CharField(max_length=100, verbose_name="事業機構名稱")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "事業機構"
        verbose_name_plural = "事業機構"

    def __str__(self):
        return f"{self.company_id} - {self.company_name}"

# 製程表
class Process(models.Model):
    """製程資料表，儲存所有製程相關資訊"""
    process_code = models.CharField(max_length=10, primary_key=True, verbose_name="製程代碼")
    process_name = models.CharField(max_length=100, verbose_name="製程名稱")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "製程"
        verbose_name_plural = "製程"

    def __str__(self):
        return f"{self.process_code} - {self.process_name}"

# 廢棄物/物質表
class WasteSubstance(models.Model):
    """廢棄物/物質資料表，儲存清除單中的廢棄物及再利用單中的物質資訊"""
    SUBSTANCE_TYPES = [
        ('waste', '廢棄物'),
        ('reuse', '再利用物質'),
    ]
    
    substance_id = models.AutoField(primary_key=True, verbose_name="物質ID")
    substance_code = models.CharField(max_length=10, verbose_name="物質代碼")
    substance_name = models.CharField(max_length=100, verbose_name="物質名稱")
    substance_type = models.CharField(max_length=10, choices=SUBSTANCE_TYPES, verbose_name="物質類型")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "廢棄物/物質"
        verbose_name_plural = "廢棄物/物質"
        unique_together = ('substance_code', 'substance_type')

    def __str__(self):
        return f"{self.substance_code} - {self.substance_name}"

# 清除者表
class Carrier(models.Model):
    """清除者資料表，儲存所有清除者資訊"""
    carrier_id = models.CharField(max_length=10, primary_key=True, verbose_name="清除者代碼")
    carrier_name = models.CharField(max_length=100, verbose_name="清除者名稱")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "清除者"
        verbose_name_plural = "清除者"

    def __str__(self):
        return f"{self.carrier_id} - {self.carrier_name}"

# 處理者表
class Processor(models.Model):
    """處理者資料表，儲存所有處理者資訊"""
    processor_id = models.CharField(max_length=10, primary_key=True, verbose_name="處理者代碼")
    processor_name = models.CharField(max_length=100, verbose_name="處理者名稱")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "處理者"
        verbose_name_plural = "處理者"

    def __str__(self):
        return f"{self.processor_id} - {self.processor_name}"

# 再利用者表
class Reuser(models.Model):
    """再利用者資料表，儲存所有再利用者資訊"""
    reuser_id = models.CharField(max_length=10, primary_key=True, verbose_name="再利用者代碼")
    reuser_name = models.CharField(max_length=100, verbose_name="再利用者名稱")
    reuser_nature = models.CharField(max_length=50, null=True, blank=True, verbose_name="再利用者性質")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "再利用者"
        verbose_name_plural = "再利用者"

    def __str__(self):
        return f"{self.reuser_id} - {self.reuser_name}"

# 車輛表
class Vehicle(models.Model):
    """車輛資料表，儲存所有運輸車輛資訊"""
    OWNER_TYPES = [
        ('carrier', '清除者'),
        ('processor', '處理者'),
        ('reuser', '再利用者'),
    ]
    
    vehicle_id = models.CharField(max_length=20, primary_key=True, verbose_name="車輛編號")
    vehicle_type = models.CharField(max_length=50, null=True, blank=True, verbose_name="車輛類型")
    vehicle_capacity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="載重量(公噸)")
    vehicle_owner_id = models.CharField(max_length=10, null=True, blank=True, verbose_name="擁有者代碼")
    owner_type = models.CharField(max_length=10, choices=OWNER_TYPES, null=True, blank=True, verbose_name="擁有者類型")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "車輛"
        verbose_name_plural = "車輛"

    def __str__(self):
        return f"{self.vehicle_id} ({self.get_owner_type_display()}: {self.vehicle_owner_id})"

# 聯單基本表
class Manifest(models.Model):
    """聯單基本資訊表，為所有類型聯單的主表"""
    MANIFEST_TYPES = [
        ('disposal', '清除單'),
        ('reuse', '再利用單'),
    ]
    
    manifest_id = models.CharField(max_length=17, primary_key=True, verbose_name="聯單編號")
    waste_id = models.CharField(max_length=10, verbose_name="廢棄物ID")
    company = models.ForeignKey(Company, on_delete=models.PROTECT, verbose_name="事業機構")
    process = models.ForeignKey(Process, on_delete=models.PROTECT, verbose_name="製程")
    from_storage = models.BooleanField(default=False, verbose_name="是否由貯存地起運")
    origin_location = models.CharField(max_length=100, null=True, blank=True, verbose_name="起運地")
    manifest_confirmation = models.BooleanField(default=False, verbose_name="聯單確認")
    manifest_type = models.CharField(max_length=10, choices=MANIFEST_TYPES, verbose_name="聯單類型")
    is_visible = models.BooleanField(default=True, verbose_name="是否可見")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "聯單基本資訊"
        verbose_name_plural = "聯單基本資訊"

    def __str__(self):
        return f"聯單 {self.manifest_id} - {self.company.company_name}"
        
    @property
    def is_disposal(self):
        """是否為清除單"""
        return self.manifest_type == 'disposal'
        
    @property
    def is_reuse(self):
        """是否為再利用單"""
        return self.manifest_type == 'reuse'

# 申報單表
class Report(models.Model):
    """申報單資料表，儲存聯單的申報資訊"""
    report_id = models.AutoField(primary_key=True, verbose_name="申報單ID")
    manifest = models.OneToOneField(Manifest, on_delete=models.CASCADE, related_name='report', verbose_name="聯單編號")
    report_date = models.DateField(verbose_name="申報日期")
    report_time = models.TimeField(verbose_name="申報時間")
    transport_date = models.DateField(null=True, blank=True, verbose_name="清運日期")
    transport_time = models.TimeField(null=True, blank=True, verbose_name="清運時間")
    reported_weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="申報重量")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "申報單"
        verbose_name_plural = "申報單"

    def __str__(self):
        return f"申報單 {self.report_id} - 聯單 {self.manifest.manifest_id}"

# 清運單表
class Transport(models.Model):
    """清運單資料表，儲存聯單的清運資訊"""
    transport_id = models.AutoField(primary_key=True, verbose_name="清運單ID")
    manifest = models.OneToOneField(Manifest, on_delete=models.CASCADE, related_name='transport', verbose_name="聯單編號")
    carrier = models.ForeignKey(Carrier, on_delete=models.PROTECT, verbose_name="清除者")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, null=True, blank=True, verbose_name="車輛")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="運送日期")
    delivery_time = models.TimeField(null=True, blank=True, verbose_name="運送時間")
    carrier_vehicle_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="清除者運載車號")
    carrier_confirmation = models.BooleanField(default=False, verbose_name="清除者確認")
    carrier_rejection_reason = models.CharField(max_length=200, null=True, blank=True, verbose_name="清除者不接受原因")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "清運單"
        verbose_name_plural = "清運單"

    def __str__(self):
        return f"清運單 {self.transport_id} - 聯單 {self.manifest.manifest_id}"

# 處理單表
class Processing(models.Model):
    """處理單資料表，僅用於清除單類型的聯單"""
    processing_id = models.AutoField(primary_key=True, verbose_name="處理單ID")
    manifest = models.OneToOneField(Manifest, on_delete=models.CASCADE, related_name='processing', verbose_name="聯單編號")
    processor = models.ForeignKey(Processor, on_delete=models.PROTECT, verbose_name="處理者")
    receive_date = models.DateField(null=True, blank=True, verbose_name="收受日期")
    receive_time = models.TimeField(null=True, blank=True, verbose_name="收受時間")
    intermediate_treatment = models.CharField(max_length=50, null=True, blank=True, verbose_name="中間處理方式")
    processing_completion_date = models.DateField(null=True, blank=True, verbose_name="處理完成日期")
    processing_completion_time = models.TimeField(null=True, blank=True, verbose_name="處理完成時間")
    final_disposal_method = models.CharField(max_length=50, null=True, blank=True, verbose_name="最終處置方式")
    processor_confirmation = models.BooleanField(default=False, verbose_name="處理者確認")
    processor_vehicle = models.CharField(max_length=20, null=True, blank=True, verbose_name="處理者運載車號")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    
    # 最終處置相關欄位
    final_processor_id = models.CharField(max_length=10, null=True, blank=True, verbose_name="最終處置者代碼")
    final_processor_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="最終處置者名稱")
    entry_date = models.DateField(null=True, blank=True, verbose_name="進場日期")
    entry_time = models.TimeField(null=True, blank=True, verbose_name="進場時間")
    entry_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="進場編號")
    final_processor_confirmation = models.BooleanField(default=False, verbose_name="最終處置者確認")
    final_destination = models.CharField(max_length=50, null=True, blank=True, verbose_name="最終流向")

    class Meta:
        verbose_name = "處理單"
        verbose_name_plural = "處理單"

    def __str__(self):
        return f"處理單 {self.processing_id} - 聯單 {self.manifest.manifest_id}"

# 回收單表
class Recycling(models.Model):
    """回收單資料表，僅用於再利用單類型的聯單"""
    recycling_id = models.AutoField(primary_key=True, verbose_name="回收單ID")
    manifest = models.OneToOneField(Manifest, on_delete=models.CASCADE, related_name='recycling', verbose_name="聯單編號")
    reuser = models.ForeignKey(Reuser, on_delete=models.PROTECT, verbose_name="再利用者")
    recovery_date = models.DateField(null=True, blank=True, verbose_name="回收日期")
    recovery_time = models.TimeField(null=True, blank=True, verbose_name="回收時間")
    reuse_purpose = models.CharField(max_length=50, null=True, blank=True, verbose_name="再利用用途")
    reuse_purpose_description = models.CharField(max_length=100, null=True, blank=True, verbose_name="再利用用途說明")
    reuse_method = models.CharField(max_length=50, null=True, blank=True, verbose_name="再利用方式")
    reuse_completion_time = models.DateTimeField(null=True, blank=True, verbose_name="再利用完成時間")
    reuser_confirmation = models.BooleanField(default=False, verbose_name="再利用者是否確認")
    reuser_vehicle = models.CharField(max_length=20, null=True, blank=True, verbose_name="再利用者實際運載車號")
    reuser_rejection_reason = models.CharField(max_length=200, null=True, blank=True, verbose_name="再利用者不接受原因")
    source_confirmed = models.BooleanField(default=False, verbose_name="產源是否已確認申報聯單內容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "回收單"
        verbose_name_plural = "回收單"

    def __str__(self):
        return f"回收單 {self.recycling_id} - 聯單 {self.manifest.manifest_id}"

# 清除單資料表
class DisposalManifestData(models.Model):
    """清除單特有資料表，儲存清除單特有的廢棄物資訊"""
    manifest = models.OneToOneField(Manifest, on_delete=models.CASCADE, primary_key=True, related_name='disposal_data', verbose_name="聯單編號")
    waste_substance = models.ForeignKey(WasteSubstance, on_delete=models.PROTECT, verbose_name="廢棄物")
    waste_code = models.CharField(max_length=10, verbose_name="廢棄物代碼")
    waste_name = models.CharField(max_length=100, verbose_name="廢棄物名稱")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "清除單資料"
        verbose_name_plural = "清除單資料"

    def __str__(self):
        return f"清除單資料 - 聯單 {self.manifest.manifest_id}"

# 再利用單資料表
class ReuseManifestData(models.Model):
    """再利用單特有資料表，儲存再利用單特有的物質資訊"""
    manifest = models.OneToOneField(Manifest, on_delete=models.CASCADE, primary_key=True, related_name='reuse_data', verbose_name="聯單編號")
    substance = models.ForeignKey(WasteSubstance, on_delete=models.PROTECT, verbose_name="物質")
    substance_code = models.CharField(max_length=10, verbose_name="物質代碼")
    substance_name = models.CharField(max_length=100, verbose_name="物質名稱")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "再利用單資料"
        verbose_name_plural = "再利用單資料"

    def __str__(self):
        return f"再利用單資料 - 聯單 {self.manifest.manifest_id}"

# 維持原有的匯入歷史模型
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
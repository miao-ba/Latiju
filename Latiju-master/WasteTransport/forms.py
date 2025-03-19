from django import forms
from .models import (
    Company, Process, WasteSubstance, Carrier, Processor, Reuser, Vehicle,
    Manifest, Report, Transport, Processing, Recycling
)

class ManifestFilterForm(forms.Form):
    """聯單篩選表單 - 增強版"""
    MANIFEST_TYPE_CHOICES = [
        ('', '全部類型'),
        ('disposal', '清除單'),
        ('reuse', '再利用單'),
    ]
    
    CONFIRMATION_STATUS_CHOICES = [
        ('', '全部狀態'),
        ('confirmed', '已確認'),
        ('unconfirmed', '未確認'),
    ]

    FILTER_LOGIC_CHOICES = [
        ('or', '其中一個滿足即可'),
        ('and', '所有條件皆滿足'),
    ]
    
    manifest_type = forms.ChoiceField(
        choices=MANIFEST_TYPE_CHOICES, 
        required=False, 
        label="聯單類型",
        widget=forms.Select(attrs={'class': 'ts-select'})
    )
    
    manifest_id = forms.CharField(
        max_length=17, 
        required=False, 
        label="聯單編號",
        widget=forms.TextInput(attrs={'class': 'ts-input', 'placeholder': '請輸入聯單編號'})
    )
    
    company_name = forms.CharField(
        max_length=100, 
        required=False, 
        label="事業機構名稱",
        widget=forms.TextInput(attrs={
            'class': 'ts-input', 
            'placeholder': '請輸入事業機構名稱',
            'id': 'company_name',  # 添加ID用於自動完成功能
        })
    )
    
    waste_code = forms.CharField(
        max_length=10, 
        required=False, 
        label="廢棄物/物質代碼",
        widget=forms.TextInput(attrs={
            'class': 'ts-input', 
            'placeholder': '請輸入代碼',
            'id': 'waste_code',  # 添加ID用於自動完成功能
        })
    )
    
    waste_name = forms.CharField(
        max_length=100, 
        required=False, 
        label="廢棄物/物質名稱",
        widget=forms.TextInput(attrs={
            'class': 'ts-input', 
            'placeholder': '請輸入名稱',
            'id': 'waste_name',  # 添加ID用於自動完成功能
        })
    )
    
    report_date_from = forms.DateField(
        required=False, 
        label="申報日期從",
        widget=forms.DateInput(attrs={'class': 'ts-input', 'type': 'date'})
    )
    
    report_date_to = forms.DateField(
        required=False, 
        label="申報日期至",
        widget=forms.DateInput(attrs={'class': 'ts-input', 'type': 'date'})
    )
    
    reported_weight_above = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False, 
        label="申報重量高於",
        widget=forms.NumberInput(attrs={'class': 'ts-input', 'placeholder': '最小重量 (kg)', 'min': '0'})
    )
    
    reported_weight_below = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False, 
        label="申報重量低於",
        widget=forms.NumberInput(attrs={'class': 'ts-input', 'placeholder': '最大重量 (kg)', 'min': '0'})
    )
    
    confirmation_status = forms.ChoiceField(
        choices=CONFIRMATION_STATUS_CHOICES,
        required=False,
        label="確認狀態",
        widget=forms.Select(attrs={'class': 'ts-select'})
    )
    
    filter_logic = forms.ChoiceField(
        choices=FILTER_LOGIC_CHOICES,
        required=False,
        initial='and',
        label="篩選邏輯",
        widget=forms.RadioSelect(attrs={'class': 'ts-radio'})
    )

class CSVImportForm(forms.Form):
    """CSV匯入表單"""
    IMPORT_TYPE_CHOICES = [
        ('disposal', '清除單'),
        ('reuse', '再利用單'),
    ]
    
    CONFLICT_RESOLUTION_CHOICES = [
        ('ask', '詢問如何處理'),
        ('skip', '略過重複資料'),
        ('replace', '覆蓋重複資料'),
        ('keep_both', '保留兩者'),
        ('smart_merge', '智慧合併'),
    ]
    
    csv_file = forms.FileField(
        label="CSV/XLSX 檔案",
        help_text="請選擇要匯入的檔案 (支援 CSV 或 XLSX 格式)",
        widget=forms.FileInput(attrs={'class': 'ts-input', 'accept': '.csv,.xlsx'})
    )
    
    import_type = forms.ChoiceField(
        choices=IMPORT_TYPE_CHOICES,
        label="匯入類型",
        widget=forms.Select(attrs={'class': 'ts-select'})
    )
    
    conflict_resolution = forms.ChoiceField(
        choices=CONFLICT_RESOLUTION_CHOICES,
        initial='ask',
        label="衝突處理方式",
        widget=forms.Select(attrs={'class': 'ts-select'})
    )
    
    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')
        
        if not file:
            raise forms.ValidationError("請選擇一個檔案")
        
        # 檢查檔案格式
        file_name = file.name.lower()
        if not (file_name.endswith('.csv') or file_name.endswith('.xlsx')):
            raise forms.ValidationError("僅支援 CSV 或 XLSX 檔案格式")
            
        # 檢查檔案大小，限制為5MB
        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("檔案大小不得超過5MB")
            
        return file

# 公司表單
class CompanyForm(forms.ModelForm):
    """事業機構表單"""
    class Meta:
        model = Company
        fields = ['company_id', 'company_name']
        widgets = {
            'company_id': forms.TextInput(attrs={'class': 'ts-input'}),
            'company_name': forms.TextInput(attrs={'class': 'ts-input'}),
        }

# 製程表單
class ProcessForm(forms.ModelForm):
    """製程表單"""
    class Meta:
        model = Process
        fields = ['process_code', 'process_name']
        widgets = {
            'process_code': forms.TextInput(attrs={'class': 'ts-input'}),
            'process_name': forms.TextInput(attrs={'class': 'ts-input'}),
        }

# 廢棄物/物質表單
class WasteSubstanceForm(forms.ModelForm):
    """廢棄物/物質表單"""
    class Meta:
        model = WasteSubstance
        fields = ['substance_code', 'substance_name', 'substance_type']
        widgets = {
            'substance_code': forms.TextInput(attrs={'class': 'ts-input'}),
            'substance_name': forms.TextInput(attrs={'class': 'ts-input'}),
            'substance_type': forms.Select(attrs={'class': 'ts-select'}),
        }

# 清除者表單
class CarrierForm(forms.ModelForm):
    """清除者表單"""
    class Meta:
        model = Carrier
        fields = ['carrier_id', 'carrier_name']
        widgets = {
            'carrier_id': forms.TextInput(attrs={'class': 'ts-input'}),
            'carrier_name': forms.TextInput(attrs={'class': 'ts-input'}),
        }

# 處理者表單
class ProcessorForm(forms.ModelForm):
    """處理者表單"""
    class Meta:
        model = Processor
        fields = ['processor_id', 'processor_name']
        widgets = {
            'processor_id': forms.TextInput(attrs={'class': 'ts-input'}),
            'processor_name': forms.TextInput(attrs={'class': 'ts-input'}),
        }

# 再利用者表單
class ReuserForm(forms.ModelForm):
    """再利用者表單"""
    class Meta:
        model = Reuser
        fields = ['reuser_id', 'reuser_name', 'reuser_nature']
        widgets = {
            'reuser_id': forms.TextInput(attrs={'class': 'ts-input'}),
            'reuser_name': forms.TextInput(attrs={'class': 'ts-input'}),
            'reuser_nature': forms.TextInput(attrs={'class': 'ts-input'}),
        }

# 車輛表單
class VehicleForm(forms.ModelForm):
    """車輛表單"""
    class Meta:
        model = Vehicle
        fields = ['vehicle_id', 'vehicle_type', 'vehicle_capacity', 'vehicle_owner_id', 'owner_type']
        widgets = {
            'vehicle_id': forms.TextInput(attrs={'class': 'ts-input'}),
            'vehicle_type': forms.TextInput(attrs={'class': 'ts-input'}),
            'vehicle_capacity': forms.NumberInput(attrs={'class': 'ts-input', 'min': '0', 'step': '0.01'}),
            'vehicle_owner_id': forms.TextInput(attrs={'class': 'ts-input'}),
            'owner_type': forms.Select(attrs={'class': 'ts-select'}),
        }
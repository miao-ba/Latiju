import csv
import io
import json
import time
import logging
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from MedicalWasteManagementSystem.permissions import permission_required
from .models import (
    Manifest, Report, Transport, Processing, Recycling,
    DisposalManifestData, ReuseManifestData, ImportHistory,
    Company, Process, WasteSubstance, Carrier, Processor, Reuser, Vehicle
)
from .forms import ManifestFilterForm, CSVImportForm

# 設定日誌
logger = logging.getLogger(__name__)

# 聯單清單頁面 - 主視圖
@permission_required('importer')
def manifest_list(request):
    """
    顯示聯單清單頁面，支援篩選功能
    """
    form = ManifestFilterForm(request.GET)
    
    # 初始化查詢集 - 只查詢可見的資料
    query = Manifest.objects.filter(is_visible=True)
    
    # 套用篩選條件
    if form.is_valid():
        data = form.cleaned_data
        
        # 根據聯單類型篩選
        manifest_type = data.get('manifest_type')
        if manifest_type:
            query = query.filter(manifest_type=manifest_type)
            
        # 聯單編號篩選
        manifest_id = data.get('manifest_id')
        if manifest_id:
            query = query.filter(manifest_id__icontains=manifest_id)
            
        # 事業機構名稱篩選
        company_name = data.get('company_name')
        if company_name:
            query = query.filter(company__company_name__icontains=company_name)
            
        # 廢棄物代碼/物質代碼篩選
        waste_code = data.get('waste_code')
        if waste_code:
            # 使用 Q 對象組合查詢條件
            query = query.filter(
                Q(disposal_data__waste_code__icontains=waste_code) | 
                Q(reuse_data__substance_code__icontains=waste_code)
            )
            
        # 廢棄物名稱/物質名稱篩選
        waste_name = data.get('waste_name')
        if waste_name:
            # 使用 Q 對象組合查詢條件
            query = query.filter(
                Q(disposal_data__waste_name__icontains=waste_name) | 
                Q(reuse_data__substance_name__icontains=waste_name)
            )
            
        # 申報日期篩選
        report_date_from = data.get('report_date_from')
        if report_date_from:
            query = query.filter(report__report_date__gte=report_date_from)
            
        report_date_to = data.get('report_date_to')
        if report_date_to:
            query = query.filter(report__report_date__lte=report_date_to)
            
        # 申報重量篩選
        reported_weight_below = data.get('reported_weight_below')
        if reported_weight_below:
            query = query.filter(report__reported_weight__lte=reported_weight_below)
            
        reported_weight_above = data.get('reported_weight_above')
        if reported_weight_above:
            query = query.filter(report__reported_weight__gte=reported_weight_above)
            
        # 確認狀態篩選
        confirmation_status = data.get('confirmation_status')
        if confirmation_status == 'confirmed':
            query = query.filter(manifest_confirmation=True)
        elif confirmation_status == 'unconfirmed':
            query = query.filter(manifest_confirmation=False)
    
    # 使用 select_related 和 prefetch_related 優化查詢
    query = query.select_related('company', 'report').prefetch_related(
        'disposal_data', 'reuse_data', 'transport', 'processing', 'recycling'
    )
    
    # 根據申報日期排序
    query = query.order_by('-report__report_date')
    
    # 準備顯示的聯單數據
    manifest_results = []
    for manifest in query:
        # 基礎數據
        item = {
            'type': manifest.manifest_type,
            'type_display': '清除單' if manifest.manifest_type == 'disposal' else '再利用單',
            'manifest': manifest,
            'manifest_id': manifest.manifest_id,
            'waste_id': manifest.waste_id,
            'company_name': manifest.company.company_name,
            'report_date': manifest.report.report_date if hasattr(manifest, 'report') else None,
            'manifest_confirmation': manifest.manifest_confirmation
        }
        
        # 根據聯單類型添加不同的數據
        if manifest.manifest_type == 'disposal':
            if hasattr(manifest, 'disposal_data'):
                item['waste_code'] = manifest.disposal_data.waste_code
                item['waste_name'] = manifest.disposal_data.waste_name
            else:
                item['waste_code'] = '無資料'
                item['waste_name'] = '無資料'
                
            if hasattr(manifest, 'report'):
                item['reported_weight'] = manifest.report.reported_weight
            else:
                item['reported_weight'] = 0
        else:  # 再利用單
            if hasattr(manifest, 'reuse_data'):
                item['waste_code'] = manifest.reuse_data.substance_code
                item['waste_name'] = manifest.reuse_data.substance_name
            else:
                item['waste_code'] = '無資料'
                item['waste_name'] = '無資料'
                
            if hasattr(manifest, 'report'):
                item['reported_weight'] = manifest.report.reported_weight
            else:
                item['reported_weight'] = 0
        
        manifest_results.append(item)
    
    # 分頁處理
    paginator = Paginator(manifest_results, 20)  # 每頁20筆
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 取得最近的匯入歷史
    recent_imports = ImportHistory.objects.all().order_by('-import_date')[:5]
    
    # 統計資料
    total_count = query.count()
    disposal_count = query.filter(manifest_type='disposal').count()
    reuse_count = query.filter(manifest_type='reuse').count()
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'disposal_count': disposal_count,
        'reuse_count': reuse_count,
        'total_count': total_count,
        'manifests': page_obj,  # 為了卡片式顯示添加
        'recent_imports': recent_imports,
        'import_form': CSVImportForm(),
    }
    
    # 如果是AJAX請求，只返回聯單部分的HTML
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        manifests_html = render_to_string('waste_transport/partials/manifest_cards.html', {'manifests': page_obj})
        return JsonResponse({'html': manifests_html})
    
    return render(request, 'waste_transport/manifest_list.html', context)

# 清除單詳細資訊 - AJAX
@permission_required('importer')
def disposal_manifest_detail(request, manifest_id, waste_id):
    """
    顯示清除單詳細資訊
    """
    # 使用 select_related 和 prefetch_related 優化查詢
    manifest = get_object_or_404(
        Manifest.objects.select_related(
            'company', 'process', 'report', 'transport', 'transport__carrier', 
            'processing', 'processing__processor', 'disposal_data', 'disposal_data__waste_substance'
        ),
        manifest_id=manifest_id, waste_id=waste_id, is_visible=True, manifest_type='disposal'
    )
    
    # 如果是AJAX請求，返回HTML片段
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('waste_transport/partials/disposal_detail.html', {'manifest': manifest})
        return JsonResponse({'html': html})
    
    # 否則返回完整頁面
    return render(request, 'waste_transport/disposal_manifest_detail.html', {'manifest': manifest})

# 再利用單詳細資訊 - AJAX
@permission_required('importer')
def reuse_manifest_detail(request, manifest_id, waste_id):
    """
    顯示再利用單詳細資訊
    """
    # 使用 select_related 和 prefetch_related 優化查詢
    manifest = get_object_or_404(
        Manifest.objects.select_related(
            'company', 'process', 'report', 'transport', 'transport__carrier', 
            'recycling', 'recycling__reuser', 'reuse_data', 'reuse_data__substance'
        ),
        manifest_id=manifest_id, waste_id=waste_id, is_visible=True, manifest_type='reuse'
    )
    
    # 如果是AJAX請求，返回HTML片段
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('waste_transport/partials/reuse_detail.html', {'manifest': manifest})
        return JsonResponse({'html': html})
    
    # 否則返回完整頁面
    return render(request, 'waste_transport/reuse_manifest_detail.html', {'manifest': manifest})

# 獲取所有符合條件的聯單ID，用於全選功能
@permission_required('importer')
def get_all_manifest_ids(request):
    """
    獲取所有符合篩選條件的聯單ID，用於全選功能
    """
    form = ManifestFilterForm(request.GET)
    
    # 初始化查詢集 - 只查詢可見的資料
    query = Manifest.objects.filter(is_visible=True)
    
    # 套用篩選條件
    if form.is_valid():
        data = form.cleaned_data
        
        # 根據聯單類型篩選
        manifest_type = data.get('manifest_type')
        if manifest_type:
            query = query.filter(manifest_type=manifest_type)
            
        # 聯單編號篩選
        manifest_id = data.get('manifest_id')
        if manifest_id:
            query = query.filter(manifest_id__icontains=manifest_id)
            
        # 事業機構名稱篩選
        company_name = data.get('company_name')
        if company_name:
            query = query.filter(company__company_name__icontains=company_name)
            
        # 廢棄物代碼篩選
        waste_code = data.get('waste_code')
        if waste_code:
            # 使用 Q 對象組合查詢條件
            query = query.filter(
                Q(disposal_data__waste_code__icontains=waste_code) | 
                Q(reuse_data__substance_code__icontains=waste_code)
            )
            
        # 廢棄物名稱篩選
        waste_name = data.get('waste_name')
        if waste_name:
            # 使用 Q 對象組合查詢條件
            query = query.filter(
                Q(disposal_data__waste_name__icontains=waste_name) | 
                Q(reuse_data__substance_name__icontains=waste_name)
            )
            
        # 申報日期篩選
        report_date_from = data.get('report_date_from')
        if report_date_from:
            query = query.filter(report__report_date__gte=report_date_from)
            
        report_date_to = data.get('report_date_to')
        if report_date_to:
            query = query.filter(report__report_date__lte=report_date_to)
            
        # 申報重量篩選
        reported_weight_below = data.get('reported_weight_below')
        if reported_weight_below:
            query = query.filter(report__reported_weight__lte=reported_weight_below)
            
        reported_weight_above = data.get('reported_weight_above')
        if reported_weight_above:
            query = query.filter(report__reported_weight__gte=reported_weight_above)
            
        # 確認狀態篩選
        confirmation_status = data.get('confirmation_status')
        if confirmation_status == 'confirmed':
            query = query.filter(manifest_confirmation=True)
        elif confirmation_status == 'unconfirmed':
            query = query.filter(manifest_confirmation=False)
    
    # 提取所有符合條件的聯單ID
    manifests = [{'type': m.manifest_type, 'manifest_id': m.manifest_id, 'waste_id': m.waste_id} 
                for m in query.only('manifest_id', 'manifest_type', 'waste_id')]
    
    return JsonResponse({
        'success': True,
        'manifests': manifests
    })

# CSV匯入處理 - AJAX
@csrf_exempt
@permission_required('importer')
def import_csv(request):
    """
    處理CSV檔案匯入
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '僅支援POST請求'})
    
    form = CSVImportForm(request.POST, request.FILES)
    if not form.is_valid():
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = [str(error) for error in error_list]
        return JsonResponse({'success': False, 'errors': errors})
    
    try:
        csv_file = request.FILES['csv_file']
        import_type = form.cleaned_data['import_type']
        conflict_resolution = form.cleaned_data['conflict_resolution']
        
        # 處理CSV檔案
        csv_file_data = csv_file.read().decode('utf-8-sig')
        csv_io = io.StringIO(csv_file_data)
        reader = csv.DictReader(csv_io)
        rows = list(reader)  # 將所有行先讀入記憶體
        
        # 檢查是否有衝突
        conflict_exists = False
        conflicting_records = []
        
        for row in rows:
            manifest_id = row.get('聯單編號')
            waste_id = row.get('廢棄物ID')
            if not manifest_id or not waste_id:
                continue
                
            # 檢查是否已存在
            existing = Manifest.objects.filter(
                manifest_id=manifest_id, 
                waste_id=waste_id,
                is_visible=True
            ).first()
                
            if existing:
                conflict_exists = True
                conflict_data = {
                    'manifest_id': manifest_id,
                    'waste_id': waste_id,
                    'company_name': row.get('事業機構名稱', ''),
                    'report_date': row.get('申報日期', ''),
                    'new_data': {k: v for k, v in row.items() if v},
                    'existing_data': {}
                }
                
                # 添加現有資料以顯示差異
                if existing.manifest_type == 'disposal':
                    if hasattr(existing, 'disposal_data'):
                        conflict_data['existing_data'] = {
                            '聯單編號': existing.manifest_id,
                            '事業機構代碼': existing.company.company_id,
                            '事業機構名稱': existing.company.company_name,
                            '申報日期': existing.report.report_date.strftime('%Y/%m/%d') if hasattr(existing, 'report') else '',
                            '廢棄物代碼': existing.disposal_data.waste_code,
                            '廢棄物名稱': existing.disposal_data.waste_name,
                            '申報重量': str(existing.report.reported_weight) if hasattr(existing, 'report') else '',
                            '廢棄物ID': existing.waste_id
                        }
                else:  # 再利用單
                    if hasattr(existing, 'reuse_data'):
                        conflict_data['existing_data'] = {
                            '聯單編號': existing.manifest_id,
                            '事業機構代碼': existing.company.company_id,
                            '事業機構名稱': existing.company.company_name,
                            '申報日期': existing.report.report_date.strftime('%Y/%m/%d') if hasattr(existing, 'report') else '',
                            '物質代碼': existing.reuse_data.substance_code,
                            '物質名稱': existing.reuse_data.substance_name,
                            '申報重量': str(existing.report.reported_weight) if hasattr(existing, 'report') else '',
                            '廢棄物ID': existing.waste_id
                        }
                
                conflicting_records.append(conflict_data)
        
        if conflict_exists and conflict_resolution == 'ask':
            # 返回衝突資訊，由前端顯示衝突解決對話框
            return JsonResponse({
                'success': False,
                'conflict': True,
                'conflicting_records': conflicting_records,
                'import_data': {
                    'csv_data': csv_file_data,
                    'import_type': import_type,
                    'filename': csv_file.name,
                }
            })
        else:
            # 直接處理匯入
            result = process_csv_import(rows, import_type, conflict_resolution, csv_file.name)
            return JsonResponse(result)
            
    except Exception as e:
        logger.error(f"匯入過程中發生錯誤：{str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': f"匯入過程中發生錯誤：{str(e)}"})

# 處理衝突解決 - AJAX
@csrf_exempt
@permission_required('importer')
def handle_conflict_resolution(request):
    """
    處理衝突解決
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '僅支援POST請求'})
    
    try:
        # 解析JSON資料
        data = json.loads(request.body)
        csv_data = data.get('csv_data')
        import_type = data.get('import_type')
        filename = data.get('filename')
        conflict_resolution = data.get('conflict_resolution')
        apply_to_all = data.get('apply_to_all', False)
        
        if not all([csv_data, import_type, filename, conflict_resolution]):
            return JsonResponse({'success': False, 'error': '缺少必要參數'})
        
        # 處理CSV資料
        csv_io = io.StringIO(csv_data)
        reader = csv.DictReader(csv_io)
        rows = list(reader)
        
        # 處理匯入
        result = process_csv_import(rows, import_type, conflict_resolution, filename, apply_to_all)
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"處理衝突解決時發生錯誤：{str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': f"處理衝突解決時發生錯誤：{str(e)}"})

# 處理CSV匯入
def process_csv_import(rows, import_type, conflict_resolution, filename, apply_to_all=False):
    """
    處理CSV檔案匯入的核心邏輯
    """
    try:
        # 統計資料
        total_records = len(rows)
        imported_records = 0
        skipped_records = 0
        
        # 批次處理，每100筆一個事務
        batch_size = 100
        
        with transaction.atomic():
            for i in range(0, total_records, batch_size):
                batch = rows[i:i+batch_size]
                
                try:
                    with transaction.atomic():
                        for row in batch:
                            row = transform_waste_record(row)
                            # 根據聯單類型處理資料
                            if import_type == 'disposal':
                                result = handle_disposal_import(row, conflict_resolution, apply_to_all)
                            else:  # 再利用單
                                result = handle_reuse_import(row, conflict_resolution, apply_to_all)
                            
                            if result:
                                imported_records += 1
                            else:
                                skipped_records += 1
                except Exception as e:
                    logger.error(f"批次處理時發生錯誤：{str(e)}", exc_info=True)
                    skipped_records += len(batch)
            
            # 儲存匯入歷史記錄
            ImportHistory.objects.create(
                filename=filename,
                import_type=import_type,
                total_records=total_records,
                imported_records=imported_records,
                skipped_records=skipped_records
            )
            
            return {
                'success': True, 
                'message': f'成功匯入 {imported_records} 筆資料，跳過 {skipped_records} 筆資料',
                'imported': imported_records,
                'skipped': skipped_records,
                'total': total_records
            }
            
    except Exception as e:
        logger.error(f"匯入過程中發生錯誤：{str(e)}", exc_info=True)
        return {'success': False, 'error': f"匯入過程中發生錯誤：{str(e)}"}

# 處理清除單匯入
def handle_disposal_import(row, conflict_resolution, apply_to_all=False):
    """
    處理清除單匯入邏輯
    """
    try:
        # 轉換布林值欄位
        bool_fields = ['是否由貯存地起運', '聯單確認', '清除者確認', '處理者確認', '最終處置者確認']
        for field in bool_fields:
            if field in row:
                value = row[field]
                row[field] = value.upper() == 'Y' or value.upper() == 'TRUE' or value == '1'
        
        # 檢查聯單是否已存在
        manifest_id = row.get('聯單編號')
        waste_id = row.get('廢棄物ID')
        if not manifest_id or not waste_id:
            return False
        
        with transaction.atomic():
            # 檢查現有資料
            existing_manifest = Manifest.objects.filter(
                manifest_id=manifest_id, 
                waste_id=waste_id, 
                is_visible=True
            ).first()
            
            # 根據衝突處理方式決定如何處理
            if existing_manifest:
                if conflict_resolution == 'skip':
                    return False
                elif conflict_resolution == 'replace':
                    # 將現有聯單標記為不可見，然後創建新的
                    existing_manifest.is_visible = False
                    existing_manifest.save()
                elif conflict_resolution == 'cancel':
                    # 取消整個匯入過程
                    return False
            
            # 1. 建立或獲取公司資料
            company, _ = Company.objects.get_or_create(
                company_id=row.get('事業機構代碼', ''),
                defaults={
                    'company_name': row.get('事業機構名稱', ''),
                }
            )
            
            # 2. 建立或獲取製程資料
            process, _ = Process.objects.get_or_create(
                process_code=row.get('製程代碼', '0'),
                defaults={
                    'process_name': row.get('製程名稱', '無資料'),
                }
            )
            
            # 3. 建立或獲取廢棄物資料
            waste_substance, _ = WasteSubstance.objects.get_or_create(
                substance_code=row.get('廢棄物代碼', ''),
                substance_type='waste',
                defaults={
                    'substance_name': row.get('廢棄物名稱', ''),
                }
            )
            
            # 4. 建立或獲取清除者資料
            carrier, _ = Carrier.objects.get_or_create(
                carrier_id=row.get('清除者代碼', ''),
                defaults={
                    'carrier_name': row.get('清除者名稱', ''),
                }
            )
            
            # 5. 建立或獲取處理者資料
            processor, _ = Processor.objects.get_or_create(
                processor_id=row.get('處理者代碼', ''),
                defaults={
                    'processor_name': row.get('處理者名稱', ''),
                }
            )
            
            # 6. 建立或獲取車輛資料
            vehicle = None
            if row.get('運載車號'):
                vehicle, _ = Vehicle.objects.get_or_create(
                    vehicle_id=row.get('運載車號', ''),
                    defaults={
                        'vehicle_owner_id': row.get('清除者代碼', ''),
                        'owner_type': 'carrier',
                    }
                )
            
            # 7. 建立聯單主記錄
            manifest = Manifest.objects.create(
                manifest_id=manifest_id,
                waste_id=waste_id,
                company=company,
                process=process,
                from_storage=row.get('是否由貯存地起運', False),
                origin_location=row.get('起運地', ''),
                manifest_confirmation=row.get('聯單確認', False),
                manifest_type='disposal',
                is_visible=True,
            )
            
            # 8. 建立清除單特有資料
            DisposalManifestData.objects.create(
                manifest=manifest,
                waste_substance=waste_substance,
                waste_code=row.get('廢棄物代碼', ''),
                waste_name=row.get('廢棄物名稱', ''),
            )
            
            # 9. 建立申報單
            Report.objects.create(
                manifest=manifest,
                report_date=parse_date(row.get('申報日期', None)),
                report_time=parse_time(row.get('申報時間', None)),
                transport_date=parse_date(row.get('清運日期', None)),
                transport_time=parse_time(row.get('清運時間', None)),
                reported_weight=parse_float(row.get('申報重量', 0)),
            )
            
            # 10. 建立清運單
            Transport.objects.create(
                manifest=manifest,
                carrier=carrier,
                vehicle=vehicle,
                delivery_date=parse_date(row.get('運送日期', None)),
                delivery_time=parse_time(row.get('運送時間', None)),
                carrier_vehicle_number=row.get('清除者運載車號', ''),
                carrier_confirmation=row.get('清除者確認', False),
            )
            
            # 11. 建立處理單
            Processing.objects.create(
                manifest=manifest,
                processor=processor,
                receive_date=parse_date(row.get('收受日期', None)),
                receive_time=parse_time(row.get('收受時間', None)),
                intermediate_treatment=row.get('中間處理方式', ''),
                processing_completion_date=parse_date(row.get('處理完成日期', None)),
                processing_completion_time=parse_time(row.get('處理完成時間', None)),
                final_disposal_method=row.get('最終處置方式', ''),
                processor_confirmation=row.get('處理者確認', False),
                processor_vehicle=row.get('處理者運載車號', ''),
                final_processor_id=row.get('最終處置者代碼', ''),
                final_processor_name=row.get('最終處置者名稱', ''),
                entry_date=parse_date(row.get('進場日期', None)),
                entry_time=parse_time(row.get('進場時間', None)),
                entry_number=row.get('進場編號', ''),
                final_processor_confirmation=row.get('最終處置者確認', False),
                final_destination=row.get('最終流向', ''),
            )
            
            return True
    except Exception as e:
        logger.error(f"處理清除單匯入時發生錯誤: {e}", exc_info=True)
        return False

# 處理再利用單匯入
def handle_reuse_import(row, conflict_resolution, apply_to_all=False):
    """
    處理再利用單匯入邏輯
    """
    try:
        # 轉換布林值欄位
        bool_fields = ['是否由貯存地起運', '聯單確認', '清除者確認', '再利用者是否確認', '產源是否已確認申報聯單內容']
        for field in bool_fields:
            if field in row:
                value = row[field]
                row[field] = value.upper() == 'Y' or value.upper() == 'TRUE' or value == '1'
        
        # 檢查聯單是否已存在
        manifest_id = row.get('聯單編號')
        waste_id = row.get('廢棄物ID')
        if not manifest_id or not waste_id:
            return False
            
        with transaction.atomic():
            # 檢查現有資料
            existing_manifest = Manifest.objects.filter(
                manifest_id=manifest_id, 
                waste_id=waste_id,
                is_visible=True
            ).first()
            
            # 根據衝突處理方式決定如何處理
            if existing_manifest:
                if conflict_resolution == 'skip':
                    return False
                elif conflict_resolution == 'replace':
                    # 將現有聯單標記為不可見，然後創建新的
                    existing_manifest.is_visible = False
                    existing_manifest.save()
                elif conflict_resolution == 'cancel':
                    # 取消整個匯入過程
                    return False
            
            # 1. 建立或獲取公司資料
            company, _ = Company.objects.get_or_create(
                company_id=row.get('事業機構代碼', ''),
                defaults={
                    'company_name': row.get('事業機構名稱', ''),
                }
            )
            
            # 2. 建立或獲取製程資料
            process, _ = Process.objects.get_or_create(
                process_code=row.get('製程代碼', '0'),
                defaults={
                    'process_name': row.get('製程名稱', '無資料'),
                }
            )
            
            # 3. 建立或獲取物質資料
            substance, _ = WasteSubstance.objects.get_or_create(
                substance_code=row.get('物質代碼', ''),
                substance_type='reuse',
                defaults={
                    'substance_name': row.get('物質名稱', ''),
                }
            )
            
            # 4. 建立或獲取清除者資料（如果有）
            carrier = None
            if row.get('清除者代碼'):
                carrier, _ = Carrier.objects.get_or_create(
                    carrier_id=row.get('清除者代碼', ''),
                    defaults={
                        'carrier_name': row.get('清除者名稱', '') or '',
                    }
                )
            
            # 5. 建立或獲取再利用者資料（如果有）
            reuser = None
            if row.get('再利用者代碼'):
                reuser, _ = Reuser.objects.get_or_create(
                    reuser_id=row.get('再利用者代碼', ''),
                    defaults={
                        'reuser_name': row.get('再利用者名稱', '') or '',
                        'reuser_nature': row.get('再利用者性質', ''),
                    }
                )
            
            # 6. 建立或獲取車輛資料
            vehicle = None
            if row.get('運載車號'):
                vehicle, _ = Vehicle.objects.get_or_create(
                    vehicle_id=row.get('運載車號', ''),
                    defaults={
                        'vehicle_owner_id': row.get('清除者代碼', '') if row.get('清除者代碼') else None,
                        'owner_type': 'carrier',
                    }
                )
            
            # 7. 建立聯單主記錄
            manifest = Manifest.objects.create(
                manifest_id=manifest_id,
                waste_id=waste_id,
                company=company,
                process=process,
                from_storage=row.get('是否由貯存地起運', False),
                origin_location=row.get('起運地', ''),
                manifest_confirmation=row.get('聯單確認', False),
                manifest_type='reuse',
                is_visible=True,
            )
            
            # 8. 建立再利用單特有資料
            ReuseManifestData.objects.create(
                manifest=manifest,
                substance=substance,
                substance_code=row.get('物質代碼', ''),
                substance_name=row.get('物質名稱', ''),
            )
            
            # 9. 建立申報單
            Report.objects.create(
                manifest=manifest,
                report_date=parse_date(row.get('申報日期', None)),
                report_time=parse_time(row.get('申報時間', None)),
                transport_date=parse_date(row.get('清運日期', None)),
                transport_time=parse_time(row.get('清運時間', None)),
                reported_weight=parse_float(row.get('申報重量', 0)),
            )
            
            # 10. 建立清運單（如果有清除者）
            if carrier:
                Transport.objects.create(
                    manifest=manifest,
                    carrier=carrier,
                    vehicle=vehicle,
                    delivery_date=parse_date(row.get('運送日期', None)),
                    delivery_time=parse_time(row.get('運送時間', None)),
                    carrier_vehicle_number=row.get('清除者實際運載車號', ''),
                    carrier_confirmation=row.get('清除者確認', False),
                    carrier_rejection_reason=row.get('清除者不接受原因', ''),
                )
            
            # 11. 建立回收單（如果有再利用者）
            if reuser:
                Recycling.objects.create(
                    manifest=manifest,
                    reuser=reuser,
                    recovery_date=parse_date(row.get('回收日期', None)),
                    recovery_time=parse_time(row.get('回收時間', None)),
                    reuse_purpose=row.get('再利用用途', ''),
                    reuse_purpose_description=row.get('再利用用途說明', ''),
                    reuse_method=row.get('再利用方式', ''),
                    reuse_completion_time=parse_datetime(row.get('再利用完成時間', None)),
                    reuser_confirmation=row.get('再利用者是否確認', False),
                    reuser_vehicle=row.get('再利用者實際運載車號', ''),
                    reuser_rejection_reason=row.get('再利用者不接受原因', ''),
                    source_confirmed=row.get('產源是否已確認申報聯單內容', False),
                )
                
            return True
    except Exception as e:
        logger.error(f"處理再利用單匯入時發生錯誤: {e}", exc_info=True)
        return False

# 修改刪除聯單功能 - 變更為標記不可見
@csrf_exempt
@permission_required('importer')
def delete_manifests(request):
    """
    批量標記聯單為不可見
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '僅支援POST請求'})
    
    try:
        # 解析JSON資料
        data = json.loads(request.body)
        manifests_to_delete = data.get('manifests', [])
        
        if not manifests_to_delete:
            return JsonResponse({'success': False, 'error': '未提供要移除的聯單'})
        
        deleted_count = 0
        
        with transaction.atomic():
            for manifest in manifests_to_delete:
                manifest_type = manifest.get('type')
                manifest_id = manifest.get('manifestId')
                waste_id = manifest.get('wasteId')
                
                if not all([manifest_type, manifest_id, waste_id]):
                    continue
                
                # 標記聯單為不可見
                result = Manifest.objects.filter(
                    manifest_id=manifest_id, 
                    waste_id=waste_id,
                    manifest_type=manifest_type,
                    is_visible=True
                ).update(is_visible=False)
                
                deleted_count += result
        
        return JsonResponse({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'成功移除 {deleted_count} 筆聯單'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'移除過程中發生錯誤：{str(e)}'})

# 自動完成相關視圖函數
def autocomplete_company_name(request):
    """自動完成事業機構名稱"""
    query = request.GET.get('q', '')
    
    # 從公司資料表中查詢符合條件的名稱
    companies = Company.objects.filter(
        company_name__icontains=query
    ).values('company_name').distinct()[:20]
    
    # 將結果格式化為列表字典
    results = [{'name': company['company_name']} for company in companies]
    
    return JsonResponse({'results': results})

def autocomplete_waste_name(request):
    """自動完成廢棄物名稱"""
    query = request.GET.get('q', '')
    
    # 從物質資料表中查詢符合條件的名稱
    waste_substances = WasteSubstance.objects.filter(
        substance_name__icontains=query
    ).values('substance_name').distinct()[:20]
    
    # 將結果格式化為列表字典
    results = [{'name': substance['substance_name']} for substance in waste_substances]
    
    return JsonResponse({'results': results})

def autocomplete_waste_code(request):
    """自動完成廢棄物代碼"""
    query = request.GET.get('q', '')
    
    # 從物質資料表中查詢符合條件的代碼
    waste_codes = WasteSubstance.objects.filter(
        substance_code__icontains=query
    ).values('substance_code').distinct()[:20]
    
    # 將結果格式化為列表字典
    results = [{'code': substance['substance_code']} for substance in waste_codes]
    
    return JsonResponse({'results': results})

# 輔助函數：解析日期
def parse_date(date_str):
    if not date_str or date_str.strip() == '':
        return None
        
    formats = ['%Y/%m/%d', '%Y-%m-%d', '%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M:%S']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except (ValueError, TypeError):
            continue
    
    return None

# 輔助函數：解析時間
def parse_time(time_str):
    if not time_str or time_str.strip() == '':
        return None
        
    formats = ['%H:%M:%S', '%H:%M']
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt).time()
        except (ValueError, TypeError):
            continue
    
    return None

# 輔助函數：解析日期時間
def parse_datetime(datetime_str):
    if not datetime_str or datetime_str.strip() == '':
        return None
        
    formats = ['%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M', '%Y-%m-%d %H:%M']
    for fmt in formats:
        try:
            return datetime.strptime(datetime_str, fmt)
        except (ValueError, TypeError):
            continue
    
    return None

# 輔助函數：解析浮點數
def parse_float(value):
    if not value:
        return 0.0
        
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

# 輔助函數：轉換聯單記錄
def transform_waste_record(record):
    """
    轉換聯單記錄中的日期時間欄位
    """
    # 日期時間欄位對應表
    datetime_keys = {
        '申報日期': ('申報日期', '申報時間'),
        '清運日期': ('清運日期', '清運時間'),
        '運送日期': ('運送日期', '運送時間'),
        '收受日期': ('收受日期', '收受時間'),
        '回收日期': ('回收日期', '回收時間'),
        '處理完成日期': ('處理完成日期', '處理完成時間')
    }
    
    # 建立一個記錄的複本，避免修改原始資料
    transformed_record = record.copy()
    
    # 轉換日期時間欄位
    for original_key, (date_key, time_key) in datetime_keys.items():
        try:
            if original_key in record and record[original_key]:
                # 嘗試分割日期和時間
                datetime_str = record[original_key]
                if ' ' in datetime_str:
                    date_part, time_part = datetime_str.split(' ', 1)
                    transformed_record[date_key] = date_part
                    transformed_record[time_key] = time_part
                else:
                    transformed_record[date_key] = datetime_str
                    transformed_record[time_key] = None
        except Exception:
            # 如果處理失敗，保持原樣
            continue
    
    return transformed_record
from django.db import migrations

def migrate_data_forward(apps, schema_editor):
    """
    將數據從舊的模型結構遷移到新的模型結構
    
    步驟：
    1. 獲取舊模型與新模型的參照
    2. 遍歷所有舊的清除單和再利用單
    3. 為每個舊記錄建立相關的新記錄（事業單位、廢棄物/物質等）
    4. 建立聯單主記錄及其關聯記錄
    """
    # 獲取舊模型
    OldDisposalManifest = apps.get_model('WasteTransport', 'DisposalManifest')
    OldReuseManifest = apps.get_model('WasteTransport', 'ReuseManifest')
    
    # 獲取新模型
    Company = apps.get_model('WasteTransport', 'Company')
    Process = apps.get_model('WasteTransport', 'Process')
    WasteSubstance = apps.get_model('WasteTransport', 'WasteSubstance')
    Carrier = apps.get_model('WasteTransport', 'Carrier')
    Processor = apps.get_model('WasteTransport', 'Processor')
    Reuser = apps.get_model('WasteTransport', 'Reuser')
    Vehicle = apps.get_model('WasteTransport', 'Vehicle')
    Manifest = apps.get_model('WasteTransport', 'Manifest')
    Report = apps.get_model('WasteTransport', 'Report')
    Transport = apps.get_model('WasteTransport', 'Transport')
    Processing = apps.get_model('WasteTransport', 'Processing')
    Recycling = apps.get_model('WasteTransport', 'Recycling')
    DisposalManifestData = apps.get_model('WasteTransport', 'DisposalManifestData')
    ReuseManifestData = apps.get_model('WasteTransport', 'ReuseManifestData')
    
    # 遷移清除單資料
    for old_disposal in OldDisposalManifest.objects.all():
        # 1. 建立或獲取公司資料
        company, _ = Company.objects.get_or_create(
            company_id=old_disposal.company_id,
            defaults={
                'company_name': old_disposal.company_name,
            }
        )
        
        # 2. 建立或獲取製程資料
        process, _ = Process.objects.get_or_create(
            process_code=old_disposal.process_code,
            defaults={
                'process_name': old_disposal.process_name,
            }
        )
        
        # 3. 建立或獲取廢棄物資料
        waste_substance, _ = WasteSubstance.objects.get_or_create(
            substance_code=old_disposal.waste_code,
            substance_type='waste',
            defaults={
                'substance_name': old_disposal.waste_name,
            }
        )
        
        # 4. 建立或獲取清除者資料
        carrier, _ = Carrier.objects.get_or_create(
            carrier_id=old_disposal.carrier_id,
            defaults={
                'carrier_name': old_disposal.carrier_name,
            }
        )
        
        # 5. 建立或獲取處理者資料
        processor, _ = Processor.objects.get_or_create(
            processor_id=old_disposal.processor_id,
            defaults={
                'processor_name': old_disposal.processor_name,
            }
        )
        
        # 6. 建立或獲取車輛資料
        vehicle = None
        if old_disposal.carrier_vehicle:
            vehicle, _ = Vehicle.objects.get_or_create(
                vehicle_id=old_disposal.carrier_vehicle,
                defaults={
                    'vehicle_owner_id': old_disposal.carrier_id,
                    'owner_type': 'carrier',
                }
            )
        
        # 7. 建立聯單主記錄
        manifest, created = Manifest.objects.get_or_create(
            manifest_id=old_disposal.manifest_id,
            defaults={
                'waste_id': old_disposal.waste_id,
                'company': company,
                'process': process,
                'from_storage': old_disposal.from_storage,
                'origin_location': old_disposal.origin_location,
                'manifest_confirmation': old_disposal.manifest_confirmation,
                'manifest_type': 'disposal',
                'is_visible': old_disposal.is_visible,
                'created_at': old_disposal.created_at,
                'updated_at': old_disposal.updated_at,
            }
        )
        
        # 如果記錄已存在但不是此次建立的，則更新欄位值
        if not created:
            manifest.waste_id = old_disposal.waste_id
            manifest.company = company
            manifest.process = process
            manifest.from_storage = old_disposal.from_storage
            manifest.origin_location = old_disposal.origin_location
            manifest.manifest_confirmation = old_disposal.manifest_confirmation
            manifest.manifest_type = 'disposal'
            manifest.is_visible = old_disposal.is_visible
            manifest.created_at = old_disposal.created_at
            manifest.updated_at = old_disposal.updated_at
            manifest.save()
        
        # 8. 建立清除單特有資料
        disposal_data, _ = DisposalManifestData.objects.get_or_create(
            manifest=manifest,
            defaults={
                'waste_substance': waste_substance,
                'waste_code': old_disposal.waste_code,
                'waste_name': old_disposal.waste_name,
            }
        )
        
        # 9. 建立申報單
        report, _ = Report.objects.get_or_create(
            manifest=manifest,
            defaults={
                'report_date': old_disposal.report_date,
                'report_time': old_disposal.report_time,
                'transport_date': old_disposal.transport_date,
                'transport_time': old_disposal.transport_time,
                'reported_weight': old_disposal.reported_weight,
            }
        )
        
        # 10. 建立清運單
        transport, _ = Transport.objects.get_or_create(
            manifest=manifest,
            defaults={
                'carrier': carrier,
                'vehicle': vehicle,
                'delivery_date': old_disposal.delivery_date,
                'delivery_time': old_disposal.delivery_time,
                'carrier_vehicle_number': old_disposal.carrier_vehicle_number,
                'carrier_confirmation': old_disposal.carrier_confirmation,
            }
        )
        
        # 11. 建立處理單
        processing, _ = Processing.objects.get_or_create(
            manifest=manifest,
            defaults={
                'processor': processor,
                'receive_date': old_disposal.receive_date,
                'receive_time': old_disposal.receive_time,
                'intermediate_treatment': old_disposal.intermediate_treatment,
                'processing_completion_date': old_disposal.processing_completion_date,
                'processing_completion_time': old_disposal.processing_completion_time,
                'final_disposal_method': old_disposal.final_disposal_method,
                'processor_confirmation': old_disposal.processor_confirmation,
                'processor_vehicle': old_disposal.processor_vehicle,
                'final_processor_id': old_disposal.final_processor_id,
                'final_processor_name': old_disposal.final_processor_name,
                'entry_date': old_disposal.entry_date,
                'entry_time': old_disposal.entry_time,
                'entry_number': old_disposal.entry_number,
                'final_processor_confirmation': old_disposal.final_processor_confirmation,
                'final_destination': old_disposal.final_destination,
            }
        )
    
    # 遷移再利用單資料
    for old_reuse in OldReuseManifest.objects.all():
        # 1. 建立或獲取公司資料
        company, _ = Company.objects.get_or_create(
            company_id=old_reuse.company_id,
            defaults={
                'company_name': old_reuse.company_name,
            }
        )
        
        # 2. 建立或獲取製程資料
        process, _ = Process.objects.get_or_create(
            process_code=old_reuse.process_code,
            defaults={
                'process_name': old_reuse.process_name,
            }
        )
        
        # 3. 建立或獲取物質資料
        substance, _ = WasteSubstance.objects.get_or_create(
            substance_code=old_reuse.substance_code,
            substance_type='reuse',
            defaults={
                'substance_name': old_reuse.substance_name,
            }
        )
        
        # 4. 建立或獲取清除者資料（如果有）
        carrier = None
        if old_reuse.carrier_id:
            carrier, _ = Carrier.objects.get_or_create(
                carrier_id=old_reuse.carrier_id,
                defaults={
                    'carrier_name': old_reuse.carrier_name or '',
                }
            )
        
        # 5. 建立或獲取再利用者資料（如果有）
        reuser = None
        if old_reuse.reuser_id:
            reuser, _ = Reuser.objects.get_or_create(
                reuser_id=old_reuse.reuser_id,
                defaults={
                    'reuser_name': old_reuse.reuser_name or '',
                    'reuser_nature': old_reuse.reuser_nature,
                }
            )
        
        # 6. 建立或獲取車輛資料
        vehicle = None
        if old_reuse.carrier_vehicle:
            vehicle, _ = Vehicle.objects.get_or_create(
                vehicle_id=old_reuse.carrier_vehicle,
                defaults={
                    'vehicle_owner_id': old_reuse.carrier_id if old_reuse.carrier_id else None,
                    'owner_type': 'carrier',
                }
            )
        
        # 7. 建立聯單主記錄
        manifest, created = Manifest.objects.get_or_create(
            manifest_id=old_reuse.manifest_id,
            defaults={
                'waste_id': old_reuse.waste_id,
                'company': company,
                'process': process,
                'from_storage': old_reuse.from_storage,
                'origin_location': old_reuse.origin_location,
                'manifest_confirmation': old_reuse.manifest_confirmation,
                'manifest_type': 'reuse',
                'is_visible': old_reuse.is_visible,
                'created_at': old_reuse.created_at,
                'updated_at': old_reuse.updated_at,
            }
        )
        
        # 如果記錄已存在但不是此次建立的，則更新欄位值
        if not created:
            manifest.waste_id = old_reuse.waste_id
            manifest.company = company
            manifest.process = process
            manifest.from_storage = old_reuse.from_storage
            manifest.origin_location = old_reuse.origin_location
            manifest.manifest_confirmation = old_reuse.manifest_confirmation
            manifest.manifest_type = 'reuse'
            manifest.is_visible = old_reuse.is_visible
            manifest.created_at = old_reuse.created_at
            manifest.updated_at = old_reuse.updated_at
            manifest.save()
        
        # 8. 建立再利用單特有資料
        reuse_data, _ = ReuseManifestData.objects.get_or_create(
            manifest=manifest,
            defaults={
                'substance': substance,
                'substance_code': old_reuse.substance_code,
                'substance_name': old_reuse.substance_name,
            }
        )
        
        # 9. 建立申報單
        report, _ = Report.objects.get_or_create(
            manifest=manifest,
            defaults={
                'report_date': old_reuse.report_date,
                'report_time': old_reuse.report_time,
                'transport_date': old_reuse.transport_date,
                'transport_time': old_reuse.transport_time,
                'reported_weight': old_reuse.reported_weight,
            }
        )
        
        # 10. 建立清運單（如果有清除者）
        if carrier:
            transport, _ = Transport.objects.get_or_create(
                manifest=manifest,
                defaults={
                    'carrier': carrier,
                    'vehicle': vehicle,
                    'delivery_date': old_reuse.delivery_date,
                    'delivery_time': old_reuse.delivery_time,
                    'carrier_vehicle_number': old_reuse.carrier_vehicle_number,
                    'carrier_confirmation': old_reuse.carrier_confirmation,
                    'carrier_rejection_reason': old_reuse.carrier_rejection_reason,
                }
            )
        
        # 11. 建立回收單（如果有再利用者）
        if reuser:
            recycling, _ = Recycling.objects.get_or_create(
                manifest=manifest,
                defaults={
                    'reuser': reuser,
                    'recovery_date': old_reuse.recovery_date,
                    'recovery_time': old_reuse.recovery_time,
                    'reuse_purpose': old_reuse.reuse_purpose,
                    'reuse_purpose_description': old_reuse.reuse_purpose_description,
                    'reuse_method': old_reuse.reuse_method,
                    'reuse_completion_time': old_reuse.reuse_completion_time,
                    'reuser_confirmation': old_reuse.reuser_confirmation,
                    'reuser_vehicle': old_reuse.reuser_vehicle,
                    'reuser_rejection_reason': old_reuse.reuser_rejection_reason,
                    'source_confirmed': old_reuse.source_confirmed,
                }
            )

def migrate_data_backward(apps, schema_editor):
    """
    回滾數據遷移，將數據從新的模型結構遷移回舊的模型結構
    """
    # 由於這是一個較複雜的遷移，我們不實現回滾功能
    # 如果需要回滾，建議從備份恢復資料
    pass

class Migration(migrations.Migration):
    """
    定義資料遷移操作
    """
    # 依賴於創建新表結構的遷移
    dependencies = [
        ('WasteTransport', '0001_initial'),  # 這裡應該是創建新模型的遷移編號
    ]

    operations = [
        migrations.RunPython(migrate_data_forward, migrate_data_backward),
    ]
/**
 * 醫療廢棄物暨資源管理系統 - 聯單管理模組前端腳本
 * 提供聯單列表、詳細內容顯示、CSV匯入匯出等功能
 */

// 全局變數
let importSessionData = null;
let selectedManifests = new Set();

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化篩選表單顯示/隱藏
    initFilterToggle();
    
    // 初始化聯單卡片點擊事件
    initManifestCardEvents();
    
    // 初始化詳細視圖標籤切換
    initDetailTabs();
    
    // 初始化全選功能
    initSelectAllCheckbox();
    
    // 初始化CSV標籤切換
    initCSVFormatTabs();
    
    // 初始化模態視窗關閉事件
    initModalCloseEvents();
    
    // 初始化幫助按鈕
    document.getElementById('help-button').addEventListener('click', openHelpModal);
});

/**
 * 初始化篩選表單的顯示/隱藏功能
 */
function initFilterToggle() {
    const filterToggleBtn = document.getElementById('filter-toggle');
    const filterForm = document.getElementById('filter-form');
    
    if (!filterToggleBtn || !filterForm) return;
    
    // 一開始隱藏篩選表單
    filterForm.style.display = 'none';
    filterToggleBtn.innerHTML = '<span class="ts-icon is-filter-icon"></span> 顯示篩選條件';
    
    filterToggleBtn.addEventListener('click', function() {
        const isExpanded = filterForm.style.display !== 'none';
        
        if (isExpanded) {
            filterForm.style.display = 'none';
            filterToggleBtn.innerHTML = '<span class="ts-icon is-filter-icon"></span> 顯示篩選條件';
        } else {
            filterForm.style.display = 'block';
            filterToggleBtn.innerHTML = '<span class="ts-icon is-filter-slash-icon"></span> 隱藏篩選條件';
        }
    });
}

/**
 * 初始化聯單卡片點擊事件，加載詳細內容
 */
function initManifestCardEvents() {
    const manifestCards = document.querySelectorAll('.manifest-card');
    
    manifestCards.forEach(card => {
        card.addEventListener('click', function(event) {
            // 如果點擊的是複選框，不要載入詳細資料
            if (event.target.type === 'checkbox' || event.target.tagName === 'LABEL') {
                return;
            }
            
            // 移除所有卡片的活動狀態
            manifestCards.forEach(c => c.classList.remove('is-active'));
            
            // 設置當前卡片為活動狀態
            this.classList.add('is-active');
            
            // 獲取聯單資訊
            const manifestId = this.dataset.manifestId;
            const wasteId = this.dataset.wasteId;
            const type = this.dataset.type;
            
            // 根據類型載入對應的詳細內容
            loadManifestDetail(type, manifestId, wasteId);
        });
    });
}

/**
 * 初始化詳細視圖標籤切換
 */
function initDetailTabs() {
    document.addEventListener('click', function(event) {
        if (event.target.matches('[data-tab-detail]')) {
            const tabs = document.querySelectorAll('[data-tab-detail]');
            const tabIndex = event.target.getAttribute('data-tab-detail');
            
            // 移除所有標籤頁的活動狀態
            tabs.forEach(tab => tab.classList.remove('is-active'));
            
            // 設置當前標籤頁為活動狀態
            event.target.classList.add('is-active');
            
            // 隱藏所有內容區塊
            const segments = document.querySelectorAll('[data-detail-name]');
            segments.forEach(segment => {
                segment.style.display = 'none';
            });
            
            // 顯示對應的內容區塊
            const targetSegment = document.querySelector(`[data-detail-name="${tabIndex}"]`);
            if (targetSegment) {
                targetSegment.style.display = 'block';
            }
        }
    });
}

/**
 * 初始化CSV格式標籤切換
 */
function initCSVFormatTabs() {
    const csvTabs = document.querySelectorAll('[data-tab="csv-disposal"], [data-tab="csv-reuse"]');
    
    csvTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // 移除所有標籤頁的活動狀態
            csvTabs.forEach(t => t.classList.remove('is-active'));
            
            // 設置當前標籤頁為活動狀態
            this.classList.add('is-active');
            
            // 隱藏所有CSV格式說明區塊
            document.querySelectorAll('[data-name="csv-disposal"], [data-name="csv-reuse"]').forEach(segment => {
                segment.style.display = 'none';
            });
            
            // 顯示對應的CSV格式說明區塊
            const targetSegment = document.querySelector(`[data-name="${this.getAttribute('data-tab')}"]`);
            if (targetSegment) {
                targetSegment.style.display = 'block';
            }
        });
    });
}

/**
 * 初始化全選功能
 */
function initSelectAllCheckbox() {
    const selectAllCheckbox = document.getElementById('select-all-manifests');
    if (!selectAllCheckbox) return;
    
    // 更新批量刪除按鈕狀態函數
    function updateBatchDeleteButton() {
        const batchDeleteBtn = document.getElementById('batch-delete-btn');
        if (selectedManifests.size > 0) {
            batchDeleteBtn.classList.remove('is-disabled');
        } else {
            batchDeleteBtn.classList.add('is-disabled');
        }
    }
    
    // 全選/取消全選
    selectAllCheckbox.addEventListener('change', function() {
        const isChecked = this.checked;
        const manifestCheckboxes = document.querySelectorAll('.manifest-checkbox');
        
        manifestCheckboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
            
            const card = checkbox.closest('.manifest-card');
            const manifestId = card.dataset.manifestId;
            const wasteId = card.dataset.wasteId;
            const type = card.dataset.type;
            const key = `${type}|${manifestId}|${wasteId}`;
            
            if (isChecked) {
                selectedManifests.add(key);
            } else {
                selectedManifests.delete(key);
            }
        });
        
        updateBatchDeleteButton();
    });
    
    // 單個勾選改變時更新全選狀態
    document.addEventListener('change', function(event) {
        if (event.target.matches('.manifest-checkbox')) {
            const checkbox = event.target;
            const card = checkbox.closest('.manifest-card');
            const manifestId = card.dataset.manifestId;
            const wasteId = card.dataset.wasteId;
            const type = card.dataset.type;
            const key = `${type}|${manifestId}|${wasteId}`;
            
            if (checkbox.checked) {
                selectedManifests.add(key);
            } else {
                selectedManifests.delete(key);
                
                // 如果有取消勾選，則全選框也取消勾選
                selectAllCheckbox.checked = false;
            }
            
            // 如果所有聯單都被勾選，則全選框也勾選
            const allCheckboxes = document.querySelectorAll('.manifest-checkbox');
            const allChecked = Array.from(allCheckboxes).every(cb => cb.checked);
            
            selectAllCheckbox.checked = allChecked;
            
            updateBatchDeleteButton();
        }
    });
    
    // 批量刪除按鈕
    const batchDeleteBtn = document.getElementById('batch-delete-btn');
    if (batchDeleteBtn) {
        batchDeleteBtn.addEventListener('click', function() {
            if (selectedManifests.size === 0) return;
            
            if (confirm(`確定要移除 ${selectedManifests.size} 筆選取的聯單嗎？`)) {
                showNotification(`已移除 ${selectedManifests.size} 筆聯單`, 'info');
                
                // 清空選取
                selectedManifests.clear();
                
                // 重置全選框和所有勾選框
                selectAllCheckbox.checked = false;
                document.querySelectorAll('.manifest-checkbox').forEach(checkbox => {
                    checkbox.checked = false;
                });
                
                updateBatchDeleteButton();
            }
        });
    }
}

/**
 * 初始化模態視窗關閉事件
 */
function initModalCloseEvents() {
    // 點擊模態視窗外的區域關閉模態視窗
    document.addEventListener('click', function(event) {
        const importModal = document.getElementById('import-modal');
        const conflictModal = document.getElementById('conflict-modal');
        const helpModal = document.getElementById('help-modal');
        
        if (event.target === importModal) {
            closeImportModal();
        } else if (event.target === conflictModal) {
            closeConflictModal();
        } else if (event.target === helpModal) {
            closeHelpModal();
        }
    });
}

/**
 * 加載聯單詳細內容
 * @param {string} type - 聯單類型 (disposal|reuse)
 * @param {string} manifestId - 聯單編號
 * @param {string} wasteId - 廢棄物ID
 */
function loadManifestDetail(type, manifestId, wasteId) {
    const detailContainer = document.getElementById('manifest-detail');
    if (!detailContainer) return;
    
    // 顯示載入中訊息
    detailContainer.innerHTML = `
        <div class="ts-loading is-centered">
            <div class="image"></div>
            <div class="text">加載中...</div>
        </div>
    `;
    
    // 根據類型決定API路徑
    const url = type === 'disposal' 
        ? `/waste_transport/disposal/${manifestId}/${wasteId}`
        : `/waste_transport/reuse/${manifestId}/${wasteId}`;
    
    // 發送AJAX請求
    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('網路錯誤');
        }
        return response.json();
    })
    .then(data => {
        // 更新詳細內容容器
        detailContainer.innerHTML = data.html;
        
        // 初始化詳細視圖標籤功能
        initDetailTabs();
    })
    .catch(error => {
        console.error('載入詳細資料失敗:', error);
        detailContainer.innerHTML = `
            <div class="ts-notice is-negative">
                <div class="content">
                    <div class="header">載入失敗</div>
                    <div class="description">無法載入聯單詳細資料，請重試或聯絡系統管理員。</div>
                </div>
            </div>
        `;
    });
}

/**
 * 清空篩選表單
 */
function clearFilterForm() {
    const form = document.getElementById('manifest-filter-form');
    if (!form) return;
    
    // 重置下拉選單
    form.querySelectorAll('select').forEach(select => {
        select.selectedIndex = 0;
    });
    
    // 清空輸入框
    form.querySelectorAll('input[type="text"], input[type="number"], input[type="date"]').forEach(input => {
        input.value = '';
    });
    
    // 提交表單以重新載入
    form.submit();
}

/**
 * 匯出篩選後的數據
 */
function exportFilteredData() {
    const form = document.getElementById('manifest-filter-form');
    if (!form) return;
    
    // 獲取當前的篩選條件
    const formData = new FormData(form);
    const searchParams = new URLSearchParams(formData);
    
    // 導航到匯出URL
    window.location.href = `/waste_transport/export/?${searchParams.toString()}`;
}

/**
 * 打開匯入CSV模態視窗
 */
function openImportModal() {
    const modal = document.getElementById('import-modal');
    if (!modal) return;
    
    modal.classList.add('is-visible');
    
    // 重置表單
    const form = document.getElementById('csv-import-form');
    if (form) {
        form.reset();
    }
    
    // 重置匯入資料
    importSessionData = null;
}

/**
 * 關閉匯入CSV模態視窗
 */
function closeImportModal() {
    const modal = document.getElementById('import-modal');
    if (!modal) return;
    
    modal.classList.remove('is-visible');
}

/**
 * 打開衝突解決模態視窗
 */
function openConflictModal(conflictData) {
    const modal = document.getElementById('conflict-modal');
    if (!modal) return;
    
    // 設置衝突記錄
    const recordsContainer = document.getElementById('conflict-records-container');
    if (recordsContainer) {
        // 構建衝突記錄HTML
        let html = `<p>以下 ${conflictData.length} 筆記錄與現有資料發生衝突：</p>`;
        
        conflictData.forEach((record, index) => {
            html += `
                <div class="ts-box has-top-spaced">
                    <div class="ts-content">
                        <div class="ts-header is-heavy">${index + 1}. 聯單編號: ${record.manifest_id} (廢棄物ID: ${record.waste_id})</div>
                        <div class="ts-text">事業機構名稱: ${record.company_name}</div>
                        <div class="ts-text has-bottom-spaced-small">申報日期: ${record.report_date}</div>
                        
                        <table class="conflict-table">
                            <thead>
                                <tr>
                                    <th>欄位名稱</th>
                                    <th>現有資料</th>
                                    <th>匯入資料</th>
                                </tr>
                            </thead>
                            <tbody>
            `;
            
            // 對比現有資料和新資料
            const allFields = new Set([
                ...Object.keys(record.existing_data || {}),
                ...Object.keys(record.new_data || {})
            ]);
            
            for (const field of allFields) {
                const existingValue = (record.existing_data && record.existing_data[field]) || '-';
                const newValue = (record.new_data && record.new_data[field]) || '-';
                const isDifferent = existingValue !== newValue && existingValue !== '-' && newValue !== '-';
                
                html += `
                    <tr>
                        <td>${field}</td>
                        <td ${isDifferent ? 'class="different-value"' : ''}>${existingValue}</td>
                        <td ${isDifferent ? 'class="different-value"' : ''}>${newValue}</td>
                    </tr>
                `;
            }
            
            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        });
        
        recordsContainer.innerHTML = html;
    }
    
    modal.classList.add('is-visible');
}

/**
 * 關閉衝突解決模態視窗
 */
function closeConflictModal() {
    const modal = document.getElementById('conflict-modal');
    if (!modal) return;
    
    modal.classList.remove('is-visible');
    
    // 清除衝突資料
    importSessionData = null;
}

/**
 * 打開使用說明模態視窗
 */
function openHelpModal() {
    const modal = document.getElementById('help-modal');
    if (!modal) return;
    
    modal.classList.add('is-visible');
}

/**
 * 關閉使用說明模態視窗
 */
function closeHelpModal() {
    const modal = document.getElementById('help-modal');
    if (!modal) return;
    
    modal.classList.remove('is-visible');
}

/**
 * 提交匯入表單
 */
function submitImport() {
    const form = document.getElementById('csv-import-form');
    if (!form) return;
    
    const formData = new FormData(form);
    const submitBtn = document.getElementById('import-submit-btn');
    
    // 禁用按鈕，顯示載入中
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<div class="ts-loading is-small is-white"></div> 匯入中...';
    }
    
    // 發送AJAX請求
    fetch('/waste_transport/import/', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('網路錯誤');
        }
        return response.json();
    })
    .then(data => {
        // 恢復按鈕狀態
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '匯入';
        }
        
        if (data.success) {
            // 匯入成功
            closeImportModal();
            showNotification(data.message, 'positive');
            
            // 重新載入頁面以顯示新資料
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else if (data.conflict) {
            // 有衝突，顯示衝突解決對話框
            closeImportModal();
            importSessionData = data.import_data;
            openConflictModal(data.conflicting_records);
        } else {
            // 其他錯誤
            showNotification(data.error || '匯入失敗', 'negative');
        }
    })
    .catch(error => {
        console.error('匯入失敗:', error);
        
        // 恢復按鈕狀態
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '匯入';
        }
        
        showNotification('匯入失敗，請重試', 'negative');
    });
}

/**
 * 解決衝突並繼續匯入
 */
function resolveConflicts() {
    if (!importSessionData) {
        closeConflictModal();
        return;
    }
    
    // 獲取選擇的衝突解決方式
    const resolution = document.querySelector('input[name="conflict_resolution"]:checked').value;
    
    // 準備請求資料
    const requestData = {
        ...importSessionData,
        conflict_resolution: resolution
    };
    
    const resolveBtn = document.getElementById('resolve-conflicts-btn');
    
    // 禁用按鈕，顯示載入中
    if (resolveBtn) {
        resolveBtn.disabled = true;
        resolveBtn.innerHTML = '<div class="ts-loading is-small is-white"></div> 處理中...';
    }
    
    // 發送AJAX請求
    fetch('/waste_transport/resolve_conflicts/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('網路錯誤');
        }
        return response.json();
    })
    .then(data => {
        // 恢復按鈕狀態
        if (resolveBtn) {
            resolveBtn.disabled = false;
            resolveBtn.innerHTML = '確認處理';
        }
        
        if (data.success) {
            // 處理成功
            closeConflictModal();
            showNotification(data.message, 'positive');
            
            // 重新載入頁面以顯示新資料
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            // 處理失敗
            showNotification(data.error || '處理衝突失敗', 'negative');
        }
    })
    .catch(error => {
        console.error('處理衝突失敗:', error);
        
        // 恢復按鈕狀態
        if (resolveBtn) {
            resolveBtn.disabled = false;
            resolveBtn.innerHTML = '確認處理';
        }
        
        showNotification('處理衝突失敗，請重試', 'negative');
    });
}

/**
 * 顯示通知訊息
 * @param {string} message - 訊息內容
 * @param {string} type - 訊息類型 (positive|negative|info)
 */
function showNotification(message, type = 'info') {
    const snackbar = document.getElementById('notification-snackbar');
    if (!snackbar) return;
    
    // 設置樣式
    let bgColor = 'var(--ts-gray-800)';
    if (type === 'positive') {
        bgColor = 'var(--ts-positive-600)';
    } else if (type === 'negative') {
        bgColor = 'var(--ts-negative-600)';
    } else if (type === 'info') {
        bgColor = 'var(--ts-primary-600)';
    }
    
    snackbar.style.backgroundColor = bgColor;
    
    // 設置訊息
    const contentElement = snackbar.querySelector('.content');
    if (contentElement) {
        contentElement.textContent = message;
    }
    
    // 顯示通知
    snackbar.classList.add('show');
    
    // 設置自動關閉計時器
    setTimeout(closeNotification, 3000);
}

/**
 * 關閉通知
 */
function closeNotification() {
    const snackbar = document.getElementById('notification-snackbar');
    if (!snackbar) return;
    
    snackbar.classList.remove('show');
}

/**
 * 獲取Cookie值
 * @param {string} name - Cookie名稱
 * @returns {string} Cookie值
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
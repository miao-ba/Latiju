from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.timezone import localtime
from django.views.decorators.csrf import csrf_exempt

from MedicalWasteManagementSystem.permissions import *

# Create your views here.
def index(request):
    return render(request, 'main_menu.html')

def view_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            pass

    # 傳遞 login_error 給模板
    return render(request, 'account/login.html')

def view_logout(request):
    logout(request)
    return redirect('main')

# 左側帳號選單欄
@permission_required('moderator')
def view_account_manage_list(request):
    # 定義群組名稱的順序及其對應的圖示
    permission_order = ['root', 'moderator', 'staff', 'registrar', 'importer']
    permission_icons = {
        'root': 'gear',
        'moderator': 'user-shield',
        'staff': 'users',
        'registrar': 'file-pen',
        'importer': 'file-import',
    }

    # 查詢群組，並在 Python 中排序
    permissions = Group.objects.filter(name__in=permission_order)
    groups = sorted(permissions, key=lambda g: permission_order.index(g.name))

    # 建立群組與成員的映射
    permission_types = {group.name: group.user_set.all() for group in groups}

    # 確保所有群組名稱都存在於字典中，即使成員為空
    permission_types = {name: permission_types.get(name, []) for name in permission_order}

    # print(permission_types)  # 確認群組名稱
    # print(permission_icons)   # 確認圖標對應的字典

    # 傳遞至模板
    return render(request, 'account/manage.html', {
        'permission_icons': permission_icons,
        'permission_types': permission_types,
        'current_user': request.user
    })

# 右側帳號資訊欄
@permission_required('moderator')
def view_account_manage_info(request, account_id):
    try:
        account = User.objects.get(username=account_id)
        account_data = {
            'username': account.username,
            'first_name': account.first_name,
            'last_name': account.last_name,
            'group': account.groups.first().name if account.groups.exists() else "",
            'is_superuser': account.is_superuser,
            'is_staff': account.is_staff,
            'date_joined': localtime(account.date_joined).strftime("%Y-%m-%d %H:%M:%S.%f %z"),
            'last_login': localtime(account.last_login).strftime("%Y-%m-%d %H:%M:%S.%f %z"),
        }
        return JsonResponse(account_data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Account not found'}, status=404)

# 帳號刪除
@csrf_exempt
@permission_required('moderator')
def delete_account(request, username):
    if request.method == 'DELETE':
        try:
            with transaction.atomic():  # 使用交易確保一致性
                current_user = request.user
                target_user = User.objects.get(username=username)

                if target_user == current_user:
                    return JsonResponse({'success': False, 'error': '不能刪除自己的帳號'}, status=403)

                current_user_group_name = current_user.groups.first().name if current_user.groups.exists() else None
                target_user_group_name = target_user.groups.first().name if target_user.groups.exists() else None

                if current_user_group_name not in GROUP_HIERARCHY or target_user_group_name not in GROUP_HIERARCHY:
                    return JsonResponse({'success': False, 'error': '群組配置無效，請聯繫管理員'}, status=500)

                if GROUP_HIERARCHY[current_user_group_name] <= GROUP_HIERARCHY[target_user_group_name]:
                    return JsonResponse({'success': False, 'error': '權限不足，無法刪除此帳號'}, status=403)

                target_user.delete()
                return JsonResponse({'success': True})

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': '目標帳號不存在'}, status=404)
        except Exception as e:
            # 記錄其他異常並返回錯誤
            print(f"刪除帳戶時發生錯誤：{e}")
            return JsonResponse({'success': False, 'error': '伺服器內部錯誤'}, status=500)
    return JsonResponse({'success': False, 'error': '無效的請求方法'}, status=405)

@permission_required('moderator')
def view_account_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        permission = request.POST.get('permission')

        # print(username, email, first_name, last_name)
        # print(password, permission)

        # 檢查必填項目
        if not username or not password or not permission:
            return JsonResponse({'success': False, 'error': '請填寫所有必填項目！'})

        try:
            # 創建用戶
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )

            # 確認群組是否存在並分配
            user_permission = Group.objects.get(name=permission)
            user.groups.add(user_permission)

            return JsonResponse({'success': True})
        except (Exception, ValidationError) as e:
            # 返回錯誤訊息
            return JsonResponse({'success': False, 'error': str(e)})

    # 動態調整下拉選單
    user = request.user
    permission_options = []
    if user.groups.filter(name='root').exists():
        permission_options = ['moderator', 'staff', 'registrar', 'importer']
    elif user.groups.filter(name='moderator').exists():
        permission_options = ['registrar', 'importer']

    return render(request, 'account/register.html', {'permission_options': permission_options})
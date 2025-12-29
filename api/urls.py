#api/urls.py
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import *

urlpatterns = [
    # USER
    # Ini memberitahu Django, "Jika sisa URL-nya adalah 'login/',
    # jalankan fungsi 'obtain_auth_token'"
    path('login/', obtain_auth_token, name='api_login'),
    path('user/create', RegisterView.as_view(), name='api_create_user'),
    path('users/', GetUserAllView.as_view(), name='api_get_all_user'),
    path('user/<str:email>/', GetUserByEmail.as_view(), name='api_get_user_by_email'),
    path('user/delete/<str:email>/', DeleteAllUserByEmail.as_view(), name='api_delete_user_by_email'),
    path('user/update/<str:email>/', UpdateUserView.as_view(), name='api_update_user_by_email'),
    path('user/me', GetUserIdView.as_view(), name='api_get_id_user'),

    # CATEGORY
    path('category/create/', CreateCategoryView.as_view(), name='api_create_category'),
    # path('category/create/', CategoryView.as_view(), name='api_create_category'),

    # REIMBURSE
    path('reimbursements/', GetReimburseAllView.as_view(), name='api_reimbursement_list'),
    path('reimbursements/<int:pk>', GetReimburseByIdView.as_view(), name='api_reimbursement_by_id'),
    path('reimbursements/user/', GetReimburseUserView.as_view(), name='api_user_reimbursement'),
    path('reimbursements/thisMonth/', GetReimburseThisMonthView.as_view(), name='api_this_month_reimbursement'),
    path('reimbursements/thisYear/', GetReimburseThisYearView.as_view(), name='api_this_year_reimbursement'),
    path('reimbursements/thisYear/<str:email>/', GetReimburseThisYearViewPerUser.as_view(), name='api_this_year_reimbursement_per_user'),
    path('reimbursements/thisMonth/<str:email>/', GetReimburseByEmailThisMonthView.as_view(), name='api_this_month_reimbursement_per_user_email'),
    path('reimbursements/create/', CreateReimburseView.as_view(), name='api_create_reimbursement'),
    path('reimbursements/update/<int:pk>', UpdateReimburseView.as_view(), name='api_update_reimbursement'),
    path('reimbursements/delete/<int:pk>', DeleteReimburseByIdView.as_view(), name='api_delete_reimbursement'),

    # REIMBURSE ITEM
    path('items/', GetReimburseItemView.as_view(), name='api_reimburse_item_list'),
    path('item/create', CreateReimburseItemView.as_view(), name='api_create_reimburse_item'),
    path('item/<int:reimburse_id>', GetReimburseItemByIdView.as_view(), name='api_reimburse_item_list_by_id'),

    # FINANCE
    path('finance/create/', CreateFinanceManagementView.as_view(), name='finance-create'),
    path('finance/update/', UpdateFinanceManagementView.as_view(), name='finance-update'),
    path('finance/user/<str:email>/', GetFinanceManagementByUserView.as_view(), name='get-finance-user'),

    # SITE SETTING
    path('settings/', getSiteSettingsAll.as_view(), name='get_setting_all'),
    path('settings/<str:category>/', getSiteSettingsByCategory.as_view(), name='get_setting_by_category'),
    path('settings/<str:category>/<str:key>/', getSiteSettingByCategoryAndKey.as_view(), name='get_setting_by_category_and_key'),
    path('setting/create/', CreateSiteSettingView.as_view(), name='create_setting'),
    path('setting/update/', UpdateSettingView.as_view(), name='update_setting'),
    path('setting/delete/', DeleteSiteSettingByCategoryAndKeyView.as_view(), name='delete_setting'),

    # SLIP SALARY
    path('slip-salary/', GetSlipSalaryAllView.as_view(), name='get_slip_salary_all'),

    # OVERTIME LOG
    path('overtimelog/', GetOvertimeLogAllView.as_view(), name='get_all_overtime_log'),
    path('overtimelog/me/', GetOvertimeLogByTokenView.as_view(), name='get_all_my_overtime_log'),
    path('overtimelog/thisMonth/me/', GetOvertimeLogByTokenThisMonthView.as_view(), name='get_all_my_overtime_log_this_month'),
    path('overtimelog/<str:email>/', GetOvertimeLogByUserView.as_view(), name='get_all_overtime_log_by_user'),
    path('overtimelog/thisMonth/<str:email>/', GetOvertimeLogByUserThisMonthView.as_view(), name='get_all_overtime_log_by_user_this_month'),
    path('overtime/create/', CreateOvertimeLogView.as_view(), name='create_overtime_log'),
    path('overtime/update/<pk>/', UpdateOvertimeLogView.as_view(), name='update_overtime_log_by_token'),
    path('overtime/delete/<pk>/', DeleteOvertimeLogView.as_view(), name='delete_overtime_log'),

    # EMPLOYEE
    path('employee/', GetEmployeeAllView.as_view(), name='get_all_employee'),
    path('employee/me/', GetMyEmployeeView.as_view(), name='get_my_employee_data'),
    path('employee/get/<str:email>/', GetEmployeeByUserView.as_view(), name='get_employee_by_user'),
    path('employee/create/<str:email>/', CreateEmployeeView.as_view(), name='create_employee'),
    path('employee/update/<str:email>/', UpdateEmployeeView.as_view(), name='update_employee_data'),

    # BANK ACCOUNT
    path('bankAccount/', getBankAccountAllView.as_view(), name='get_all_bank_account'),
    path('bankAccount/me/', getMyBankAccountView.as_view(), name='get_my_bank_account'),
    path('bankAccount/<str:email>/', getBankAccountByUserView.as_view(), name='get_bank_account_by_user'),
    path('bankAccount/create/self/', createMyBankAccountView.as_view(), name='create_my_bank_account'),
    path('bankAccount/create/<str:email>/', createBankAccountView.as_view(), name='create_bank_account'),
    path('bankAccount/update/<int:pk>/', updateBankAccountView.as_view(), name='update_bank_account'),
    path('bankAccount/delete/<int:pk>/', deleteBankAccountView.as_view(), name='delete_bank_account'),

    # SLIP SALARY
    path('slipSalary/', getSlipSalaryAllView.as_view(), name='get_all_slip_salary'),
    path('slipSalary/create/<str:email>/', CreateSlipSalaryByUserView.as_view(), name='create_slip_salary_by_user'),
    path('slipSalary/delete/<str:email>/', DeleteSlipSalaryByUserView.as_view(), name='delete_slip_salary_by_user'),
]



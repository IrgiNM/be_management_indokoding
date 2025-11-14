#api/urls.py
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import *

urlpatterns = [
    # Ini memberitahu Django, "Jika sisa URL-nya adalah 'login/',
    # jalankan fungsi 'obtain_auth_token'"
    path('login/', obtain_auth_token, name='api_login'),
    path('user/create', RegisterView.as_view(), name='api_create_user'),
    path('users/', GetUserAllView.as_view(), name='api_get_all_user'),
    path('user/me', GetUserIdView.as_view(), name='api_get_id_user'),

    path('category/create/', CreateCategoryView.as_view(), name='api_create_category'),
    # path('category/create/', CategoryView.as_view(), name='api_create_category'),

    path('reimbursements/', GetReimburseAllView.as_view(), name='api_reimbursement_list'),
    path('reimbursements/<int:pk>', GetReimburseByIdView.as_view(), name='api_reimbursement_by_id'),
    path('reimbursements/user/', GetReimburseUserView.as_view(), name='api_user_reimbursement'),
    path('reimbursements/thisMonth/', GetReimburseThisMonthView.as_view(), name='api_this_month_reimbursement'),
    path('reimbursements/create/', CreateReimburseView.as_view(), name='api_create_reimbursement'),
    path('reimbursements/update/<int:pk>', UpdateReimburseView.as_view(), name='api_update_reimbursement'),
    path('reimbursements/delete/<int:pk>', DeleteReimburseByIdView.as_view(), name='api_delete_reimbursement'),

    path('items/', GetReimburseItemView.as_view(), name='api_reimburse_item_list'),
    path('item/create', CreateReimburseItemView.as_view(), name='api_create_reimburse_item'),
    path('item/<int:reimburse_id>', GetReimburseItemByIdView.as_view(), name='api_reimburse_item_list_by_id'),
]


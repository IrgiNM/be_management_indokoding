#api/urls.py
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import *

urlpatterns = [
    # Ini memberitahu Django, "Jika sisa URL-nya adalah 'login/',
    # jalankan fungsi 'obtain_auth_token'"
    path('login/', obtain_auth_token, name='api_login'),
    path('createUser/', RegisterView.as_view(), name='api_create_user'),
    path('getUserAll/', GetUserAllView.as_view(), name='api_get_all_user'),

    path('category/create/', CreateCategoryView.as_view(), name='api_create_category'),

    path('reimbursements/', GetReimburseAllView.as_view(), name='api_reimbursement_list'),
    path('reimbursements/user/', GetReimburseUserView.as_view(), name='api_user_reimbursement'),
    path('reimbursements/create/', CreateReimburseView.as_view(), name='api_create_reimbursement'),
    path('reimbursements/update/<int:pk>', UpdateReimburseView.as_view(), name='api_update_reimbursement'),

    path('createReimbursementItem/', CreateReimburseItemView.as_view(), name='api_create_reimburse_item'),
]


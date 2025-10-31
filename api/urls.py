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

    path('craeteCategory/', CreateCategoryView.as_view(), name='api_create_category'),

    path('reimbursements/', ReimbursementListView.as_view(), name='api_reimbursement_list'),
    path('createReimbursement/', CreateReimburseView.as_view(), name='api_create_reimbursement'),

    path('createReimbursementItem/', CreateReimburseItemView.as_view(), name='api_create_reimburse_item'),
]


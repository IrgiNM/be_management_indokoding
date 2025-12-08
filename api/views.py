from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from api.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .helpers import UserCheckRole
from datetime import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404


# USER
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        role = UserCheckRole(request.user)
        if not role:
            return Response({'error': 'Failed you not staff'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

class GetUserAllView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        role = UserCheckRole(request.user)
        if not role:
            return Response({'error': 'Failed you not staff'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
    
class GetUserByEmail(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,) 
    serializer_class = UserSerializer
    lookup_field = 'email'

    def get_queryset(self):
        return User.objects.all()
    
class DeleteAllUserByEmail(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        email = kwargs.get('email')

        users = User.objects.filter(email=email)
        count = users.count()

        if count == 0:
            return Response({"message": "Tidak ada user dengan email tersebut."}, status=404)

        users.delete()
        return Response({"message": f"{count} user berhasil dihapus."})

class GetUserIdView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user # biar bisa ngambil dari header yang dikirim
    
class UpdateUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    lookup_field = "email"


# CATEGORY
class CreateCategoryView(generics.CreateAPIView):
    queryset = Category.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = CategorySerializers

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')

        # kalau tidak ada field 'name', kembalikan error
        if not name:
            return Response({'error': 'Field "name" wajib diisi'}, status=status.HTTP_400_BAD_REQUEST)

        # cek apakah kategori sudah ada
        existing_category = Category.objects.filter(name=name).first()

        if existing_category:
            # kalau sudah ada, return data kategori itu (tanpa buat baru)
            serializer = self.get_serializer(existing_category)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # kalau belum ada, buat baru seperti biasa
        return super().create(request, *args, **kwargs)


# REIMBURSE
class GetReimburseByEmailThisMonthView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,) 
    serializer_class = ReimbursementSerializers
    lookup_field = 'email'
    def get_queryset(self):
        email = self.kwargs.get('email')
        now = datetime.now()
        queryset = Reimbursement.objects.filter(
            user__email=email,
            created_at__year=now.year,
            created_at__month=now.month
        )
        return queryset
    
class GetReimburseAllView(generics.ListAPIView):
    queryset = Reimbursement.objects.all().order_by('-created_at')
    permission_classes = [IsAuthenticated]
    serializer_class = ReimbursementSerializers

class DeleteReimburseByIdView(generics.DestroyAPIView):
    queryset = Reimbursement.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ReimbursementSerializers

class GetReimburseByIdView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated] 
    serializer_class = ReimbursementSerializers
    def get_queryset(self):
        reimburse_id = self.kwargs['pk']
        return Reimbursement.objects.filter(id=reimburse_id)

class GetReimburseUserView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,) 
    serializer_class = ReimbursementSerializers

    def get_queryset(self):
        user = self.request.user
        
        # Ambil param optional dari query string
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        queryset = Reimbursement.objects.filter(user=user)

        # Filter jika param diberikan
        if year:
            queryset = queryset.filter(created_at__year=year)
        if month:
            queryset = queryset.filter(created_at__month=month)

        return queryset.order_by('-created_at')

class GetReimburseThisMonthView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,) 
    serializer_class = ReimbursementSerializers
    def get_queryset(self):
        now = datetime.now()
        return Reimbursement.objects.filter(
            created_at__year=now.year,
            created_at__month=now.month
        ).order_by('-created_at')
    
class GetReimburseThisYearView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,) 
    serializer_class = ReimbursementSerializers
    def get_queryset(self):
        now = datetime.now()
        return Reimbursement.objects.filter(
            created_at__year=now.year,
        ).order_by('-created_at')
    
class GetReimburseThisYearViewPerUser(generics.ListAPIView):
    permission_classes = (IsAuthenticated,) 
    serializer_class = ReimbursementSerializers
    def get_queryset(self):
        now = timezone.now()
        email = self.kwargs.get('email')
        if not email:
            return Reimbursement.objects.none()
        return Reimbursement.objects.filter(
            created_at__year=now.year,
            user__email=email
        ).order_by('-created_at')

class CreateReimburseView(generics.CreateAPIView):
    queryset = Reimbursement.objects.all()
    permission_classes = [permissions.IsAuthenticated] 
    serializer_class = ReimbursementSerializers
    parser_classes = (MultiPartParser, FormParser)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UpdateReimburseView(generics.UpdateAPIView):
    queryset = Reimbursement.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ReimbursementSerializers

class ReimbursementListView(generics.ListAPIView):
    serializer_class = ReimbursementSerializers # Pakai resep plural
    permission_classes = [IsAuthenticated] # Wajib login
    
    def get_queryset(self):
        # Cuma tampilkan data milik user yang sedang login
        # dan urutkan dari yang paling baru
        return Reimbursement.objects.filter(user=self.request.user).order_by('-created_at')
    

# REIMBURSEMENT ITEM
class CreateReimburseItemView(generics.CreateAPIView):
    queryset = ReimbursementItems.objects.all()
    permission_classes = (AllowAny,) 
    serializer_class = ReimbursementItemSerializers

class GetReimburseItemView(generics.ListAPIView):
    queryset = ReimbursementItems.objects.all()
    permission_classes = [IsAuthenticated] 
    serializer_class = ReimbursementItemSerializers

class GetReimburseItemByIdView(generics.ListAPIView):
    permission_classes = [IsAuthenticated] 
    serializer_class = ReimbursementItemSerializers
    def get_queryset(self):
        reimburse_id = self.kwargs['reimburse_id']
        return ReimbursementItems.objects.filter(reimbursement=reimburse_id)


# FINANCE MANAGEMENT
class GetFinanceManagementByUserView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,) 
    serializer_class = FinanceManagementSerializers
    lookup_field = 'email'
    def get_object(self):
        email = self.kwargs.get('email')
        now = datetime.now()
        queryset = FinanceManagement.objects.filter(
            user__email=email,
            created_at__year=now.year,
            created_at__month=now.month
        ).first()
        return queryset
    
class CreateFinanceManagementView(generics.CreateAPIView):
    queryset = FinanceManagement.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FinanceManagementSerializers

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        enabled_health = request.data.get('enable_bpjs_health') in [True, 'true', '1']
        enabled_employ = request.data.get('enable_bpjs_employment') in [True, 'true', '1']
        enabled_tax = request.data.get('enable_tax') in [True, 'true', '1']
        percentage_health = float(request.data.get('bpjs_health_rate_percentage', 0))
        percentage_employ = float(request.data.get('bpjs_employment_rate_percentage', 0))
        percentage_tax = float(request.data.get('tax_rate_percentage', 0))

        if not email:
            return Response(
                {'error': 'Field "email" wajib diisi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # jika BPJS tidak enabled, rate harus 0
        new_percentage_health = 0 if not enabled_health else percentage_health
        new_percentage_employ = 0 if not enabled_employ else percentage_employ
        new_percentage_tax = 0 if not enabled_tax else percentage_tax

        # cari user
        user = get_object_or_404(User, email=email)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=user,
            bpjs_health_rate_percentage=new_percentage_health,
            bpjs_employment_rate_percentage=new_percentage_employ,
            tax_rate_percentage=new_percentage_tax,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateFinanceManagementView(generics.UpdateAPIView):
    queryset = FinanceManagement.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FinanceManagementSerializers

    def get_object(self):
        email = self.request.data.get("email")

        if not email:
            raise ValidationError("email harus dikirim")
        
        try:
            return FinanceManagement.objects.get(
                user__email = email,
                is_active = True
            )
        except FinanceManagement.DoesNotExist:
            if User.objects.filter(email=email).exists():
                raise ValidationError('data tidak ada yang sedang active')
            else:
                raise ValidationError('data user yang dicari tidak ada')


# SITE SETTING
class CreateSiteSettingView(generics.CreateAPIView):
    queryset = SiteSetting.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SiteSettingSerializers

class UpdateSettingView(generics.UpdateAPIView):
    queryset = SiteSetting.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SiteSettingSerializers

    def get_object(self):
        data_category = self.request.data.get("category")
        data_key = self.request.data.get("key")

        if not data_category or not data_key:
            raise ValidationError("category dan key harus dikirim")
        
        try:
            return SiteSetting.objects.get(
                category = data_category,
                key = data_key
            )
        except SiteSetting.DoesNotExist:
            raise ValidationError('data category dan key yang dicari tidak ada')
        
class DeleteSiteSettingByCategoryAndKeyView(generics.DestroyAPIView):
    queryset = SiteSetting.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SiteSettingSerializers

    def get_object(self):
        category = self.request.data.get("category")
        key = self.request.data.get("key")

        if not category or not key:
            raise ValidationError("category dan key harus dikirim")

        try:
            return SiteSetting.objects.get(category=category, key=key)
        except SiteSetting.DoesNotExist:
            raise ValidationError("data tidak ditemukan")
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "data berhasil dihapus"}, status=200)
        
class getSiteSettingsAll(generics.ListAPIView):
    queryset = SiteSetting.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SiteSettingSerializers

class getSiteSettingsByCategory(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SiteSettingSerializers

    def get_queryset(self):
        category = self.kwargs.get("category")

        if not category:
            raise ValidationError("category harus dikirim")
        
        obj = SiteSetting.objects.filter(
            category = category
        )

        if not obj.exists():
            raise ValidationError("data tidak ada")

        return obj
    
class getSiteSettingByCategoryAndKey(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SiteSettingSerializers

    def get_object(self):
        category = self.kwargs.get("category")
        key = self.kwargs.get("key")

        if not category:
            raise ValidationError("category harus dikirim")
        if not key:
            raise ValidationError("key harus dikirim")
        
        obj = SiteSetting.objects.filter(
            category = category,
            key = key
        ).first()

        if not obj:
            raise ValidationError("data tidak ada")

        return obj
        

        
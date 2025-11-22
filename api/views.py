from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from api.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .helpers import UserCheckRole
from datetime import datetime
from django.utils import timezone


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

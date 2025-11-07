from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from api.serializers import *
from rest_framework.permissions import IsAuthenticated


# USER
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

class GetUserAllView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GetUserIdView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user # biar bisa ngambil dari header yang dikirim


# CATEGORY
class CreateCategoryView(generics.CreateAPIView):
    queryset = Category.objects.all()
    permission_classes = (AllowAny,) 
    serializer_class = CategorySerializers


# REIMBURSE
class GetReimburseAllView(generics.ListAPIView):
    queryset = Reimbursement.objects.all().order_by('-created_at')
    permission_classes = (IsAuthenticated)
    serializer_class = ReimbursementSerializers

class GetReimburseUserView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,) 
    serializer_class = ReimbursementSerializers
    def get_queryset(self):
        user = self.request.user
        return Reimbursement.objects.filter(user=user).order_by('-created_at')

class CreateReimburseView(generics.CreateAPIView):
    queryset = Reimbursement.objects.all()
    permission_classes = (AllowAny,) 
    serializer_class = ReimbursementSerializers

class UpdateReimburseView(generics.UpdateAPIView):
    queryset = Reimbursement.objects.all()
    permission_classes = (AllowAny,) 
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

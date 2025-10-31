from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from api.serializers import *
from rest_framework.permissions import IsAuthenticated


# USER
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # Izinkan siapa saja (tanpa login) untuk akses
    serializer_class = UserSerializer

class GetUserAllView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# CATEGORY
class CreateCategoryView(generics.CreateAPIView):
    queryset = Category.objects.all()
    permission_classes = (AllowAny,) 
    serializer_class = CategorySerializers


# REIMBURSE
class CreateReimburseView(generics.CreateAPIView):
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

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {
            'password': {'write_only': True},
             'email': {'required': True} # 'write_only' artinya password tidak akan
                                             # dikirim balik di respon (biar aman)
        }

    def create(self, validated_data):
        # Kita pakai create_user agar password-nya di-hash (dienkripsi)
        # BUKAN disimpan sebagai teks biasa. Ini WAJIB!
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
    def validate(self, data):
        emailData = data.get('email')
        if User.objects.filter(email=emailData).exists():
            raise serializers.ValidationError("email udah ada")
        return data
    
    # def validate_username(self, value):
    #     if User.objects.filter(username=value).exists():
    #         raise serializers.ValidationError("username udah ada")
    #     return
    # ini tidak usah karena sudah ada darisananya
        
class ReimbursementSerializers(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Reimbursement
        fields = [
            'id',
            'user',
            'user_detail',
            'title',
            'total_amount',
            'created_at',
            'updated_at',
            'description',
            'image',
            'status'
        ]

class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'created_at'
        ]

    def validate(self, data):
        nameData = data.get('name')
        if Category.objects.filter(name=nameData).exists():
            # raise serializers.ValidationError("category udah ada")
            return Category.objects.get(name=nameData)
        return data

# class CategorySerializers(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'created_at']

#     def create(self, validated_data):
#         category, created = Category.objects.get_or_create(
#             name=validated_data.get('name')
#         )
#         return category



class ReimbursementItemSerializers(serializers.ModelSerializer):
    reimbursement_detail = ReimbursementSerializers(source='reimbursement', read_only=True)
    category_detail = CategorySerializers(source='category', read_only=True)

    class Meta:
        model = ReimbursementItems
        fields = [
            'id',
            'reimbursement',
            'reimbursement_detail',
            'category',
            'category_detail',
            'item_amount',
            'created_at',
            'updated_at'
        ]
    


    
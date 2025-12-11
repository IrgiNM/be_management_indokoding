from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'is_staff']
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
    
    def update(self, instance, validated_data):
        # Update username / email / is_staff
        for attr, value in validated_data.items():
            if attr == 'password':
                # pakai set_password agar di-hash
                instance.set_password(value)
            else:
                setattr(instance, attr, value)

        instance.save()
        return instance

    def validate(self, data):
        emailData = data.get('email')
        if emailData:
            # Pastikan email unik, tetapi abaikan dirinya sendiri saat update
            user_id = self.instance.id if self.instance else None
            if User.objects.filter(email=emailData).exclude(id=user_id).exists():
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
    
class FinanceManagementSerializers(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = FinanceManagement
        fields = '__all__'

class SlipSalarySerializers(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = SalarySlip
        fields = '__all__'

class SiteSettingSerializers(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        fields = '__all__'

    def validate(self,data):
        category_data = data.get('category')
        key_data = data.get('key')

        instance = self.instance

        qs = SiteSetting.objects.filter(
            category = category_data,
            key = key_data
        )

        if instance:
            qs = qs.exclude(id=instance.id)
        
        if qs.exists():
            raise serializers.ValidationError("Setting ini sudah ada (kategori + key harus unik).")

        return data
    
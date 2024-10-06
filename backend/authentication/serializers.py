from .models import UserProfile
from rest_framework import serializers
from cryptography.fernet import Fernet
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user or self.context['request'].user

        if not user.user_email_verified:
            raise InvalidToken('No active account found with the given credentials')
        if user.user_email_verified and user.is_adminuser:
            raise InvalidToken('No active account found with the given credentials')
        if user.is_adminuser:
            raise InvalidToken('No active account found with the given credentials')

        return data
    
class CustomAdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user or self.context['request'].user

        if not user.user_email_verified and not user.is_adminuser:
                raise InvalidToken('No active account found with the given credentials')
        if user.user_email_verified and not user.is_adminuser:
                raise InvalidToken('No active account found with the given credentials') 
        if not user.user_email_verified and user.is_adminuser:
            raise InvalidToken('No active account found with the given credentials')

        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["id", 'username', 'email', 'password']
        extra_kwargs = {
            "username":{"write_only": True},
            "email":{"write_only":True},
            "password":{"write_only": True},
        }

    # def create(self, validated_data):
    #     user = UserProfile.objects.create_user(**validated_data)
    #     return user
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        key = settings.ENCRYPTION_KEY
        cipher_suite = Fernet(key)
        encrypted_id = cipher_suite.encrypt(str(ret['id']).encode()).decode()
        ret['id'] = encrypted_id

        return ret
    

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["username", 'email']

class UsersDetailSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = ['id','username', 'email', 'companyname', 'user_email_verified', 'status']

    def get_status(self, obj):
        return 'active' if obj.is_active else 'banned'
    

class BusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['companyname', 'companyemail', 'phonenumber', 'companyaddress']

class EmailOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['otp']
    
class ActivateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user_email_verified']

class UpdateUserProfilePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

from django.shortcuts import render
from .models import UserProfile
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import (UserSerializer, UserDetailsSerializer, BusinessProfileSerializer, CustomTokenObtainPairSerializer,
                           EmailOTPSerializer, UsersDetailSerializer, CustomAdminTokenObtainPairSerializer)
from .serializers import ActivateUserProfileSerializer, UpdateUserProfilePasswordSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from .utils import send_email_otp, otp_generator
from django.contrib.auth.hashers import make_password 


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomAdminTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomAdminTokenObtainPairSerializer

class CreateUserView(generics.CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email', None)

        try:
            existing_user = UserProfile.objects.get(email=email)
            if not existing_user.user_email_verified:
                existing_user.delete()
                request.data['password'] = make_password(request.data['password'])
                return super().create(request, *args, **kwargs)
            else:
                return Response({"message" : "User with email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            request.data['password'] = make_password(request.data['password'])
            return super().create(request, *args, **kwargs)
            


class UserDetilsView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserDetailsSerializer
    lookup_field = 'pk'
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class UsersDetailView(generics.ListAPIView):
    serializer_class = UsersDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        queryset = UserProfile.objects.filter(is_staff=False)
        return queryset

class BusinessDetailsView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    lookup_field = 'pk'
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(user = user)


class UserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserDetailsSerializer
    lookup_field = 'pk'
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class SentEmailOTPView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, email, format=None):
       return Response({'message': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST) 

    def post(self, request, email, format=None):
        try:
            user = UserProfile.objects.get(email = email)
        except UserProfile.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        otp = otp_generator()
        user.otp = otp
        user.save()
        send_email_otp(email=email, otp=otp)

        return Response({'data' : otp}, status=status.HTTP_200_OK)


class GetUserOtpView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = EmailOTPSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self , request, *args, **kwargs):

        email = kwargs.get('email')
        if email:
            try:
                user = self.get_queryset().get(email = email)
                serializer = self.get_serializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except UserProfile.DoesNotExist:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    def post(self, request, *args, **kwargs):
        return Response({'message': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

class ActivateUserProfileView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = ActivateUserProfileSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = kwargs.get('email')
        if email:
            try:
                user = self.get_queryset().get(email=email)
                if user.otp == request.data['otp']:
                    user.user_email_verified = True
                    user.otp = ''
                    user.save()
                    serializer = self.get_serializer(user)
                    return Response({'data': serializer.data}, status=status.HTTP_200_OK)
                return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except UserProfile.DoesNotExist:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message':'email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
class ActivateAdminProfileView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = ActivateUserProfileSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = kwargs.get('email')
        if email:
            try:
                user = self.get_queryset().get(email=email)
                if user.otp == request.data['otp']:
                    user.user_email_verified = True
                    user.is_adminuser = True
                    user.otp = ''
                    user.save()
                    serializer = self.get_serializer(user)
                    return Response({'data': serializer.data}, status=status.HTTP_200_OK)
                return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except UserProfile.DoesNotExist:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message':'email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
class UserProfileDeleteView(generics.DestroyAPIView):
    queryset = UserProfile.objects.all()
    authentication_classes = []
    lookup_field = 'email'
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response('Successfully deleted', status=status.HTTP_200_OK)
    
class ForgotPasswordUserSearchView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        email = kwargs.get('email')
        if not email:
            return Response('Email Required', status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = UserProfile.objects.get(email = email)
            if user:
                return Response( status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response('User with email does not exists', status=status.HTTP_404_NOT_FOUND)
        return Response('Invalid request', status=status.HTTP_400_BAD_REQUEST)
    
class UpdateUserProfilePasswordView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UpdateUserProfilePasswordSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    lookup_field = 'email'

    def put(self, request, *args, **kwargs):
        email = kwargs.get('email')
        if not email:
            return Response('Email Required', status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = self.get_object()
            request.data['password'] = make_password(request.data['password'])
            user.password = request.data['password']
            user.otp = ''
            user.save()
            # print('user', user)
            return Response('Password Changed', status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response('User with email does not exists', status=status.HTTP_404_NOT_FOUND)

        

        

    

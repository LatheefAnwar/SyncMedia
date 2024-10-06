from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from allauth.socialaccount.models import SocialApp
from .models import SocialHandle, FacebookPage, InstagramAccount, SocialMediaRevokePremission
from authentication.models import UserProfile
from allauth.socialaccount.providers.facebook.constants import ( GRAPH_API_VERSION, GRAPH_API_URL)
from django.shortcuts import redirect
from .serializers import SocialHandlesSerializer, SocialMediaSerializer, UnlinkAccountSerializer
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .utils import generate_facebook_expiry_date
from urllib.parse import urlencode
import requests
import json

    
class FacebookOAuthCallbackView(APIView):
    permission_classes = [AllowAny]
    access_url = GRAPH_API_URL+GRAPH_API_VERSION + '/oauth/access_token'
    user_data_url = GRAPH_API_URL + 'me'
    def get(self, request):
        user_id = request.GET.get('state')
        if not user_id:
            return Response({'error': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
        callback_url = settings.SOCIAL_AUTH_CALLBACK_URI
        code = request.GET.get('code')

        if not code:
            return redirect(callback_url if callback_url else '/')
        
        try:
            app = SocialApp.objects.get(provider='facebook')
            token_data = self.get_access_token(app, code, user_id)
        except SocialApp.DoesNotExist:
            return Response({'error': 'Facebook not configured'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_data = self.get_user_data(token_data['access_token'])
            user_save = self.save_user_data(user_data, token_data, user_id)
            if not user_save:
                return Response({'error': 'Error saving user data'}, status=status.HTTP_400_BAD_REQUEST)
            return redirect(callback_url if callback_url else '/')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_access_token(self, app, code, user_id):
        params = {
            'client_id': app.client_id,
            'redirect_uri': self.get_callback_url(user_id),
            'client_secret': app.secret,
            'code': code,
        }
        response = requests.get(self.access_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_user_data(self, access_token):
        params = {
            'fields': 'id,name,email',
            'access_token': access_token,
        }
        response = requests.get(self.user_data_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def save_user_data(self, user_data, token_data, user_id):
        try:
            user = UserProfile.objects.get(id=user_id)
            try:
                facebook_handle = SocialHandle.objects.get(user=user, provider='facebook')
                if token_data.get('expires_in'):
                    facebook_handle.access_token = token_data['access_token']
                    facebook_handle.refresh_token = token_data.get('refresh_token', '')
                    facebook_handle.token_expiry = timezone.now() + timedelta(seconds= token_data['expires_in'])
                    facebook_handle.save()
                    pages_data = self.get_facebook_pages(token_data['access_token'])
                    self.save_facebook_pages(pages_data, user, token_data['access_token'])
                    return facebook_handle
                
                facebook_handle.access_token = token_data['access_token']
                facebook_handle.refresh_token = token_data.get('refresh_token', '')
                facebook_handle.token_expiry = generate_facebook_expiry_date()
                facebook_handle.save()
                pages_data = self.get_facebook_pages(token_data['access_token'])
                self.save_facebook_pages(pages_data, user, token_data['access_token'])
                return facebook_handle
                
            except SocialHandle.DoesNotExist:
                if token_data.get('expires_in'):
                    facebook_data = SocialHandle.objects.create(
                        user = user,
                        provider = 'facebook',
                        uid = user_data['id'],
                        extra_data = user_data,
                        access_token = token_data['access_token'],
                        refresh_token = token_data.get('refresh_token', ''),
                        token_expiry = timezone.now() + timedelta(seconds= token_data['expires_in'])               
                    )
                    facebook_data.save()
                    pages_data = self.get_facebook_pages(token_data['access_token'])
                    self.save_facebook_pages(pages_data, user, token_data['access_token'])
                    return facebook_data
                
                facebook_data = SocialHandle.objects.create(
                        user = user,
                        provider = 'facebook',
                        uid = user_data['id'],
                        extra_data = user_data,
                        access_token = token_data['access_token'],
                        refresh_token = token_data.get('refresh_token', ''),
                        token_expiry = generate_facebook_expiry_date()              
                    )
                facebook_data.save()
                pages_data = self.get_facebook_pages(token_data['access_token'])
                self.save_facebook_pages(pages_data, user, token_data['access_token'])
                return facebook_data   
        except UserProfile.DoesNotExist:
            return False 

    def get_facebook_pages(self, access_token):
        url = GRAPH_API_URL + GRAPH_API_VERSION + '/me/accounts'
        params = {
            'access_token': access_token,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('data', [])
    
    def save_facebook_pages(self, pages_data, user, access_token):
        FacebookPage.objects.filter(user=user).delete()
        for page in pages_data:
            fb_page, created = FacebookPage.objects.update_or_create(
                user = user,
                page_id = page['id'],
                defaults={
                    'page_name': page.get('name'),
                    'page_access_token': page.get('access_token'),
                    'page_category': page.get('category'),
                    'extra_data': json.dumps(page)
                }
            )
            insta_account = self.get_instagram_profile(page['id'], access_token)
            if insta_account:
                self.save_instagram_profile(fb_page, insta_account)
            
    def get_instagram_profile(self, page_id, access_token):
        url = GRAPH_API_URL + GRAPH_API_VERSION + '/' + page_id
        params = {
        'fields': 'instagram_business_account',
        'access_token': access_token,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        insta_id = response.json().get('instagram_business_account', [])
        if insta_id:
            data = self.get_instagram_account(insta_id, access_token)
            return data
    
    def get_instagram_account(self, insta_id, access_token):
        url = GRAPH_API_URL + GRAPH_API_VERSION + '/' + insta_id.get('id')
        params = {
        'fields': 'id,username',
        'access_token': access_token,
        }
        response = requests.get(url, params=params)
        return response.json()

    def save_instagram_profile(self, fb_page, insta_account):
        InstagramAccount.objects.update_or_create(
            facebook_page = fb_page,
            instagram_id = insta_account['id'],
            defaults={
                'username': insta_account.get('username'),
                'extra_data': json.dumps(insta_account)
            }
        )

    def get_callback_url(self, user_id):
        callback_url = reverse('facebook_callback')
        return f'{self.request.build_absolute_uri(callback_url)}?state={user_id}'
      
class FacebookOAuthRedirectView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
       try:   
        app = SocialApp.objects.get(provider='facebook')
        params = {
            'client_id': app.client_id,
            'redirect_uri': self.get_callback_url(user_id),
            'scope': settings.SOCIALACCOUNT_PROVIDERS['facebook']['SCOPE'],
            'response_type': 'code',
            'state': user_id
        }
        authorization_url = f'https://www.facebook.com/{GRAPH_API_VERSION}/dialog/oauth?' + urlencode(params)
        return redirect(authorization_url)
       except SocialApp.DoesNotExist:
           return Response({'error': 'Facebook not configured'}, status=status.HTTP_400_BAD_REQUEST)
       except Exception as e:
           return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
    def get_callback_url(self, user_id):
        callback_url = reverse('facebook_callback')
        return f'{self.request.build_absolute_uri(callback_url)}?state={user_id}'
    
class RevokeFacebookUserAccessView(APIView):
    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('id') 
        if not user_id:
            return Response({'User ID not provided'})
        try:
            facebook_data = SocialHandle.objects.get(user__id=user_id, provider='facebook')
            revoke = self.revoke_user_permissions(facebook_data.access_token, facebook_data.uid)
            if not revoke:
                return Response({'Error revoking, access token not valid'}, status=status.HTTP_400_BAD_REQUEST)
            facebook_data.delete()
            return Response({'User data revoked'}, status=status.HTTP_200_OK)
        except SocialHandle.DoesNotExist:
            return Response({'User not yet connected facebook'}, status=status.HTTP_404_NOT_FOUND)

    def revoke_user_permissions(self, user_access_token, uid):
        revoke_url = f'{GRAPH_API_URL}{GRAPH_API_VERSION}/{uid}/permissions'
        params = {
            'access_token': user_access_token
        }
        response = requests.delete(revoke_url, params=params)
        return True if response.status_code == 200 else False


class GoogleOAuthCallbackView(APIView):
    permission_classes = [AllowAny]
    token_url = f'https://oauth2.googleapis.com/token'
    profile_url = 'https://www.googleapis.com/oauth2/v2/userinfo'

    def get(self, request):
        user_id = request.GET.get('state')
        if not user_id:
            return Response({'error: User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
        callback_url = settings.SOCIAL_AUTH_CALLBACK_URI
        code = request.GET.get('code')
        if not code:
            return redirect(callback_url if callback_url else '/')
            # return Response({'error': 'Authorization code not provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            app = SocialApp.objects.get(provider='google')
            token_data = self.get_access_token(app, code)
        except SocialApp.DoesNotExist:
            return Response({'error': 'Google not configured'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not token_data:
            return Response({'error': 'faild to get token data'}, status=status.HTTP_400_BAD_REQUEST)
        user_data = self.get_user_data(token_data['access_token'])
        if not user_data:
            return Response({'error': 'error fetching user info'}, status=status.HTTP_400_BAD_REQUEST)
        user_saved = self.save_user_data(user_id, user_data, token_data)
        if not user_saved:
            return Response({'error': 'Error saving the user data'}, status=status.HTTP_400_BAD_REQUEST)
        return redirect(callback_url)

    def get_access_token(self, app, code):
        data = {
            'code': code,
            'client_id': app.client_id,
            'client_secret': app.secret,
            'redirect_uri': self.get_callback_url(),
            'grant_type': 'authorization_code',
        }
        response = requests.post(self.token_url,  data=data)
        response.raise_for_status()
        return response.json()
    
    def get_user_data(self, access_token):
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.get(self.profile_url, headers=headers)
        response.raise_for_status()
        return response.json()
 
    def save_user_data(self, user_id, user_data,token_data):
        try:
            user = UserProfile.objects.get(id=user_id)
            try:
                google_handle = SocialHandle.objects.get(user=user, provider='youtube')
                google_handle.access_token = token_data['access_token']
                google_handle.refresh_token = token_data.get('refresh_token', '')
                google_handle.token_expiry = timezone.now() + timedelta(seconds= token_data['expires_in'])
                google_handle.save()
                return google_handle
            except SocialHandle.DoesNotExist:
                google_data = SocialHandle.objects.create(
                    user = user,
                    provider = 'youtube',
                    uid = user_data['id'],
                    extra_data = user_data,
                    access_token = token_data['access_token'],
                    refresh_token = token_data.get('refresh_token', ''),
                    token_expiry = timezone.now() + timedelta(seconds= token_data['expires_in'])               
                )
                google_data.save()
                return google_data
        except UserProfile.DoesNotExist:
            return False
        
    def get_callback_url(self):
        return self.request.build_absolute_uri(reverse('google_callback'))
    
    
class GoogleOAuthRedirectView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            app = SocialApp.objects.get(provider='google')
            scopes = ' '.join(settings.SOCIALACCOUNT_PROVIDERS['google']['SCOPE'])
            params = {
                'scope': scopes,
                'access_type':'offline',
                'response_type': 'code',
                'state': user_id,
                'redirect_uri': self.get_callback_url(),
                'client_id': app.client_id,
            }
            authorization_url = f'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)
            return redirect(authorization_url)
        except SocialApp.DoesNotExist:
            return Response({'error': 'Google not configured'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get_callback_url(self):
        return self.request.build_absolute_uri(reverse('google_callback'))

class RevokeGoogleUserAccessView(APIView):
    revoke_url = f'https://oauth2.googleapis.com/revoke'

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('id') 
        if not user_id:
            return Response({'User ID not provided'})
        try:
            google_data = SocialHandle.objects.get(user__id=user_id, provider='youtube')
            revoke = self.revoke_user_permissions(google_data.access_token)
            if not revoke:
                return Response({'Error revoking, access token not valid'}, status=status.HTTP_400_BAD_REQUEST)
            google_data.delete()
            return Response({'User data revoked'}, status=status.HTTP_200_OK)
        except SocialHandle.DoesNotExist:
            return Response({'User not yet connected Google'}, status=status.HTTP_404_NOT_FOUND)

    def revoke_user_permissions(self, user_access_token):
        params = {
            'token': user_access_token
        }
        response = requests.post(self.revoke_url, params=params)
        return True if response.status_code == 200 else False

          
class GetUserSocialHandlesView(generics.ListAPIView):
    serializer_class = SocialHandlesSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return SocialHandle.objects.filter(user__id=user_id)
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({'details': 'user didn\'t add any socialmedia yet'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UnlinkAccountsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        
        user_id = kwargs.get('id')
        queryset = self.get_queryset(self.get_social_media_names(user_id))
        serializer = UnlinkAccountSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def get_queryset(self, social_media):
        queryset = SocialMediaRevokePremission.objects.filter(provider__in=social_media)
        return queryset
    
    def get_social_media_names(self, user_id):
        user_social_media = SocialHandle.objects.filter(user__id=user_id)
        serializer = SocialMediaSerializer(user_social_media, many=True)
        social_media = [handle['provider'] for handle in serializer.data]
        return social_media

        


    



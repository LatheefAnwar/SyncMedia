from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import ProductDetailsSerializer, ProductsViewSerializer
from socialconnect.serializers import FacebookPageSerializer, InstaAccountsSerializers
from .models import ProductsDetail
from socialconnect.models import FacebookPage, InstagramAccount, SocialHandle
from authentication.models import UserProfile
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from allauth.socialaccount.providers.facebook.constants import  GRAPH_API_VERSION, GRAPH_API_URL
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .tasks import send_email_campaign_mass_mail
import openpyxl
import re
import requests
import tempfile
import os

# Create your views here.


class ProductDetailsCreateView(generics.CreateAPIView):
    queryset = ProductsDetail.objects.all()
    serializer_class = ProductDetailsSerializer
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        request.data['user'] = user_id
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ProdectDetailsView(generics.ListAPIView):
    serializer_class = ProductsViewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['pk']
        return ProductsDetail.objects.filter(user = UserProfile.objects.get(pk=user_id))

class GetFacebookPageView(generics.RetrieveAPIView):
    serializer_class = FacebookPageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
         user_id = self.kwargs.get('pk')
         return FacebookPage.objects.filter(user__id= user_id)

    def get(self, request, *args, **kwargs):
    
        queryset = self.get_queryset() 
        if not queryset.exists():
            return Response({'error': 'No page available for the current user'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetInstagramAccountView(generics.RetrieveAPIView):
    serializer_class = InstaAccountsSerializers
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        facebook_pages = request.data
        if not facebook_pages:
            return Response({'error', 'No facebook page provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instaobjects = self.get_instagram(facebook_pages)
        except InstagramAccount.DoesNotExist:
            return Response({'error': 'One or more Instagram accounts do not exist'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(instaobjects, status=status.HTTP_200_OK)

    def get_instagram(self, facebook_pages):
        queryset = []
        for page in facebook_pages:

            try:
                queryset_object = InstagramAccount.objects.get(facebook_page__page_name=page.get('page_name'))
                serializer = self.get_serializer(queryset_object)
                queryset.append(serializer.data)
            except InstagramAccount.DoesNotExist:
                continue
        return queryset
               
class PostSocialMediaContentview(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def post(self, request, *args, **kwargs):
        print('\n\n\n',request.data,'\n\n\n')
        user_id = kwargs.get('pk')
        if not user_id:
            return Response({'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        fbpage = request.data.get('fbpage')
        if not fbpage:
            return Response({'Invalid Facebook Page request'}, status=status.HTTP_400_BAD_REQUEST )
        pages = fbpage.split(',')
        pageaccess = self.get_page_objects(user_id, pages)
        if not pageaccess:
            return Response({'No facebook page found for current user'}, status=status.HTTP_400_BAD_REQUEST)
        message = request.data.get('description')
        if not message:
            return Response({'error': 'No message body'}, status=status.HTTP_400_BAD_REQUEST)
        responses = self.post_FB_blog_content(pageaccess, message)
        return self.handle_responses(responses)
              
    def get_page_objects(self, user, pages):
        access = FacebookPage.objects.filter(user__id=user, page_name__in=pages)
        return access
    
    def handle_responses(self, responses):
        success_responses = [response['response'] for response in responses if response.get('response')]
        error_responses = [response['error'] for response in responses if response.get('error')]
        if success_responses:
            return Response(success_responses, status=status.HTTP_200_OK)
        if error_responses:
            return Response(error_responses, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error':'Bad Request'},status=status.HTTP_400_BAD_REQUEST)

    def post_FB_blog_content(self, page_data, content ):
        responses = []
        for data in page_data:
            page_posting_url = f'{GRAPH_API_URL}{GRAPH_API_VERSION}/{data.page_id}/feed/'
            content_data = {
                'message': content,
                'access_token': data.page_access_token
            }
            response = requests.post(page_posting_url, content_data)
            post_result = {
                'page_id': data.page_id,
                'page_name': data.page_name,
                'response': response.json() if response.status_code == 200 else None,
                'error': response.json() if response.status_code != 200 else None,
            }
            responses.append(post_result)
        return responses
       
class PostMediaContentView(PostSocialMediaContentview):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes=(MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        if not user_id:
            return Response({'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        fbpage =  request.data.get('fbpage')
        if not fbpage:
            return Response({'Invalid Facebook Page request'}, status=status.HTTP_400_BAD_REQUEST)
        pages = fbpage.split(',')
        
        pageaccess = self.get_page_objects(user_id, pages)
        if not pageaccess:
            return Response({'No facebook page found for current user'}, status=status.HTTP_400_BAD_REQUEST)
        message = request.data.get('description')
        image = request.data.get('image')
        with tempfile.NamedTemporaryFile(dir= settings.FB_TEMP_PATH, delete=False) as temp_file:
                for chunk in image.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
        responses = self.post_FB_image_content(pageaccess, message, temp_file_path)
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return self.handle_responses(responses)
    
    def post_FB_image_content(self, page_data, message, image_path):
        responses = []
        for data in page_data:
            page_posting_url = f'{GRAPH_API_URL}{GRAPH_API_VERSION}/{data.page_id}/photos/'
            with open (image_path, 'rb') as image_file:
                files = {'source': image_file}
                content_data = {
                    'message': message,
                    'access_token': data.page_access_token
                }
                response = requests.post(page_posting_url, data=content_data, files=files)
                post_result = {
                'page_id': data.page_id,
                'page_name': data.page_name,
                'response': response.json() if response.status_code == 200 else None,
                'error': response.json() if response.status_code != 200 else None,
                    }
                responses.append(post_result)
        return responses
    
class PostInstagramMediaContentView(PostSocialMediaContentview):
    permission_classes  = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes=(MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        if not user_id:
            return Response({'error': 'user ID did\'t provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        instagram_profiles = request.data.get('instagram')
        if not instagram_profiles:
            return Response({'error': 'No instagram account provided'}, status=status.HTTP_400_BAD_REQUEST)
        instagram = instagram_profiles.split(',')
        
        query_set = self.get_instagram_queryset(instagram)

        if not query_set:
            return Response({'error': 'No instagram account found for the current user'})
        try:
            provider = SocialHandle.objects.get(provider='facebook', user=user_id)
        except SocialHandle.DoesNotExist:
            return Response({'error': 'Facebook not configured'}, status=status.HTTP_400_BAD_REQUEST)
        access_token = provider.access_token

        message = request.data.get('description')
        if not message:
            return Response({'error': 'No description provided'}, status=status.HTTP_400_BAD_REQUEST)
        image = request.data.get('image')
        if not image:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        response = self.complete_instagram_post(query_set, access_token, message)
        return self.handle_responses(response)
    
    def get_instagram_queryset(self, insta_username):
        query = InstagramAccount.objects.filter(username__in = insta_username)
        return query
    
    def complete_instagram_post(self, insta_accounts, access_token, caption):
        responses = []
        for account in insta_accounts:
            insta_posting_url = f'{GRAPH_API_URL}{GRAPH_API_VERSION}/{account.instagram_id}/media'
        
            params = {
                'image_url' : settings.INSTAGRAM_IMAGE_URL,
                'caption' : caption,
                'access_token': access_token
            }

            response = requests.post(insta_posting_url, params=params)
            container_id = response.json().get('id') if response.status_code == 200 else None
            if container_id:
                publish_response = self.publish_container(account.instagram_id, account.username, container_id, access_token)
                responses.append(publish_response)
            else:
                post_result = {
                    'insta_id': account.instagram_id,
                    'username': account.username,
                    'response': None,
                    'error': response.json() if response.status_code != 200 else None,
                        }
                responses.append(post_result)
        return responses     
    
    def publish_container(self, insta_id, insta_user, container_id, access_token):
        publish_url = f'{GRAPH_API_URL}{GRAPH_API_VERSION}/{insta_id}/media_publish'
        params = {
            'creation_id': container_id,
            'access_token': access_token,
        }

        response = requests.post(publish_url, params=params)
        post_result = {
            'insta_id': insta_id,
            'username': insta_user,
            'response': response.json() if response.status_code == 200 else None,
            'error': response.json() if response.status_code != 200 else None,
                }
        return post_result
    


class PostEmailCampaignView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        emails = []
        user_id = kwargs.get('pk')
        files = request.FILES.getlist('to[]')

        for file in files:
            if file.name.endswith('.xlsx'):
                saved_path = default_storage.save(file.name, ContentFile(file.read()))
                file_path = default_storage.path(saved_path)
                try:
                    emails.extend(self.extract_emails_from_xlsx(file_path))

                finally:
                    default_storage.delete(file_path)
        
        campaign_name = request.data.get('campaignName')
        subject = request.data.get('subject')
        email_content = request.data.get('description')
        link = request.data.get('link', None) 
        image = request.data.get('image', None)

        context = {
            'message': email_content,
            'link': link,
            'image': image
        }
        print('\n\n',emails)
        send_email_campaign_mass_mail.delay(subject, context, emails)
        return Response({'user_id': user_id}, status=status.HTTP_200_OK)
    
    def extract_emails_from_xlsx(self, xlsx_path):
        emails = []
        try:
            workbook = openpyxl.load_workbook(xlsx_path)
            for sheet in workbook.worksheets:
                for row in sheet.iter_rows(values_only=True):
                    for cell in row:
                        if isinstance(cell, str) and re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', cell):
                            emails.append(cell)
        except Exception as e:
            print(f"Error occurred while parsing Excel file {xlsx_path}: {e}")
        return emails
   

    
     

        
from rest_framework import serializers
from .models import SocialHandle, FacebookPage, InstagramAccount, SocialMediaRevokePremission

class SocialHandlesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialHandle
        fields = ['provider', 'token_expired']

        def get_token_expired(self, instance):
                return instance.token_expired()
        
class FacebookPageSerializer(serializers.ModelSerializer):
     class Meta:
          model = FacebookPage
          fields = ['page_name']

class SocialMediaSerializer(serializers.ModelSerializer):
     class Meta:
          model = SocialHandle
          fields = ['provider']

class InstaAccountsSerializers(serializers.ModelSerializer):
     class Meta:
          model = InstagramAccount
          fields = ['username']

class UnlinkAccountSerializer(serializers.ModelSerializer):
     class Meta:
          model = SocialMediaRevokePremission
          fields = ['provider', 'revoke_url']

# class FacebookPageAccessSerializer(serializers.ModelSerializer):
#     class Meta:
#          model = FacebookPage
#          fields = ['page_id','page_access_token']
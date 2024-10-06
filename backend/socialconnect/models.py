from django.db import models
from django.utils import timezone
from authentication.models import UserProfile
# Create your models here.

class SocialHandle(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20)
    uid = models.CharField(max_length=50)
    extra_data = models.JSONField()
    access_token = models.CharField(max_length=300, blank=True, null=True)
    refresh_token = models.CharField(max_length=300, blank=True, null=True)
    token_expiry = models.DateTimeField(blank=True, null=True)

    def token_expired(self):
        return timezone.now() >= self.token_expiry

    def __str__(self):
        return self.provider
    
class FacebookPage(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    page_id = models.CharField(max_length=100)
    page_name = models.CharField(max_length=255)
    page_access_token = models.CharField(max_length=500)
    page_category = models.CharField(max_length=255)
    extra_data = models.JSONField()

    def __str__(self):
        return f'{self.page_name} + {self.user}'
    
class InstagramAccount(models.Model):
    facebook_page = models.ForeignKey(FacebookPage, on_delete=models.CASCADE)
    instagram_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    extra_data = models.JSONField()


    def __str__(self):
        return f'{self.username}'
    
class SocialMediaRevokePremission(models.Model):
    provider = models.CharField(max_length=100)
    revoke_url = models.URLField()

    def __str__(self) :
        return f'{self.provider}'
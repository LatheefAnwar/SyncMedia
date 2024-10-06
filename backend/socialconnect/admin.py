from django.contrib import admin
from .models import SocialHandle, FacebookPage, InstagramAccount, SocialMediaRevokePremission

# Register your models here.

admin.site.register(SocialHandle)
admin.site.register(FacebookPage)
admin.site.register(InstagramAccount)
admin.site.register(SocialMediaRevokePremission)
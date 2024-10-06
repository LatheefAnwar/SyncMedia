from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile

# Register your models here.

class UserProfileAdmin(BaseUserAdmin):
    fieldsets = (
        (None,{
            'fields':('email', 'password', 'username', 'last_login',
                       'companyname', 'companyemail', 'phonenumber', 'companyaddress',
                       'otp')
        }),
        ('permissions',{'fields':(
            'is_active',
            'is_staff',
            'is_superuser',
            'is_adminuser',
            'user_email_verified',
            'business_email_verified',
            'groups',
            'user_permissions',
            
        )}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1','password2')
            }
        ),
    )
    list_display = ( 'email', 'username', 'companyname', 'companyemail')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(UserProfile, UserProfileAdmin)


from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.

class UserProfileManager(BaseUserManager):
        
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError("User must have an email address")
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email = email,
            is_staff = is_staff,
            is_active = True,
            is_superuser = is_superuser,
            last_login = now,
            date_joined = now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)
        user.save(using = self._db)
        return user
    # def create_user(self, email, password=None, **extra_fields):
    #     if not email:
    #         raise ValueError("The Email field must be set")
    #     email = self.normalize_email(email)
    #     user = self.model(email= email, **extra_fields)
    #     user.set_password(password)
    #     user.save(using=self._db)
    #     return user

    # def create_superuser(self, email, password=None, **extra_fields):
    #     extra_fields.setdefault('is_staff', True)
    #     extra_fields.setdefault('is_superuser', True)

    #     if extra_fields.get('is_staff') is not True:
    #         raise ValueError('Superuser must have is_staff=True.')
    #     if extra_fields.get('is_superuser') is not True:
    #         raise ValueError('Superuser must have is_superuser=True.')
    #     return self.create_user(email, password, **extra_fields)



class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("Email address"),unique=True, help_text=_(
            "Required for authentication. Email is unique"
        ),error_messages={
            "unique": _("A user with that email already exists."),
        },)
    username = models.CharField(_("Username/Fullname"), max_length=150,help_text=_(
            "150 characters or fewer."), blank=True)
    is_active = models.BooleanField(_("active"),default=True,help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ))
    is_staff = models.BooleanField(_("staff status"), default=False,
        help_text=_("Designates whether the user can log into this admin site."))
    is_superuser = models.BooleanField(_("Superuser status"),default=False)
    is_adminuser = models.BooleanField(_("Adminuser status"),default=False,
        help_text=_("Designates whether the user can log into admin site."))
    date_joined = models.DateTimeField(_("date joined"),auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    companyname = models.CharField(_("Company name"), max_length= 100, null=True, blank=True,
        help_text=_("Required. Add company name when creating business profile"))
    companyemail = models.EmailField(_("Company Email address"), null= True, blank= True,
        help_text=_("Required. Add company email address when creating business profile."
                    "This email address is not unique."))
    phonenumber = models.CharField(_("Company Phone number"),max_length=15, null=True, blank=True,
        help_text=_("Required. Add company phone number when creating business profile."))
    companyaddress = models.TextField(_("Company address"), null=True, blank=True,
        help_text=_("Required. Add company address when creating business profile."))
    otp = models.CharField(_("OTP"), max_length=7, null=True, blank=True,
        help_text=_("This field stores the OTP and will reset once authenticated."))
    user_email_verified = models.BooleanField(_("User Verified"),default= False,
        help_text=_("False by default, True when user's email is verified"))
    business_email_verified = models.BooleanField(_("Business Verified"),default= False,
        help_text=_("False by default, True when business email is verified"))

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []


    # def __str__(self) :
    #     return self.email
    
    def get_absolute_url(self):
        return "/users/%i" % self.pk

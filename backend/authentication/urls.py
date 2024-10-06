from django.urls import path
from .views import  (CreateUserView, UserDetilsView, UserUpdateView, BusinessDetailsView,
                      CustomTokenObtainPairView, UpdateUserProfilePasswordView,SentEmailOTPView,
                        GetUserOtpView, ActivateUserProfileView, UserProfileDeleteView, ForgotPasswordUserSearchView,
                          UsersDetailView, CustomAdminTokenObtainPairView, ActivateAdminProfileView) 


urlpatterns = [
    path("user/register/", CreateUserView.as_view(), name="user.register"),
    path('user/token/', CustomTokenObtainPairView.as_view(), name='token.obtain.pair'),
    path("user/details/<int:pk>/", UserDetilsView.as_view(), name="user.details"),
    path('user/details/allusers/', UsersDetailView.as_view(), name='users.all.details'),
    path('user/details/update/<int:pk>/', UserUpdateView.as_view(), name='user.update'),
    path('business/register/<int:pk>/', BusinessDetailsView.as_view(), name='Business.profile'),
    path('user/email-otp/<str:email>/', SentEmailOTPView.as_view(), name='email.otp'),
    path('user/email-otp/details/<str:email>/', GetUserOtpView.as_view(), name='email.otp.details'),
    path('user/register/activate/<str:email>/', ActivateUserProfileView.as_view(), name='user.activate'),
    path('user/register/delete/<str:email>/', UserProfileDeleteView.as_view(), name='user.delete'),
    path('user/forgotpassword/<str:email>/', ForgotPasswordUserSearchView.as_view(), name='user.forgotpassword'),
    path('user/forgotpassword/resetpassword/<str:email>/', UpdateUserProfilePasswordView.as_view(), name='user.resetpassword'),
    path('admin/token/', CustomAdminTokenObtainPairView.as_view(), name='admin.token.obtain.pair'),
    path('admin/register/activate/<str:email>/', ActivateAdminProfileView.as_view(), name='admin.activate'),

]
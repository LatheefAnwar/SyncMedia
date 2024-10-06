from django.urls import path
from .views import (FacebookOAuthRedirectView, FacebookOAuthCallbackView, GetUserSocialHandlesView,
                    GoogleOAuthRedirectView, GoogleOAuthCallbackView, RevokeGoogleUserAccessView,
                    RevokeFacebookUserAccessView, UnlinkAccountsView)


urlpatterns = [
    path('facebook/oauth/<int:user_id>/', FacebookOAuthRedirectView.as_view(), name='facebook_login'),
    path('facebook/callback/', FacebookOAuthCallbackView.as_view(), name ='facebook_callback'),
    path('facebook/revoke/<int:id>/', RevokeFacebookUserAccessView.as_view(), name='facebook_revoke'),
    path('google/oauth/<int:user_id>/', GoogleOAuthRedirectView.as_view(), name='google_login'),
    path('google/callback/', GoogleOAuthCallbackView.as_view(), name='google_callback'),
    path('google/revoke/<int:id>/', RevokeGoogleUserAccessView.as_view(), name='google_revoke'),
    path('user/allsocialhandles/<int:user_id>/', GetUserSocialHandlesView.as_view(), name='user_socialhandles'),
    path('user/unlink/<int:id>/', UnlinkAccountsView.as_view(), name='unlink_social_accounts'),
]
from django.urls import path
from .views import  (ProductDetailsCreateView, ProdectDetailsView, GetFacebookPageView, PostSocialMediaContentview, PostMediaContentView,
                     PostInstagramMediaContentView, GetInstagramAccountView, PostEmailCampaignView)
urlpatterns = [

    path("product/register/", ProductDetailsCreateView.as_view(), name="product.register"),
    path("product/details/<int:pk>/", ProdectDetailsView.as_view(), name="products.details"),
    path('facebook/pages/<int:pk>/', GetFacebookPageView.as_view(), name='facebook.pages'),
    path('socialmedia/feed/<int:pk>/', PostSocialMediaContentview.as_view(), name='socialmedia.content.post'),
    path('socialmedia/media/<int:pk>/', PostMediaContentView.as_view(), name='facebook.media'),
    path('instagram/media/<int:pk>/', PostInstagramMediaContentView.as_view(), name='instagram.media'),
    path('instagram/accounts/', GetInstagramAccountView.as_view(), name='instagram.accounts'),
    path('emailcampaign/<int:pk>/', PostEmailCampaignView.as_view(), name='email.campain'),
    # path('test', test_celery, name='noname'),
    # path('task-result/<str:task_id>/', get_task_result, name='get_task_result'),


]
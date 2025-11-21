from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views as api_views


urlpatterns = [
    path('register/', api_views.UserCreateAPIView.as_view()),
    path('login/', obtain_auth_token, name='api_token_auth'),
    path('profile/update/', api_views.ProfileUpdateAPIView.as_view(), name='update_profile'),
    path('profile/to_searching_allies/', api_views.UserToSearchingInAlliesList.as_view()),
    path('verify/', api_views.UserVerifyAPIView.as_view()),
]

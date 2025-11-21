from django.contrib.auth.views import LogoutView
from django.urls import path
from .api.urls import urlpatterns as accounts_api_urls
from accounts import views
from api import views as api_views
from django.contrib.auth import views as auth_views
from allauth.account import views as allauth_views

urlpatterns = [
    path('', views.UserListView.as_view(), name='user_list'),
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', allauth_views.logout, name='account_logout'),
    path('set-phone/', views.set_phone_view, name='set_phone'),
    path('<uuid:pk>/detail/', views.UserDetailView.as_view(), name='user_detail'),
    path('edit/', views.UserUpdateView.as_view(), name='user_update'),
    path('reset_password/', views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

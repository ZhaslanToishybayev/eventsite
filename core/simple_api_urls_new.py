from django.urls import path
from . import simple_api_views

urlpatterns = [
    path('simple-chat/', simple_api_views.simple_chat_api, name='simple_chat_api'),
    path('simple-status/', simple_api_views.simple_status_api, name='simple_status_api'),
]
from django.urls import path, include

urlpatterns = [
    path('', include('clubs.api.urls')),
    path('', include('accounts.api.urls')),
    path('ai/', include('ai_consultant.api.urls')),
    path('ai/', include('ai_consultant.api.urls_v2')),
]

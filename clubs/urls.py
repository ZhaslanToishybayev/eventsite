from django.urls import path
from clubs import views

club_urlpatterns = [
    path('clubs/', views.ClubListView.as_view(), name='clubs'),
    path('clubs/create/', views.ClubCreateView.as_view(), name='club_create'),
    path('clubs/<uuid:pk>/', views.ClubDetailView.as_view(), name='club_detail'),
    path('clubs/<uuid:pk>/update', views.ClubEditView.as_view(), name='club_edit'),
    path('clubs/<uuid:pk>/delete', views.ClubDeleteView.as_view(), name='club_delete'),
]

festival_urlpatterns = [
    path('festivals/', views.FestivalListView.as_view(), name='festivals'),
    path('festivals/<uuid:pk>/', views.FestivalDetailView.as_view(), name='festival_detail'),
    path('festivals/create/', views.FestivalCreateView.as_view(), name='festival_create'),
    path('festivals/<uuid:pk>/update/', views.FestivalUpdateView.as_view(), name='festival_update'),
    path('festivals/<uuid:pk>/delete/', views.FestivalDeleteView.as_view(), name='festival_delete'),
    path('festivals/<uuid:pk>/requests/', views.FestivalRequests.as_view(), name='festival_requests'),
    path('festivals/<uuid:pk>/approved/', views.FestivalApprovedClubs.as_view(), name='festival_approved_clubs'),
]

club_events_urlpatterns = [
    path('club/events/', views.ClubEventListView.as_view(), name='club_events'),
    path('club/<uuid:pk>/events/create/', views.CreateClubEventView.as_view(), name='event_create'),
    path('club/events/<uuid:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('club/events/<uuid:pk>/edit/', views.UpdateEventView.as_view(), name='edit_event'),
    path('event-calendar/', views.EventCalendarView.as_view(), name='event_calendar'),
]

club_service_urlpatterns = [
    path('clubs/<uuid:pk>/create_service', views.CreateServiceView.as_view(), name='create_service'),
    path('service/<uuid:pk>/', views.ClubServiceDetailView.as_view(), name='service_detail'),
    path('services/<uuid:pk>/edit/', views.UpdateServiceView.as_view(), name='edit_service'),
]

club_photogallery_urlpatterns = [
    path('clubs/<uuid:pk>/photogallery/', views.ClubPhotoGalleryView.as_view(), name='club_photogallery'),
    path('clubs/<uuid:pk>/photogallery/add/', views.ClubAddPhotoView.as_view(), name='club_photogallery_add'),
    path(
            'clubs/<uuid:pk>/photogallery/delete/',
            views.galleryForClubsDeleteView.as_view(),
            name='gallery_for_club_delete'
        ),
]

services_for_club_urlpatterns = [
    path('services/for-club/create/', views.ServiceForClubsCreateView.as_view(), name='service_for_club_create'),
    path('services/for-club/<uuid:pk>/', views.ServiceForClubDetailView.as_view(), name='service_for_club_detail'),
    path('services/for-club/<uuid:pk>/edit/', views.ServiceForClubsEditView.as_view(), name='service_for_club_edit'),
    path(
        'services/for-club/<uuid:pk>/delete/',
        views.ServiceForClubsDeleteView.as_view(),
        name='service_for_club_delete'
    ),
    path('services/for-club/all/', views.ServiceForClubsListView.as_view(), name='service_for_club_list'),
]


publication_urlpatterns = [
    path('publications/', views.PublicationListView.as_view(), name='publications'),
    path('publications/<uuid:pk>/', views.PublicationDetailView.as_view(), name='publication_detail'),
    path('publications/create/', views.PublicationCreateView.as_view(), name='publication_create'),
    path('publications/<uuid:pk>/update/', views.PublicationUpdateView.as_view(), name='publication_update'),
    path('publications/<uuid:pk>/delete/', views.PublicationDeleteView.as_view(), name='publication_delete'),
]


other_urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('clubs/<uuid:pk>/managers/edit/', views.ChooseClubManagersView.as_view(), name='club_managers_choose'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('policy/', views.PolicyView.as_view(), name='policy'),
    path('photogallery/<uuid:pk>/delete', views.galleryForClubsDeleteView.as_view(), name='photogallery_delete'),
]

urlpatterns = [
    *club_urlpatterns,
    *festival_urlpatterns,
    *club_events_urlpatterns,
    *club_service_urlpatterns,
    *club_photogallery_urlpatterns,
    *other_urlpatterns,
    *services_for_club_urlpatterns,
    *publication_urlpatterns,
]

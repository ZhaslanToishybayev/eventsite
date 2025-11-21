from clubs.api import views
from rest_framework import routers


router = routers.DefaultRouter()
router.register('clubs', views.ClubViewSet)
router.register('club/join_requests', views.ClubJoinRequestViewSet)
router.register('category', views.ClubCategoryViewSet)
router.register('cities', views.ClubCityViewSet)
router.register('services', views.ClubServiceViewSet)
router.register('service_images', views.ClubServiceImageViewSet)
router.register('events', views.ClubEventViewSet)
router.register('ads', views.ClubAdsViewSet)
router.register('gallery/photos', views.ClubGalleryPhotoViewSet)
router.register('festivals', views.FestivalViewSet)
router.register('festival/join_requests', views.FestivalParticipationRequestViewSet)
router.register('club/partnership_requests', views.ClubPartnerShipRequestViewSet)

urlpatterns = router.urls

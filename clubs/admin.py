from django.contrib import admin
from .models import *


class ClubPhotoInline(admin.TabularInline):
    model = ClubGalleryPhoto


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'city', 'address', 'is_active',)
    inlines = (ClubPhotoInline,)
    readonly_fields = ('members_count', 'likes_count', 'partners_count', 'likes', 'members')


@admin.register(ClubCategory)
class ClubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active',)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'iata_code',)


@admin.register(ClubEvent)
class ClubEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'start_datetime', 'location',)


@admin.register(ClubAds)
class ClubAdsAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'club',)


class ServiceImageInline(admin.TabularInline):
    model = ClubServiceImage
    can_delete = True
    verbose_name_plural = 'Фото услуги'
    extra = 5


@admin.register(ClubService)
class ClubServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'club',)
    inlines = (ServiceImageInline,)


@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):
    list_display = ('name', 'location',)


@admin.register(FestivalParticipationRequest)
class FestivalParticipationRequestAdmin(admin.ModelAdmin):
    list_display = ('club', 'festival', 'approved',)


@admin.register(ClubJoinRequest)
class ClubJoinRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'approved')


@admin.register(ClubGalleryPhoto)
class ClubGalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ('club', )

@admin.register(ServiceForClubs)
class ServiceForClubsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


admin.site.register(Publication)

@admin.register(ClubPost)
class ClubPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at', 'club')
    search_fields = ('title', 'content', 'club__name')

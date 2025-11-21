from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = _('Profile')


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('phone', 'first_name', 'last_name', 'email')
    list_display_links = ('phone',)
    fieldsets = (
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "avatar", "phone", "is_displayed_in_allies", "can_create_clubs")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (None, {"fields": ("password",)}),
    )
    ordering = ("date_joined",)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "password1", "password2"),
            },
        ),
    )
    search_fields = ("phone", "first_name", "last_name", "email")


admin.site.register(User, CustomUserAdmin)

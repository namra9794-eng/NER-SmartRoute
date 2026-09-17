from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Platform role", {"fields": ("role", "phone_number", "district", "preferred_language")}),
    )
    list_display = ("username", "email", "role", "district", "is_staff")


admin.site.register(User, CustomUserAdmin)

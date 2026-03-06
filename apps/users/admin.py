from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'name', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Info', {'fields': ('name',)}),
        ('Access', {'fields': ('is_active', 'is_staff')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'name', 'password1', 'password2')}),
    )
    list_filter = ['is_staff', 'is_active']
    search_fields = ['email', 'name']
    filter_horizontal = ()

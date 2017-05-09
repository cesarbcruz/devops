# coding=utf-8
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User
from .forms import UserAdminCreationForm, UserAdminForm


class UserAdmin(BaseUserAdmin):

    add_form = UserAdminCreationForm
    add_fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password1', 'password2')
        }),
    )
    form = UserAdminForm
    fieldsets = (
        (None, {
            'fields': ('username', 'email')
        }),
        ('Basic information', {
            'fields': ('name', 'last_login')
        }),
        ('Repository information', {
            'fields': ('repository_user', 'repository_password')
        }),
        ('VPN information', {
            'fields': ('vpn_user', 'vpn_password')
        }),
        (
            'Permissions', {
                'fields': (
                    'is_active', 'is_staff', 'is_superuser', 'groups',
                    'user_permissions'
                )
            }
        ),
    )
    list_display = ['username', 'name', 'email', 'is_active', 'is_staff', 'date_joined']


admin.site.register(User, UserAdmin)

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from continuousdelivery.forms import Global_ParametersAdminForm, ServerJbossAdminForm
from continuousdelivery.models import Global_Parameters, ServerJboss


class Global_ParametersAdmin(ModelAdmin):
    form = Global_ParametersAdminForm
    fieldsets = (
        (None, {
            'fields': ('smtp_server', 'smtp_port', 'email_sender', 'password_email_sender', 'folder_archive_binaries')
        }),
    )
    list_display = ['smtp_server', 'smtp_port', 'email_sender']

admin.site.register(Global_Parameters, Global_ParametersAdmin)


class JbossServerAdmin(ModelAdmin):
    form = ServerJbossAdminForm
    fieldsets = (
        (None, {
            'fields': ('name', 'ip', 'jboss_home', 'erp_home', 'folder_version', 'user_ssh', 'password_ssh')
        }),
    )
    list_display = ['name', 'ip', 'jboss_home', 'erp_home']

admin.site.register(ServerJboss, JbossServerAdmin)




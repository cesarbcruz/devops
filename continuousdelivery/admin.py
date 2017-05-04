from django.contrib import admin
from django.contrib.admin import ModelAdmin

from continuousdelivery.forms import Global_ParametersAdminForm
from continuousdelivery.models import Global_Parameters


class Global_ParametersAdmin(ModelAdmin):
    form = Global_ParametersAdminForm
    fieldsets = (
        (None, {
            'fields': ('smtp_server', 'smtp_port', 'email_sender', 'password_email_sender')
        }),
    )
    list_display = ['smtp_server', 'smtp_port', 'email_sender']

admin.site.register(Global_Parameters, Global_ParametersAdmin)




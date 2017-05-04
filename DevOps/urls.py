from django.contrib import admin
from django.conf.urls import include, url

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^continuousdelivery/', include('continuousdelivery.urls')),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
]

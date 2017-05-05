from django.contrib import admin
from django.conf.urls import include, url
from django.contrib.auth.views import login, logout
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^continuousdelivery/', include('continuousdelivery.urls')),
    url(r'^', include('accounts.urls', namespace='accounts')),
    url(r'^login/$', login, {'template_name': 'accounts/login.html'}, name='login'),
    url(r'^logout/$', logout, {'next_page': 'accounts:index'}, name='logout'),
]

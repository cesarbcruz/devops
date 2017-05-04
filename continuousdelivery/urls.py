from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', views.Deploy.as_view(), name='deploy'),
    url(r'^resultdeploy$', views.ResultDeploy.as_view(), name='resultdeploy'),
]

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.Deploy.as_view(), name='deploy'),
    url(r'^sucessdeploy$', views.SucessDeploy.as_view(), name='sucessdeploy'),
]

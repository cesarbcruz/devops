from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.Deploy.as_view(), name='deploy'),
    url(r'^resultdeploy$', views.ResultDeploy.as_view(), name='resultdeploy'),
    url(r'^archivebinaries$', views.ArchiveBinaries.as_view(), name='archivebinaries'),
    url(r'^viewlog$', views.ViewLog.as_view(), name='viewlog'),
]

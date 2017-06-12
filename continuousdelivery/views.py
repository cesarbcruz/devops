import os
import zipfile
from io import StringIO
from django.http import HttpResponse
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from .forms import DeployForm, ArchiveBinariesForm
from django.contrib.auth.mixins import LoginRequiredMixin

class Deploy(LoginRequiredMixin, FormView):
    template_name = "deploy.html"
    form_class = DeployForm
    success_url = "resultdeploy"

    def dispatch(self, *args, **kwargs):
           return super(Deploy, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.execute(self.request)
        return super(Deploy, self).form_valid(form)

class ResultDeploy(LoginRequiredMixin, TemplateView):
    template_name = "result_deploy.html"
    def get_context_data(self, **kwargs):
        context = super(ResultDeploy, self).get_context_data(**kwargs)
        context['log'] = self.request.session['log']
        return context

class ArchiveBinaries(LoginRequiredMixin, FormView):
    template_name = "archive_binaries.html"
    form_class = ArchiveBinariesForm
    success_url = "archivebinaries"

    def dispatch(self, *args, **kwargs):
           return super(ArchiveBinaries, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        path_version = form.select_version(self.request)
        version = path_version.split("/")
        name_zip = '{}.zip'.format(version[len(version)-1])
        path_zip = "/tmp/{}".format(name_zip)
        zipf = zipfile.ZipFile(path_zip, 'w', zipfile.ZIP_DEFLATED)
        zipdir(path_version, zipf)
        zipf.close()
        response = HttpResponse(open(path_zip, 'rb').read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="%s"' % name_zip
        return response

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


class ViewLog(LoginRequiredMixin, TemplateView):
    template_name = "view_log.html"
    def get_context_data(self, **kwargs):
        context = super(ViewLog, self).get_context_data(**kwargs)
        log = ""
        try:

            log = tail(open("/tmp/devops.log", "r"), 5)
        except Exception as ex:
            log = ex
        context['log'] = log
        return context

def tail(f,n):
    return "\n".join(f.read().split("\n")[-n:])
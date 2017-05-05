import os
import zipfile
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
        zip_io = make_zipfile("binaries.zip", form.select_version(self.request))
        response = HttpResponse(zip_io, content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename=%s' % 'binaries' + ".zip"
        #response['Content-Length'] = zip_io.()
        return response

def make_zipfile(output_filename, source_dir):
    relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(source_dir):
            # add directory (needed for empty dirs)
            zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename): # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    zip.write(filename, arcname)
    return zip
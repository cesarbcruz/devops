from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from .forms import DeployForm

class Deploy(FormView):
    template_name = "deploy.html"
    form_class = DeployForm
    success_url = "sucessdeploy"

    def form_valid(self, form):
        form.execute()
        return super(Deploy, self).form_valid(form)

class SucessDeploy(TemplateView):

    template_name = "sucess_deploy.html"

    def get_context_data(self, **kwargs):
        context = super(SucessDeploy, self).get_context_data(**kwargs)
        log_file = open("deploy.log", "r")
        log = log_file.read();
        log_file.close()
        context['log'] = log
        return context
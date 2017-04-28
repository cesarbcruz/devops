from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from .forms import DeployForm

class Deploy(FormView):
    template_name = "deploy.html"
    form_class = DeployForm
    success_url = "resultdeploy"

    def form_valid(self, form):
        form.execute()
        return super(Deploy, self).form_valid(form)

class ResultDeploy(TemplateView):

    template_name = "result_deploy.html"

    def get_context_data(self, **kwargs):
        context = super(ResultDeploy, self).get_context_data(**kwargs)
        log_file = open("deploy.log", "r")
        log = log_file.read();
        log_file.close()
        context['log'] = log
        return context
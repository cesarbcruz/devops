from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from .forms import DeployForm
import re
from django.contrib.auth.mixins import LoginRequiredMixin

class Deploy(LoginRequiredMixin, FormView):
    template_name = "deploy.html"
    form_class = DeployForm
    success_url = "resultdeploy"

    def dispatch(self, *args, **kwargs):
           return super(Deploy, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.execute(self.request.user)
        return super(Deploy, self).form_valid(form)

class ResultDeploy(LoginRequiredMixin, TemplateView):

    template_name = "result_deploy.html"

    def get_context_data(self, **kwargs):
        context = super(ResultDeploy, self).get_context_data(**kwargs)
        infile = open("deploy.log", "r")
        lines = ""
        for line in infile:
            if not line.strip():
                continue
            else:

                lines += format_log(line)
        infile.close()
        context['log'] = lines
        return context


def format_log(line):
    formated_line = line.replace("INFO", "<span style='color: green'>INFO</span> ")
    formated_line = formated_line.replace("ERROR", "<span style='color: red'>ERROR</span> ")
    date_time_log = re.search('[\d]+\-[\d]+\-[\d]+\ [\d]+\:[\d]+\:[\d]+\,[\d]+', formated_line)
    if date_time_log:
        formated_line = formated_line.replace(date_time_log.group(0),"<span style='color: blue'>{}</span> ".format(date_time_log.group(0)))

    return formated_line
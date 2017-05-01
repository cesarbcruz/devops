from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from .forms import DeployForm
import re

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
        infile = open("deploy.log", "r")
        lines = ""
        for line in infile:
            if not line.strip():
                continue
            else:
                formated_line = line.replace("INFO", "<span style='color: green'>INFO</span> ")
                formated_line = formated_line.replace("ERROR", "<span style='color: red'>ERROR</span> ")
                date_time_log = re.search('[\d]+\-[\d]+\-[\d]+\ [\d]+\:[\d]+\:[\d]+\,[\d]+', formated_line)
                if date_time_log:
                    formated_line = formated_line.replace(date_time_log.group(0), "<span style='color: blue'>{}</span> ".format(date_time_log.group(0)))
                lines += formated_line
        infile.close()
        context['log'] = lines
        return context
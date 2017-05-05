# -*- coding: utf-8 -*-
from django import forms
import tempfile, errno, shutil, time

from continuousdelivery import Deploy
from continuousdelivery.models import Global_Parameters, ServerJboss

class DeployForm(forms.Form):
    url_project_repository = forms.CharField(label='URL Project Repository')
    server_jboss = forms.ModelChoiceField(label='Server Jboss destination', queryset=ServerJboss.objects.all().order_by('ip'))
    TYPE_DEPLOY = (
        (Deploy.partial, 'Only send the binaries to the server'),
        (Deploy.partial, 'Send binaries and deploy in jboss'),
    )
    type_deploy = forms.ChoiceField(label='Type deploy', widget=forms.RadioSelect, choices=TYPE_DEPLOY, initial=Deploy.partial)

    def execute(self, user):
        start_time = time.time()
        logger = Deploy.create_log_deploy()
        logger.info('URL project repository: {}'.format(self.cleaned_data['url_project_repository']))
        server_jboss = self.cleaned_data['server_jboss']
        logger.info('Server Jboss destination: {}'.format(server_jboss.ip))
        try:
            dirpath = tempfile.mkdtemp()
            Deploy.validate_user(user)
            global_parameters = Deploy.get_send_email_notificaton()
            logger.info('Create dir temp: {}'.format(dirpath))
            Deploy.checkout_project(self.cleaned_data['url_project_repository'], dirpath, logger)
            binary_files = Deploy.get_binary_files(dirpath)
            Deploy.compile_project(dirpath, logger, binary_files)
            version = Deploy.get_version_project(dirpath)
            tag = Deploy.create_tag_svn("TAG_VER_{}".format(version), self.cleaned_data['url_project_repository'], logger, user.repository_user, user.repository_password)
            folder_version = "/usr/local/nova_versao/"
            folder_destination = "{}/{}/".format(folder_version, version)
            Deploy.send_email_notificaton(version, server_jboss.ip, tag, folder_destination, logger, global_parameters, user)
            Deploy.send_binaries(server_jboss.ip, binary_files, folder_destination, server_jboss.user_ssh, server_jboss.password_ssh, logger, server_jboss.jboss_home, server_jboss.erp_home, (self.cleaned_data['type_deploy']))
            t_sec = round(time.time() - start_time)
            (t_min, t_sec) = divmod(t_sec, 60)
            (t_hour, t_min) = divmod(t_min, 60)
            logger.info('Time processing: {}hour:{}min:{}sec'.format(t_hour, t_min, t_sec))
        except Exception as ex:
            logger.error(ex, exc_info=True)
        finally:
            try:
                shutil.rmtree(dirpath, ignore_errors=False)
            except OSError as exc:
                if exc.errno != errno.ENOENT:
                    raise

class Global_ParametersAdminForm(forms.ModelForm):
    class Meta:
        model = Global_Parameters
        fields = ['smtp_server', 'smtp_port', 'email_sender', 'password_email_sender']
        widgets = {
            'password_email_sender': forms.PasswordInput(render_value=True),
        }

class ServerJbossAdminForm(forms.ModelForm):
    class Meta:
        model = ServerJboss
        fields = ['name', 'ip', 'jboss_home', 'erp_home', 'folder_version', 'user_ssh', 'password_ssh']
        widgets = {
            'password_ssh': forms.PasswordInput(render_value=True),
        }
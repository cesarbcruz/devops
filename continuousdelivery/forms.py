# -*- coding: utf-8 -*-
from django import forms
import tempfile, errno, shutil, time, os
from continuousdelivery import DeployRun
from continuousdelivery.models import Global_Parameters, ServerJboss
from multiprocessing import Process

class DeployForm(forms.Form):
    url_project_repository = forms.CharField(label='URL Project Repository')
    server_jboss = forms.ModelChoiceField(label='Server Jboss destination', queryset=ServerJboss.objects.all().order_by('ip'))
    TYPE_DEPLOY = (
        (DeployRun.partial, 'Only send the binaries to the server'),
        (DeployRun.complete, 'Send binaries and deploy in jboss'),
    )
    type_deploy = forms.ChoiceField(label='Type deploy', widget=forms.Select, choices=TYPE_DEPLOY, initial=DeployRun.partial)
    activate_vpn = forms.BooleanField(required=False,initial=False,label='Activate VPN')

    def execute(self, request):
        try:
            start_time = time.time()
            dirpath = tempfile.mkdtemp()
            logger = DeployRun.create_log_deploy(dirpath)
            global_parameters = DeployRun.get_global_parameters()
            process_vpn = Process(target=DeployRun.activate_vpn, args=(self.cleaned_data['activate_vpn'], request.user, global_parameters, logger))
            process_vpn.start()
            logger.info('URL project repository: {}'.format(self.cleaned_data['url_project_repository']))
            server_jboss = self.cleaned_data['server_jboss']
            logger.info('Server Jboss destination: {}'.format(server_jboss.ip))
            DeployRun.validate_user(request.user)
            logger.info('Create dir temp: {}'.format(dirpath))
            DeployRun.checkout_project(self.cleaned_data['url_project_repository'], dirpath, logger)
            binary_files = DeployRun.get_binary_files(dirpath)
            DeployRun.compile_project(dirpath, logger, binary_files)
            version = DeployRun.get_version_project(dirpath)
            md5sum = DeployRun.archive_binaries(global_parameters.folder_archive_binaries, version, logger, binary_files)
            tag = DeployRun.create_tag_svn("TAG_VER_{}".format(version), self.cleaned_data['url_project_repository'], logger, request.user.repository_user, request.user.repository_password)
            folder_destination = "{}{}/".format(DeployRun.include_path_separator(server_jboss.folder_version), version)
            DeployRun.send_binaries(server_jboss.ip, binary_files, folder_destination, server_jboss.user_ssh, server_jboss.password_ssh, logger, server_jboss.jboss_home, server_jboss.erp_home, (self.cleaned_data['type_deploy']), md5sum)
            DeployRun.send_email_notificaton(version, server_jboss.ip, tag, folder_destination, logger, global_parameters, request.user)
            t_sec = round(time.time() - start_time)
            (t_min, t_sec) = divmod(t_sec, 60)
            (t_hour, t_min) = divmod(t_min, 60)
            logger.info('Time processing: {}hour:{}min:{}sec'.format(t_hour, t_min, t_sec))
            logger.info("Do not forget to update the cvs")

        except Exception as ex:
            logger.error(ex, exc_info=True)
        finally:
            DeployRun.kill_vpn()
            request.session['log'] = DeployRun.read_log(dirpath)
            try:
                shutil.rmtree(dirpath, ignore_errors=False)
            except OSError as exc:
                if exc.errno != errno.ENOENT:
                    raise

class Global_ParametersAdminForm(forms.ModelForm):
    class Meta:
        model = Global_Parameters
        fields = ['smtp_server', 'smtp_port', 'email_sender', 'password_email_sender', 'folder_archive_binaries', 'folder_vpn_certificate']
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

class ArchiveBinariesForm(forms.Form):
    versions = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(ArchiveBinariesForm, self).__init__(*args, **kwargs)
        global_parameters = DeployRun.get_global_parameters()
        list_version = []
        list_version.append(["", "--------"])
        if os.path.exists(global_parameters.folder_archive_binaries):
            for file in os.listdir(global_parameters.folder_archive_binaries):
                list_version.append(["{}{}".format(global_parameters.folder_archive_binaries, file), file])
        self.fields['versions'] = forms.ChoiceField(widget=forms.Select(), choices=list_version)

    def select_version(self, request):
        return self.cleaned_data['versions']

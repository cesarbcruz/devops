# -*- coding: utf-8 -*-
from django import forms
import subprocess, tempfile, os, re, errno, shutil, logging, smtplib, time
from email.mime.text import MIMEText
import pexpect
from pexpect import pxssh

#param global
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
sender = 'logicnotice@gmail.com'
pwd_email = 'pa33Lx$k'
destinatario = 'cesar@logicsp.com.br'
# 'michael.serafim@logicsp.com.br, roberto@logicsp.com.br, cesar@logicsp.com.br, ' \
#'tadeu.santos@logicsp.com.br, daniel@logicsp.com.br'

#param user
user_svn = "cesar"
password_svn = "Herminia2"

#param project repository
path_parametros = 'ERP-jar/src/main/java/logic/covabra/framework/parametros/ParametrosGlobaisERP.java'
url_tags = 'http://172.16.50.2/svn/repositorioCovabra/ERP/tags/'

#param server destination
jboss_home = "/usr/local/jboss-eap-6.1/"
erp_home = "/usr/local/prj_ERP_Producao/"
folder_destination_base="/usr/local/nova_versao/{}/"
user_destination = "root"
password_destination = "pa33Lx$k"

partial = 0
complete = 1

class DeployForm(forms.Form):
    url_project_repository = forms.CharField(label='URL Project Repository')
    ip_destination = forms.CharField(label='IP Destination')
    TYPE_DEPLOY = (
        (partial, 'Only send the binaries to the server'),
        (complete, 'Send binaries and deploy in jboss'),
    )
    type_deploy = forms.ChoiceField(label='Type deploy', widget=forms.RadioSelect, choices=TYPE_DEPLOY, initial=partial)

    def execute(self):
        start_time = time.time()
        logger = create_log_deploy()
        logger.info('URL project repository: {}'.format(self.cleaned_data['url_project_repository']))
        logger.info('IP destination: {}'.format(self.cleaned_data['ip_destination']))
        try:
            dirpath = tempfile.mkdtemp()
            logger.info('Create dir temp: {}'.format(dirpath))
            checkout_project(self.cleaned_data['url_project_repository'], dirpath, logger)
            compile_project(dirpath, logger)
            version = get_version_project(dirpath)
            tag = create_tag_svn("TAG_VER_{}".format(version), self.cleaned_data['url_project_repository'], logger, user_svn, password_svn)
            folder_destination = folder_destination_base.format(version)
            send_email_notificaton(version, self.cleaned_data['ip_destination'], tag, folder_destination, logger)
            binary_files = get_binary_files(dirpath)
            send_binaries(self.cleaned_data['ip_destination'], binary_files, folder_destination, user_destination, password_destination, logger, jboss_home, (self.cleaned_data['type_deploy']))
            t_sec = round(time.time() - start_time)
            (t_min, t_sec) = divmod(t_sec, 60)
            (t_hour, t_min) = divmod(t_min, 60)
            logger.info('Time processing: {}hour:{}min:{}sec'.format(t_hour, t_min, t_sec))
        except Exception as ex:
            logger.error(ex, exc_info=True)
        finally:
            try:
                shutil.rmtree(dirpath)
            except OSError as exc:
                if exc.errno != errno.ENOENT:
                    raise

def checkout_project(url, dirpath, logger):
    subprocess.call('svn checkout {0} {1}'.format(url, dirpath) , shell=True)
    logger.info('Checkout project: {} '.format(url))

def compile_project(dirpath, logger):
    subprocess.call('cd {0}; mvn install -Dmaven.test.skip=true'.format(dirpath), shell=True)
    logger.info('Compiled project')

def get_version_project(dirpath):
    conteudo_arquivo = open(os.path.join(dirpath, path_parametros)).read()
    return re.search('[\d]+\.[\d]+\.[\d]+', conteudo_arquivo).group(0).replace('.', '_')

def create_tag_svn(version, url, logger, user_svn, password_svn):
    tags = subprocess.check_output('svn ls {}'.format(url_tags), shell=True)
    if bytes(version,"utf-8") in tags:
        logger.info('Removing old tag: {}'.format(version))
        subprocess.call('svn delete {0}{1} -m "Removendo TAG Automaticamente Sistema Deploy" {2}'.format(url_tags, version, get_credentials_svn(user_svn, password_svn)), shell=True)

    logger.info('Create TAG: {0} -> {1}{2}'.format(url, url_tags, version))
    subprocess.call('svn copy {0} {1}{2} -m "Criando TAG Automaticamente Sistema Deploy" {3}'.format(url, url_tags.replace('\n',''), version, get_credentials_svn(user_svn, password_svn)),shell=True)
    return "{0}{1}".format(url_tags, version)


def create_log_deploy():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('deploy.log', mode='w')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def send_email_notificaton(version, ip_destination, tag, folder_destination, logger):
    user = "TESTE DEPLOY"
    msg = MIMEText(
        'Nova versao: {0} e TAG: {1} geradas.\n'
        'Usuario: {2}.\n'
        'Upload realizado no servidor {3} em {4}\n'
        'Não esqueça de atualizar o CVS para uma futura equalização de versão!'.format(
            version, tag, user, ip_destination, folder_destination))
    msg['Subject'] = 'Versão {} gerada'.format(version)
    msg['To'] = destinatario
    msg['From'] = sender

    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.ehlo()
    session.starttls()
    session.ehlo()
    session.login(sender, pwd_email)
    session.sendmail(sender, destinatario.split(', '), msg.as_string())
    session.quit()

    logger.info('Send email notification : {}'.format(destinatario))

def get_credentials_svn(user_svn, password_svn):
    return " --non-interactive --trust-server-cert --username {0} --password {1}".format(user_svn, password_svn)

def get_binary_files(dirpath):
    return "{0}/ERP-jar/target/ERP-jar.jar " \
           "{0}/ERP-jar/target/staging/dependency/ERP-ejb.jar " \
           "{0}/ERP-ear/target/ERP-ear-1.0-SNAPSHOT.ear " \
           "{0}/ERP-web/target/ERP-web.war " \
        .format(dirpath)

def send_binaries(hostname, binary_files, folder_destination, username, password, logger, jboss_home, type_deploy):
    s = pxssh.pxssh()
    s.login(hostname, username, password)

    execute_command(s, "rm -rf {}".format(folder_destination), logger)
    execute_command(s, "mkdir {}".format(folder_destination), logger)

    var_command = "scp {0} {1}@{2}:{3}/.".format(binary_files, username, hostname, folder_destination)
    var_child = pexpect.spawn(var_command)
    i = var_child.expect(["password:", pexpect.EOF])

    if i == 0:  # send password
        var_child.sendline(password)
        var_child.expect(pexpect.EOF, timeout=500)
        logger.info("Binaries sent to {}".format(hostname))
    elif i == 1:
        logger.error("Got the key or connection timeout")

    if type_deploy == str(complete):
        execute_command(s, "cp {0}{1} {2}.".format(folder_destination, "ERP-jar.jar", erp_home), logger)
        execute_command(s, "cp {0}{1} {2}lib/.".format(folder_destination, "ERP-ejb.jar", erp_home), logger)
        execute_command(s, "service jboss stop", logger)
        execute_command(s, "cp {0}{1} {2}standalone/deployments/".format(folder_destination, "ERP-ear-1.0-SNAPSHOT.ear", jboss_home), logger)
        execute_command(s, "cp {0}{1} {2}standalone/deployments/".format(folder_destination, "ERP-web.war", jboss_home), logger)
        execute_command(s, "service jboss start", logger)

    s.logout()

def execute_command(s, cmd, logger):
    s.sendline(cmd)
    s.prompt()
    logger.info(str(s.before, 'utf-8'))
# -*- coding: utf-8 -*-
from django import forms
import subprocess, tempfile, os, re, errno, shutil, logging, smtplib
from email.mime.text import MIMEText

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
sender = 'logicnotice@gmail.com'
pwd_email = 'pa33Lx$k'
destinatario = 'cesar@logicsp.com.br'
# 'michael.serafim@logicsp.com.br, roberto@logicsp.com.br, cesar@logicsp.com.br, ' \
#'tadeu.santos@logicsp.com.br, daniel@logicsp.com.br'

class DeployForm(forms.Form):
    url_project_repository = forms.CharField(label='URL Projeto Repositório')
    ip_destination = forms.CharField(label='IP Destino')

    def execute(self):
        logger = create_log_deploy()
        logger.info('URL project repository: {}'.format(self.cleaned_data['url_project_repository']))
        logger.info('IP destination: {}'.format(self.cleaned_data['ip_destination']))
        try:
            dirpath = tempfile.mkdtemp()
            logger.info('Create dir temp: {}'.format(dirpath))
            checkout_project(self.cleaned_data['url_project_repository'], dirpath, logger)
            compile_project(dirpath, logger)
            version = get_version_project(dirpath)
            tag = create_tag_svn("TAG_VER_{}".format(version), self.cleaned_data['url_project_repository'], logger)
            folder_destination = "/usr/local/nova_versao/{}".format(version)
            send_email_notificaton(version, self.cleaned_data['ip_destination'], tag, folder_destination, logger)
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
    path_parametros = 'ERP-jar/src/main/java/logic/covabra/framework/parametros/ParametrosGlobaisERP.java'
    conteudo_arquivo = open(os.path.join(dirpath, path_parametros)).read()
    return re.search('[\d]+\.[\d]+\.[\d]+', conteudo_arquivo).group(0).replace('.', '_')

def create_tag_svn(version, url, logger):
    url_tags = 'http://172.16.50.2/svn/repositorioCovabra/ERP/tags/'

    tags = subprocess.check_output('svn ls {}'.format(url_tags), shell=True)
    if bytes(version,"utf-8") in tags:
        logger.info('Removing old tag: {}'.format(version))
        subprocess.call('svn delete {0}{1} -m "Removendo TAG Automaticamente Sistema Deploy"'.format(url_tags, version), shell=True)
    logger.info('Create TAG: {0} -> {1}{2}'.format(url, url_tags, version))
    subprocess.call('svn copy {0} {1}{2} -m "Criando TAG Automaticamente Sistema Deploy"'.format(url, url_tags.replace('\n',''), version),shell=True)
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
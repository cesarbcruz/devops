# -*- coding: utf-8 -*-
from django import forms
import subprocess, tempfile, os, re, errno, shutil, logging

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
            create_tag_svn("TAG_VER_{}".format(version), self.cleaned_data['url_project_repository'], logger)
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


def create_log_deploy():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('deploy.log', mode='w')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

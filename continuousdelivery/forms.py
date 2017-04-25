# -*- coding: utf-8 -*-
from django import forms
import subprocess, tempfile, os, re

class DeployForm(forms.Form):
    url_build_jenkins = forms.CharField(label='URL Build Jenkins')
    ip_destination = forms.CharField(label='IP Destino')

    def execute(self):
        print(self.cleaned_data['url_build_jenkins'])
        print(self.cleaned_data['ip_destination'])

        dirpath = tempfile.mkdtemp()
        print(dirpath)
        checkout_project(self.cleaned_data['url_build_jenkins'], dirpath)
        compile_project(dirpath)
        print(get_version_project(dirpath))

        pass

def checkout_project(url, dirpath):
	subprocess.call('svn checkout {0} {1}'.format(url, dirpath) , shell=True)

def compile_project(dirpath):
	subprocess.call('cd {0}; mvn install -Dmaven.test.skip=true'.format(dirpath), shell=True)

def get_version_project(dirpath):
    path_parametros = 'ERP-jar/src/main/java/logic/covabra/framework/parametros/ParametrosGlobaisERP.java'
    conteudo_arquivo = open(os.path.join(dirpath, path_parametros)).read()
    return re.search('[\d]+\.[\d]+\.[\d]+', conteudo_arquivo).group(0).replace('.', '_')

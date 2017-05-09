# -*- coding: utf-8 -*-
import subprocess, os, re, logging, smtplib
from email.mime.text import MIMEText
import async as async
import pexpect
from pexpect import pxssh
import os.path
from accounts.models import User
from continuousdelivery.models import Global_Parameters
import urllib.request

partial = 0
complete = 1

path_parametros = 'ERP-jar/src/main/java/logic/covabra/framework/parametros/ParametrosGlobaisERP.java'
url_tag_base = 'http://{}/svn/repositorioCovabra/ERP/tags/'

def checkout_project(url, dirpath, logger):
    if url_is_alive("{}{}".format(url,path_parametros)):
        subprocess.call('svn checkout {0} {1}'.format(url, dirpath) , shell=True)
        logger.info('Checkout project: {} '.format(url))
    else:
        raise "Repository URL incorrect"

def url_is_alive(url):
    request = urllib.request.Request(url)
    request.get_method = lambda: 'HEAD'

    try:
        urllib.request.urlopen(request)
        return True
    except urllib.request.HTTPError:
        return False

def compile_project(dirpath, logger, binary_files):
    subprocess.call('cd {0}; mvn install -Dmaven.test.skip=true'.format(dirpath), shell=True)
    for binary in binary_files.split(" "):
        if not os.path.exists(binary):
            raise "Compilation failed"

    logger.info('Compiled project')

def archive_binaries(folder_archive_binaries, version, logger, binary_files):
    folder_archive_binaries = "{}{}/".format(include_path_separator(folder_archive_binaries), version)
    subprocess.call("rm -rf {}".format(folder_archive_binaries), shell=True)
    subprocess.call("mkdir {}".format(folder_archive_binaries), shell=True)
    subprocess.call("cp {0} {1}.".format(binary_files, folder_archive_binaries), shell=True)
    logger.info('Archive binaries')

def get_version_project(dirpath):
    conteudo_arquivo = open(os.path.join(dirpath, path_parametros)).read()
    return re.search('[\d]+\.[\d]+\.[\d]+', conteudo_arquivo).group(0).replace('.', '_')

def create_tag_svn(version, url, logger, user_svn, password_svn):
    url_tag = url_tag_base.format(url.split("/")[2])

    if not url_is_alive(url_tag):
        raise "Repository URL for tag does not exist: {}".format(url_tag)

    tags = subprocess.check_output('svn ls {}'.format(url_tag), shell=True)
    if bytes(version,"utf-8") in tags:
        logger.info('Removing old tag: {}'.format(version))
        subprocess.call('svn delete {0}{1} -m "Removendo TAG Automaticamente Sistema Deploy" {2}'.format(url_tag, version, get_credentials_svn(user_svn, password_svn)), shell=True)

    logger.info('Create TAG: {0} -> {1}{2}'.format(url, url_tag, version))
    subprocess.call('svn copy {0} {1}{2} -m "Criando TAG Automaticamente Sistema Deploy" {3}'.format(url, url_tag.replace('\n',''), version, get_credentials_svn(user_svn, password_svn)),shell=True)
    return "{0}{1}".format(url_tag, version)


def create_log_deploy(path):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('{}/deploy.log'.format(path), mode='w')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def read_log(path):
    infile = open('{}/deploy.log'.format(path), "r")
    log = ""
    for line in infile:
        if not line.strip():
            continue
        else:
            log += format_log(line)
    infile.close()
    return log

def format_log(line):
    formated_line = line.replace("INFO", "<span style='color: green'>INFO</span> ")
    formated_line = formated_line.replace("ERROR", "<span style='color: red'>ERROR</span> ")
    date_time_log = re.search('[\d]+\-[\d]+\-[\d]+\ [\d]+\:[\d]+\:[\d]+\,[\d]+', formated_line)
    if date_time_log:
        formated_line = formated_line.replace(date_time_log.group(0),"<span style='color: blue'>{}</span> ".format(date_time_log.group(0)))

    return formated_line

def send_email_notificaton(version, ip_destination, tag, folder_destination, logger, global_parameters, user):
    email_destination = get_email_destination(user)
    msg = MIMEText(
        'Nova versao: {0} e TAG: {1} geradas.\n'
        'Usuario: {2}.\n'
        'Upload realizado no servidor {3} em {4}\n'
        'Não esqueça de atualizar o CVS para uma futura equalização de versão!'.format(
            version, tag, user.name, ip_destination, folder_destination))
    msg['Subject'] = 'Versão {} gerada'.format(version)
    msg['To'] = email_destination
    msg['From'] = global_parameters.email_sender

    session = smtplib.SMTP(global_parameters.smtp_server, global_parameters.smtp_port)
    session.ehlo()
    session.starttls()
    session.ehlo()
    session.login(global_parameters.email_sender, global_parameters.password_email_sender)
    session.sendmail(global_parameters.email_sender, email_destination.split(', '), msg.as_string())
    session.quit()

    logger.info('Send email notification : {}'.format(email_destination))

def get_credentials_svn(user_svn, password_svn):
    return " --non-interactive --trust-server-cert --username {0} --password {1}".format(user_svn, password_svn)

def get_binary_files(dirpath):
    return "{0}/ERP-jar/target/ERP-jar.jar " \
           "{0}/ERP-jar/target/staging/dependency/ERP-ejb.jar " \
           "{0}/ERP-ear/target/ERP-ear-1.0-SNAPSHOT.ear " \
           "{0}/ERP-web/target/ERP-web.war" \
        .format(dirpath)

def send_binaries(hostname, binary_files, folder_destination, username, password, logger, jboss_home, erp_home, type_deploy):
    folder_destination = include_path_separator(folder_destination)
    jboss_home = include_path_separator(jboss_home)
    erp_home = include_path_separator(erp_home)
    s = pxssh.pxssh()
    s.login(hostname, username, password)

    execute_command(s, "rm -rf {}".format(folder_destination), logger)
    execute_command(s, "mkdir {}".format(folder_destination), logger)

    var_command = "scp {0} {1}@{2}:{3}.".format(binary_files, username, hostname, folder_destination)
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

def get_global_parameters():
    global_parameters = Global_Parameters.objects.all()
    if global_parameters:
        return global_parameters[0]
    else:
        raise "Unconfigured global parameters"

def validate_user(user):
    if not user.repository_user:
        raise "Unconfigured repository user"
    if not user.repository_password:
        raise "Unconfigured repository password"

def get_email_destination(user):
    email_destination = user.email
    l = user.groups.values_list('name', flat=True)
    users = User.objects.filter(groups__name=l ).exclude(id=user.id)
    for user in users:
        email_destination += ", {}".format(user.email)

    return email_destination

def include_path_separator(path):
    if not path.endswith('/'):
        path += "/"
    return path

@async
def activate_vpn(activate_vpn, user, global_parameters, logger):
    if activate_vpn:
        try:
            folder_vpn_certificate_user = "{}{}/".format(include_path_separator(global_parameters.folder_vpn_certificate), user.username)
            file_ovpn = None
            for file in os.listdir(folder_vpn_certificate_user):
                if file.endswith(".ovpn"):
                    file_ovpn = file
            if file_ovpn:
                name_file_auth = ".auth.txt"
                create_file_auth(folder_vpn_certificate_user, user, name_file_auth)
                kill_vpn()
                p = subprocess.Popen(['openvpn', '--config', file_ovpn, '--auth-user-pass', name_file_auth], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=folder_vpn_certificate_user)
                stdout, stderr = p.communicate()
                if stdout:
                    if bytes('ERROR',"utf-8") in stdout:
                        raise Exception(stdout)
                    else:
                        logger.info(stdout)
                if stderr:
                    raise Exception(stderr)
            else:
                raise "VPN file not found"
        except:
            raise

def create_file_auth(folder_vpn_certificate_user, user, name_file_auth):
    if not os.path.exists("{}{}".format(folder_vpn_certificate_user, name_file_auth)):
        with open('{}{}'.format(folder_vpn_certificate_user, name_file_auth),'w') as out:
            out.write('{}\n{}'.format(user.vpn_user, user.vpn_password))


def kill_vpn():
    subprocess.call('killall openvpn', shell=True)

from django.db import models

class Global_Parameters(models.Model):
    smtp_server = models.CharField(max_length=200)
    smtp_port = models.CharField(max_length=5)
    email_sender = models.CharField(max_length=200)
    password_email_sender = models.CharField(max_length=200)
    folder_archive_binaries = models.CharField(max_length=200)
    folder_vpn_certificate = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Global Parameter'
        verbose_name_plural = 'Global Parameters'

class ServerJboss(models.Model):
    name = models.CharField(max_length=200)
    ip = models.CharField(max_length=200)
    jboss_home = models.CharField(max_length=500)
    erp_home = models.CharField(max_length=500)
    folder_version = models.CharField(max_length=200)
    user_ssh = models.CharField(max_length=200)
    password_ssh = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Server Jboss'
        verbose_name_plural = 'Servers Jboss'

    def __str__(self):
        return "{0} {1}".format(self.ip, self.name)
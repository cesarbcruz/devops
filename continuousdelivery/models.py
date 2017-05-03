from django.db import models

class Global_Parameters(models.Model):
    smtp_server = models.CharField(max_length=200)
    smtp_port = models.CharField(max_length=5)
    email_sender = models.CharField(max_length=200)
    password_email_sender = models.CharField(max_length=200)
    email_destination = models.CharField(max_length=2000)



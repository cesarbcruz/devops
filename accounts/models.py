# coding=utf-8

import re

from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin

class User(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(
        'Nickname / User', max_length=30, unique=True, validators=[
            validators.RegexValidator(
                re.compile('^[\w.@+-]+$'),
                'Enter a valid username.'
                'This value must contain only letters, numbers '
                'and the characters: @/./+/-/_ .'
                , 'invalid'
            )
        ], help_text='A short name that will be used to uniquely identify'
    )
    name = models.CharField('Name', max_length=100, blank=True)
    email = models.EmailField('E-mail', unique=True)
    is_staff = models.BooleanField('Team', default=False)
    is_active = models.BooleanField('Active', default=True)
    date_joined = models.DateTimeField('Entry date', auto_now_add=True)
    repository_user = models.CharField('Repository user', max_length=100, blank=True)
    repository_password = models.CharField('Repository password', max_length=100, blank=True)
    vpn_user = models.CharField('VPN user', max_length=100, blank=True)
    vpn_password = models.CharField('VPN password', max_length=100, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.name or self.username

    def get_full_name(self):
        return str(self)

    def get_short_name(self):
        return str(self).split(" ")[0]
# coding=utf-8
from django import forms
from django.views.generic import (
    CreateView, TemplateView, UpdateView, FormView
)
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm

from .models import User
from .forms import UserAdminCreationForm


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/index.html'


class RegisterView(CreateView):

    model = User
    template_name = 'accounts/register.html'
    form_class = UserAdminCreationForm
    success_url = reverse_lazy('index')


class UpdateUserView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'accounts/update_user.html'
    fields = ['name', 'email', 'repository_user', 'repository_password', 'vpn_user', 'vpn_password']
    success_url = reverse_lazy('accounts:index')

    def get_object(self):
        return self.request.user

    def get_form(self, form_class=None):
        form = super(UpdateUserView, self).get_form(form_class)
        form.fields['repository_password'].widget = forms.PasswordInput(render_value=True)
        form.fields['vpn_password'].widget = forms.PasswordInput(render_value=True)
        return form


class UpdatePasswordView(LoginRequiredMixin, FormView):
    template_name = 'accounts/update_password.html'
    success_url = reverse_lazy('accounts:index')
    form_class = PasswordChangeForm

    def get_form_kwargs(self):
        kwargs = super(UpdatePasswordView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(UpdatePasswordView, self).form_valid(form)


index = IndexView.as_view()
register = RegisterView.as_view()
update_user = UpdateUserView.as_view()
update_password = UpdatePasswordView.as_view()

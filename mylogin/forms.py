# -*- coding: UTF-8 -*-
from django import forms


class MyLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput)
#-*- coding:UTF-8 -*-
from django import forms
from django.contrib.auth.models import User

from account.models import Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='密码',widget=forms.PasswordInput)
    repeat_password = forms.CharField(label='确认密码',widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('username','email')
    
    def clean_repeat_password(self):
        data = self.cleaned_data
        if data['password'] != data['repeat_password']:
            raise forms.ValidationError('密码不一样，请再次确认。')
        return data['repeat_password']
 
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'photo')

        
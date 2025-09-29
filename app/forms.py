from django import forms
from django.contrib.auth.models import User
from .models import Project

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

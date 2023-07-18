from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User

from .models import ProfileModel

""" class LoginForm(forms.Form):
    username = forms.CharField(max_length=63, required=True, label='Nom d’utilisateur')
    password = forms.CharField(max_length=63, widget=forms.PasswordInput, required=True, label='Mot de passe')

    def clean_confirm_password(self):
        user_name = self.cleaned_data.get('user_name')
        password = self.cleaned_data.get('password')
        if user_name and password and password != user_name:
            raise forms.ValidationError("Passwords didn't match.")
        return password

    def clean_password(self):
        user_name = self.cleaned_data.get('user_name')
        password = self.cleaned_data.get('password')
        return authenticate(user_name=user_name, password=password)
        """


class SigninForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(SigninForm, self).__init__(*args, **kwargs)

        for field_name in ['username', 'email', 'password1', 'password2']:
            self.fields[field_name].help_text = None


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = ProfileModel
        fields = ['image']





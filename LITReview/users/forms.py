from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import ProfileModel

class SigninForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(SigninForm, self).__init__(*args, **kwargs)

        for field_name in ['username', 'email', 'password1', 'password2']:
            self.fields[field_name].help_text = None

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': "Nom d'utilisateur"}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={"placeholder": "Mot de passe"}))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["style"] = "width: 80%;"
        self.fields["password"].widget.attrs["style"] = "width: 80%;"

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = ProfileModel
        fields = ['image']





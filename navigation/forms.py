from django import forms
from django.contrib.auth import forms as auth_forms

class RegistrationForm(auth_forms.UserCreationForm):
    email = forms.EmailField(max_length=75)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField()
    last_name = forms.CharField()

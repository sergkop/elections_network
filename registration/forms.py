# coding=utf8
from django import forms
from django.contrib.auth.models import User

class RegistrationForm(forms.Form):
    username = forms.RegexField(regex=r'^\w+$', max_length=30, widget=forms.TextInput(),
            error_messages={'invalid': "This value must contain only letters, numbers and underscores." })
    email = forms.EmailField(widget=forms.TextInput(maxlength=75))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False))
    
    def clean_username(self):
        """ Validate that the username is alphanumeric and is not already in use """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError("A user with that username already exists.")

    def clean_email(self):
        """ Validate that the supplied email address is unique for the site """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError("This email address is already in use. Please supply a different email address.")
        return self.cleaned_data['email']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single field.
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two password fields didn't match.")
        return self.cleaned_data

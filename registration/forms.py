# coding=utf8
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# TODO: login regex=r'^[\w.@+-]+$'
class RegistrationForm(UserCreationForm):
    username = forms.RegexField(max_length=30, min_length=4, regex=r'^\w+$',
            error_messages={'invalid': "This value must contain only letters, numbers and underscores."})
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField()
    last_name = forms.CharField()

    def clean_username(self):
        try: 
            u = User.objects.get(username__iexact=self.cleaned_data['username'])
        # if username is unique - it's ok
        except User.DoesNotExist: 
            return self.cleaned_data['username']

        raise forms.ValidationError(u'Пользователь с этим именем уже зарегистрирован')

    def clean_email(self):
        try: 
            u = User.objects.get(email=self.cleaned_data['email'])
        except User.DoesNotExist: 
            return self.cleaned_data['email']

        raise forms.ValidationError(u'Пользователь с этим email уже зарегистрирован')
        
    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two password fields didn't match.")
        return self.cleaned_data

class CompleteRegistrationForm(forms.Form):
    username = forms.RegexField(max_length=30, min_length=4, required=True, regex=r'^[\w.@+-]+$')
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, required=False)
    first_name = forms.CharField()
    last_name = forms.CharField()

    def __init__(self, user_id, *args, **kwargs):
        super(CompleteRegistrationForm, self).__init__(*args, **kwargs)
        self.user_id = user_id

    def clean_username(self):
        if self.cleaned_data['username']:
            try: 
                u = User.objects.exclude(id=self.user_id).get(username=self.cleaned_data['username'])
            # if username is unique - it's ok
            except User.DoesNotExist: 
                u = None

            if u is not None:
                raise forms.ValidationError(u'Пользователь с этим именем уже зарегистрирован')
        return self.cleaned_data['username']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def clean_email(self):
        if self.cleaned_data['email']:
            try: 
                u = User.objects.exclude(id=self.user_id).get(email=self.cleaned_data['email'])
            # if email is unique - it's ok
            except User.DoesNotExist: 
                u = None

            if u is not None:
                print self.user_id, u
                raise forms.ValidationError(u'Пользователь с этим email уже зарегистрирован')
        return self.cleaned_data['email']



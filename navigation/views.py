from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from geography.models import LocationModel
from navigation.forms import RegistrationForm

def main(request):
    context = {
        'locations': list(LocationModel.objects.filter(parent_1=None).order_by('name')),
    }
    return render_to_response('main.html', context_instance=RequestContext(request, context))

# TODO: what happens on /login page? login.html is a duplicate for elements/login.html
def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('current_profile'))
    return auth_views.login(request, template_name='login.html')

def logout(request):
    next_page = reverse('main') if 'next' in request.REQUEST else None
    return auth_views.logout(request, next_page)

# TODO: add captcha
def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('current_profile'))

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = User.objects.create_user(username, form.cleaned_data['email'], password)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            user = auth.authenticate(username=username, password=password)

            assert user and user.is_authenticated()
            auth.login(request, user)

            return HttpResponseRedirect(user.get_absolute_url())

    else:
        form = RegistrationForm()

    return render_to_response('register.html',
            context_instance=RequestContext(request, {'form': form}))

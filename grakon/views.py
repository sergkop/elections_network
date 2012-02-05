from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from grakon.forms import ProfileForm
from locations.models import Location

class BaseProfile(object):
    template_name = 'users/profile.html'
    profile_view = None # 'my_profile' or 'edit_profile'

    def get_user(self):
        raise NotImplemented

    def get_context_data(self, **kwargs):
        ctx = super(BaseProfile, self).get_context_data(**kwargs)
        user = self.get_user()
        profile = user.get_profile()

        roles = {}
        for role in profile.roles.select_related('location'):
            roles[role.type] = {'user': profile, 'location': role.location}

        ctx.update({
            'profile_user': user,
            'profile': profile,
            'roles': roles,
            'locations': list(Location.objects.filter(parent_1=None).order_by('name')),
            'links': list(profile.links.all().select_related()),
            'contacts': list(profile.contacts.all()) if user.is_authenticated() else [],
            'have_in_contacts': list(profile.have_in_contacts.all()),
            'profile_view': self.profile_view,
        })
        return ctx

class Profile(BaseProfile, TemplateView):
    profile_view = 'my_profile'

    def get_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

profile = Profile.as_view()

class MyProfile(BaseProfile, TemplateView):
    profile_view = 'my_profile'

    def get_user(self):
        return self.request.user

my_profile = login_required(MyProfile.as_view())

class EditProfile(BaseProfile, UpdateView):
    form_class = ProfileForm
    profile_view = 'edit_profile'

    def get_user(self):
        return self.request.user

    def get_object(self):
        return self.request.user.get_profile()

    def get_success_url(self):
        return reverse('my_profile')

edit_profile = login_required(EditProfile.as_view())

# TODO: fix it
def password_change(request, **kwargs):
    if request.user.get_profile().is_loginza_user():
        return redirect('password_change_forbidden')
    return auth_views.password_change(request, **kwargs)

def logout(request):
    next_page = reverse('main') if 'next' in request.REQUEST else None
    return auth_views.logout(request, next_page)

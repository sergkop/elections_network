from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView

from locations.models import Location

class BaseProfile(TemplateView):
    template_name = 'users/profile.html'

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
        })
        return ctx

class Profile(BaseProfile):
    def get_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

profile = Profile.as_view()

class MyProfile(BaseProfile):
    def get_user(self):
        return self.request.user

my_profile = login_required(MyProfile.as_view())

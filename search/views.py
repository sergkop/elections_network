from django.db.models import Q
from django.views.generic.base import TemplateView

from grakon.models import Profile
from locations.models import Location
from locations.utils import get_roles_query, regions_list
from users.forms import RoleTypeForm
from users.models import Role, ROLE_CHOICES, ROLE_TYPES

class BaseSearchView(TemplateView):
    template_name = 'search/base.html'
    tab = '' # 'user_list', 'user_table' or 'map'

    def preprocess(self):
        loc_id = ''
        for name in ('uik', 'tik', 'region'):
            loc_id = self.request.GET.get(name, '')
            if loc_id:
                break

        try:
            loc_id = int(loc_id)
        except ValueError:
            self.location = None
        else:
            try:
                self.location = Location.objects.get(id=loc_id)
            except Location.DoesNotExist:
                self.location = None

        role_form = RoleTypeForm(self.request.GET)

        if role_form.is_valid():
            self.role_type = role_form.cleaned_data['type']
        else:
            self.role_type = ''

        return {
            'tab': self.tab,
            'locations': regions_list(),
            'location_path': str(self.location.path()) if self.location else '[]',
            'role_form': role_form,
            'role_name': ROLE_TYPES[self.role_type] if self.role_type else '',
            'name': 'search',
        }

# TODO: show only verified users
class ListSearchView(BaseSearchView):
    tab = 'user_list'

    def get_context_data(self, **kwargs):
        ctx = super(BaseSearchView, self).get_context_data(**kwargs)
        ctx.update(self.preprocess())

        query = get_roles_query(self.location)
        if self.role_type:
            query = query & Q(type=self.role_type)

        profile_ids = Role.objects.filter(query).values_list('user', flat=True)
        people = Profile.objects.filter(id__in=profile_ids) \
                .exclude(user__email='', user__is_active=False) \
                .only('username', 'show_name', 'first_name', 'last_name').order_by('username')

        result_count = len(people)

        # TODO: temporary limit until pagination is introduced
        people = people[:100]

        ctx.update({
            'people': people,
            'result_count': result_count,
        })
        return ctx

user_list = ListSearchView.as_view()

class TableSearchView(BaseSearchView):
    tab = 'user_table'

    def get_context_data(self, **kwargs):
        ctx = super(BaseSearchView, self).get_context_data(**kwargs)
        ctx.update(self.preprocess())
        return ctx

user_table = TableSearchView.as_view()

class MapSearchView(BaseSearchView):
    tab = 'map'

    def get_context_data(self, **kwargs):
        ctx = super(BaseSearchView, self).get_context_data(**kwargs)
        ctx.update(self.preprocess())

        ctx.update({
            'place': self.request.GET.get('place', '')
        })
        return ctx

map = MapSearchView.as_view()

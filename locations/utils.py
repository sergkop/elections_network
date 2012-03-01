# -*- coding:utf-8 -*-
from django.db.models import Q
from django.http import HttpResponse

from loginza.models import UserMap

from grakon.utils import cache_function
from locations.models import FOREIGN_TERRITORIES, Location
from users.models import Role, ROLE_TYPES, WebObserver

@cache_function('regions_list', 600)
def regions_list():
    regions = [('', u'Выбрать субъект РФ'), None, None, None] # reserve places for Moscow, St. Petersburg and foreign countries
    for location in Location.objects.filter(region=None).only('id', 'name').order_by('name'):
        if location.name == u'Москва':
            regions[1] = (location.id, location.name)
        elif location.name == u'Санкт-Петербург':
            regions[2] = (location.id, location.name)
        elif location.name == FOREIGN_TERRITORIES:
            regions[3] = (location.id, location.name)
        else:
            regions.append((location.id, location.name))

    return regions

def get_roles_query(location):
    """ location = None for Russia """
    voter_count = 0
    if not location:
        query = Q()
    elif location.is_region():
        query = Q(location__region=location)
    elif location.is_tik():
        query = Q(location__tik=location) | Q(location=location)
    elif location.is_uik():
        query = Q(location=location)

    return query

# TODO: cache it, at least for the main page
# TODO: count members differently?
def get_roles_counters(location):
    counters = {}
    query = get_roles_query(location)
    for role in ROLE_TYPES:
        counters[role] = Role.objects.filter(Q(type=role) & query).count()

    counters['web_observer'] = len(WebObserver.objects.filter(query).distinct().values_list('user', flat=True))

    return counters

@cache_function('regions_counters', 15)
def get_region_counters():
    location_region = {}
    for loc_id, region in Location.objects.values_list('id', 'region'):
        location_region[loc_id] = region

    counters = {}
    for loc_id, role_type in Role.objects.values_list('location', 'type'):
        c = counters.setdefault(location_region[loc_id], {})
        c[role_type] = c.get(role_type, 0) + 1

    return counters

def get_locations_data(queryset, level):
    """ level=2,3,4 """
    js = 'var electionCommissions = { '
    data = []

    # get all locations from higher levels as well
    if level == 2:
        queryset = queryset.filter(region=None)
    elif level == 3:
        queryset = queryset.filter(tik=None)

    # TODO: limit locations number according to the level (don't get uiks for the whole country at once)
    locations = list(queryset.only('id', 'x_coord', 'y_coord', 'region', 'tik', 'name', 'address'))

    #region_ids = [loc.id for loc in locations if loc.is_region()]
    tik_ids = [loc.id for loc in locations if loc.is_tik()]
    uik_ids = [loc.id for loc in locations if loc.is_uik()]

    # TODO: уровень 3: delta_x=20, delta_y=10 уровень 4: 1,8 и 0,9

    if level >= 3:
        inactive_ids = UserMap.objects.filter(verified=False).values_list('user', flat=True)
        roles = list(Role.objects.exclude(user__user__email='', user__user__is_active=False,
                user__in=inactive_ids).filter(location__tik__in=tik_ids).values_list('type', 'location'))
        all_locations = list(Location.objects.filter(tik__in=tik_ids).values_list('id', 'tik'))

        locations_by_tik = {}
        for id, tik in all_locations:
            locations_by_tik.setdefault(tik, []).append(id)

    region_counters = get_region_counters()

    # {loc_id: [related_locations]}
    user_counts = {}
    for location in locations:
        if location.is_region():
            user_counts[location.id] = region_counters.get(location.id, {})
            continue

        related_locations = [location.id]
        if location.is_tik():
            related_locations += locations_by_tik[location.id]

        location_roles = filter(lambda role: role[1] in related_locations, roles)
        user_counts[location.id] = {}
        for role_type, loc_id in location_roles:
            user_counts[location.id][role_type] = user_counts[location.id].get(role_type) + 1

    for location in locations:
        if location.x_coord:
            js += str(location.id) + ': ' + location.map_data(user_counts[location.id]) + ','

    js = js[:-1] + '};'

    return HttpResponse(js, mimetype='application/javascript')

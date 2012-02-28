# -*- coding:utf-8 -*-
from django.db.models import Q
from django.http import HttpResponse

from loginza.models import UserMap

from grakon.utils import cache_function
from locations.models import FOREIGN_TERRITORIES, Location
from users.models import Role, ROLE_TYPES

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

    # Get ids of all locations that need to be taken into account for statistics
    all_ids = [loc.id for loc in locations]

    # Add all locations in regions
    region_ids = [loc.id for loc in locations if loc.is_region()]
    all_ids += Location.objects.filter(region__in=region_ids).values_list('id', flat=True)

    # Add all locations in tiks
    if level >= 3:
        tik_ids = [loc.id for loc in locations if loc.is_tik()]
        all_ids += Location.objects.filter(tik__in=tik_ids).values_list('id', flat=True)

    # Remove duplicate ids
    all_ids = set(all_ids)

    inactive_ids = UserMap.objects.filter(verified=False).values_list('user', flat=True)
    roles = Role.objects.exclude(user__user__email='', user__user__is_active=False,
            user__in=inactive_ids).filter(location__in=all_ids).values_list('type', 'location')
    all_locations = Location.objects.filter(id__in=all_ids).values_list('id', 'region', 'tik')

    # {loc_id: [related_locations]}
    user_counts = {}
    for location in locations:
        related_locations = [location.id]

        if location.is_region():
            related_locations += [id for id, region, tik in all_locations if region==location.id]
        elif location.is_tik():
            related_locations += [id for id, region, tik in all_locations if tik==location.id]

        user_counts[location.id] = {}
        location_roles = filter(lambda role_type, location: location in related_locations, roles)
        for role_type, location in location_roles:
            user_counts[location.id].setdefault(role_type, 0)
            user_counts[location.id].role_type += 1

    print user_counts

    for location in locations:
        if location.x_coord:
            js += str(location.id) + ': ' + location.map_data() + ','

    js = js[:-1] + '};'

    return HttpResponse(js, mimetype='application/javascript')

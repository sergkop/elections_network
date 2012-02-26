# -*- coding:utf-8 -*-
from django.db.models import Q
from django.http import HttpResponse

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

def get_locations_data(queryset):
    js = 'var electionCommissions = { '
    data = []
    for location in queryset.only('id', 'x_coord', 'y_coord', 'region', 'tik', 'name', 'address'):
        if location.x_coord:
            js += str(location.id) + ': ' + location.map_data() + ','

    js = js[:-1] + '};'

    return HttpResponse(js, mimetype='application/javascript')

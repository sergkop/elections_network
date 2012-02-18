# -*- coding:utf-8 -*-
from django.db.models import Q

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

# TODO: cache it, at least for the main page
def get_roles_counters(location):
    """ location = None for Russia """
    voter_count = 0
    if not location:
        query = Q()
    elif location.is_region():
        query = Q(location__region=location)
    elif location.is_tik():
        query = Q(location__tik=location)
    elif location.is_uik():
        query = Q(location=location)

    counters = {}
    for role in ROLE_TYPES:
        counters[role] = Role.objects.filter(Q(type=role) & query).count()

    return counters

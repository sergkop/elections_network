# -*- coding:utf-8 -*-
from grakon.utils import cache_function
from locations.models import FOREIGN_TERRITORIES, Location

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

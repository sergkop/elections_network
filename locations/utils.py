# -*- coding:utf-8 -*-
from locations.models import FOREIGN_TERRITORIES, Location

# TODO: cache the result
def regions_list():
    regions = [('', u'Выбрать субъект РФ'), None, None, None] # reserve places for Moscow, St. Petersburg and foreign countries
    for location in Location.objects.filter(region=None).order_by('name'):
        if location.name == u'Москва':
            regions[1] = (location.id, location.name)
        elif location.name == u'Санкт-Петербург':
            regions[2] = (location.id, location.name)
        elif location.name == FOREIGN_TERRITORIES:
            regions[3] = (location.id, location.name)
        else:
            regions.append((location.id, location.name))

    return regions

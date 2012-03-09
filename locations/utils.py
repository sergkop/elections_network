# -*- coding:utf-8 -*-
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponse

from loginza.models import UserMap

from grakon.models import Profile
from grakon.utils import cache_function
from links.models import Link
from locations.models import FOREIGN_TERRITORIES, Location
from organizations.models import Organization, OrganizationCoverage
from protocols.models import Protocol
from users.models import CommissionMember, Role, ROLE_TYPES, WebObserver
from violations.models import Violation

def cache_location_function(key_prefix, timeout, timeout_region=None, timeout_tik=None, timeout_uik=None):
    """ Takes function of one argument (location with default value None) """
    def decorator(func):
        def new_func(location=None):
            if location:
                key = key_prefix + '_' + str(location.id)
            else:
                key = key_prefix + '_all'

            res = cache.get(key)
            if res:
                return res

            res = func(location)

            # Determine timeout
            if location is None:
                timeout1 = timeout
            elif location.is_region():
                timeout1 = timeout_region or timeout
            elif location.is_tik():
                timeout1 = timeout_tik or timeout
            elif location.is_uik():
                timeout1 = timeout_uik or timeout

            cache.set(key, res, timeout1)
            return res

        return new_func

    return decorator

@cache_location_function('regions_list', 1000)
def regions_list(location=None):
    """ location = None for Russia """
    if location is None:
        regions = [('', u'Выбрать субъект РФ'), None, None, None] # reserve places for Moscow, St. Petersburg and foreign countries
        for loc_id, name in Location.objects.filter(region=None).order_by('name').values_list('id', 'name'):
            if name == u'Москва':
                regions[1] = (loc_id, name)
            elif name == u'Санкт-Петербург':
                regions[2] = (loc_id, name)
            elif name == FOREIGN_TERRITORIES:
                regions[3] = (loc_id, name)
            else:
                regions.append((loc_id, name))
        return regions
    elif location.is_region():
        return list(Location.objects.filter(region=location, tik=None).order_by('name').values_list('id', 'name'))
    elif location.is_tik():
        return list(Location.objects.filter(tik=location).order_by('name').values_list('id', 'name'))
    else:
        return []

# TODO: introduce query generators for other types of counting
def get_roles_query(location=None):
    if location is None:
        return Q()

    query = Q(location=location)
    if location.is_region():
        query |= Q(location__region=location)
    elif location.is_tik():
        query |= Q(location__tik=location)

    return query

# TODO: count members differently?
@cache_location_function('roles_counter', 300)
def get_roles_counters(location=None):
    counters = {}
    query = get_roles_query(location)

    inactive_ids = UserMap.objects.filter(verified=False).values_list('user', flat=True)

    def filter_inactive_users(queryset):
        return queryset.exclude(user__user__email='', user__user__id__in=inactive_ids).filter(user__user__is_active=True)

    roles = list(filter_inactive_users(Role.objects.filter(query)).values_list('type', 'user'))

    for role_type in ROLE_TYPES:
        counters[role_type] = len(filter(lambda r: r[0]==role_type, roles))

    # TODO: do it for location=None only?
    counters['total'] = Profile.objects.exclude(user__email='').exclude(id__in=inactive_ids).filter(user__is_active=True).count()

    # TODO: use count here?
    counters['web_observer'] = len(filter_inactive_users(WebObserver.objects.filter(query)) \
            .distinct().values_list('user', flat=True))

    counters['violations'] = Violation.objects.filter(query).count()

    counters['uiks'] = Protocol.objects.cik_protocols().filter(query).exclude(location__tik=None).count()

    protocol_queryset = Protocol.objects.from_users().filter(query).exclude(location__tik=None)
    counters['protocols'] = protocol_queryset.count()
    counters['verified_protocols'] = protocol_queryset.filter(verified=True).count()

    counters['commission_members'] = CommissionMember.objects.filter(query).count()

    if location:
        counters['links'] = Link.objects.filter(location=location).count()

    # TODO: use count instead
    counters['organizations'] = len(OrganizationCoverage.objects.organizations_at_location(location))

    return counters

@cache_function('regions_counters', 1000)
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
        #inactive_ids = UserMap.objects.filter(verified=False).values_list('user', flat=True)
        #roles = list(Role.objects.exclude(user__user__email='', user__user__is_active=False,
        #        user__in=inactive_ids).filter(location__tik__in=tik_ids).values_list('type', 'location'))
        #all_locations = list(Location.objects.filter(tik__in=tik_ids).values_list('id', 'tik'))

        locations_by_tik = {}
        #for id, tik in all_locations:
        #    locations_by_tik.setdefault(tik, []).append(id)

    region_counters = get_region_counters()

    # {loc_id: [related_locations]}
    user_counts = {}
    for location in locations:
        if location.is_region():
            user_counts[location.id] = region_counters.get(location.id, {})
            continue

        # TODO: temporary blocked due to performance issues
        user_counts[location.id] = {}
        continue

        #related_locations = [location.id]
        #if location.is_tik():
        #    related_locations += locations_by_tik[location.id]

        #location_roles = filter(lambda role: role[1] in related_locations, roles)
        #user_counts[location.id] = {}
        #for role_type, loc_id in location_roles:
        #    user_counts[location.id][role_type] = user_counts[location.id].get(role_type, 0) + 1

    for location in locations:
        if location.x_coord:
            js += str(location.id) + ': ' + location.map_data(user_counts[location.id]) + ','

    js = js[:-1] + '};'

    return HttpResponse(js, mimetype='application/javascript')

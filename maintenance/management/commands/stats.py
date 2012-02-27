from datetime import datetime

from django.core.management.base import BaseCommand

def stats_for_type(role_type):
    from users.models import Role
    roles = Role.objects.filter(type=role_type).exclude(user__user__email='', user__user__is_active=False)
    times = roles.values_list('time', flat=True)

    min_time = min(times)
    min_time = datetime(min_time.year, min_time.month, min_time.day, min_time.hour)
    print "min time", min_time
    print "max time", max(times)

    counts = {}
    for time in times:
        block_time = datetime(time.year, time.month, time.day, time.hour)
        counts.setdefault(block_time, 0)
        counts[block_time] += 1

    for block_time in counts:
        print (block_time-min_time).days, (block_time-min_time).seconds/3600, counts[block_time]

class Command(BaseCommand):
    help = "Provide registration statistics."

    def handle(self, *args, **options):
        stats_for_type('voter')
        stats_for_type('observer')
        stats_for_type('member')

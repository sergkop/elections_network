# -*- coding:utf-8 -*-
from django.db import models

# Url templates for pages on izbirkom.ru with information about comissions
RESULTS_ROOT_URL = r'http://www.%(region_name)s.vybory.izbirkom.ru/region/%(region_name)s?action=show&global=1&vrn=100100031793505&region=%(region_code)d&prver=0&pronetvd=null'
RESULTS_URL = r'http://www.%(region_name)s.vybory.izbirkom.ru/region/%(region_name)s?action=show&global=true&root=%(root)d&tvd=%(tvd)d&vrn=100100031793505&prver=0&pronetvd=null&region=%(region_code)d&sub_region=%(region_code)d&type=0&vibid=%(tvd)d'

#INFO_ROOT_URL = r'http://www.%(region_name)s.vybory.izbirkom.ru/region/%(region_name)s?action=show_komissia&region=%(region_code)d&sub_region=%(region_code)d&type=100&vrnorg=0&vrnkomis=0'
INFO_URL = r'http://www.%(region_name)s.vybory.izbirkom.ru/region/%(region_name)s?action=show_komissia&region=%(region_code)d&sub_region=%(region_code)d&type=100&vrnorg=%(vrnorg)d&vrnkomis=%(vrnkomis)d'

FOREIGN_TERRITORIES = u'Зарубежные территории' # Do not change this name without proper changes in production db and 
FOREIGN_NAME = 'foreign'
FOREIGN_CODE = 100

class Location(models.Model):
    """ The number of non-null values of parent specifies the level of location """
    # keys to the parents of the corresponding level (if present)
    region = models.ForeignKey('self', null=True, blank=True, related_name='in_region')
    tik = models.ForeignKey('self', null=True, blank=True, related_name='in_tik')

    name = models.CharField(max_length=150)
    region_name = models.CharField(max_length=20)
    region_code = models.IntegerField()

    postcode = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=40, blank=True)

    # Ids required to access data from izbirkom.ru
    tvd = models.IntegerField()
    root = models.IntegerField()
    vrnorg = models.IntegerField(blank=True, null=True)
    vrnkomis = models.IntegerField(blank=True, null=True)

    # Coordinates used in Yandex maps
    x_coord = models.FloatField(blank=True, null=True)
    y_coord = models.FloatField(blank=True, null=True)

    def level(self):
        if self.region_id is None:
            return 2
        elif self.tik_id is None:
            return 3
        else:
            return 4

    def is_region(self):
        return self.region_id is None and self.tik_id is None

    def is_tik(self):
        return self.region_id is not None and self.tik_id is None

    def is_uik(self):
        return self.region_id is not None and self.tik_id is not None

    def is_foreign(self):
        return self.region_name==FOREIGN_NAME

    def results_url(self):
        """ Link to the page with elections results on izbirkom.ru """
        data = {'region_name': self.region_name, 'region_code': self.region_code}
        if self.tvd != 0:
            data.update({'tvd': self.tvd, 'root': self.root})
            return RESULTS_URL % data
        else:
            return RESULTS_ROOT_URL % data

    def info_url(self):
        """ Link to the page with comission information on izbirkom.ru """
        if self.vrnorg is None:
            return ''

        return INFO_URL % {'region_name': self.region_name, 'region_code': self.region_code,
                'vrnorg': self.vrnorg, 'vrnkomis': self.vrnkomis}

    def __unicode__(self, full_path=False):
        name = self.name
        if full_path:
            if self.tik:
                name = str(self.tik) + u'->' + name
            if self.region:
                name = str(self.region) + u'->' + name
        return name

    @models.permalink
    def get_absolute_url(self):
        return ('location_info', (), {'loc_id': str(self.id)})

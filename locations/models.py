from django.db import models

class Location(models.Model):
    """ The number of non-null values of parent specifies the level of location """
    # keys to the parents of the corresponding level (if present)
    region = models.ForeignKey('self', null=True, blank=True, related_name='same_region_locations')
    tik = models.ForeignKey('self', null=True, blank=True, related_name='same_tik_locations')

    # TODO: how about region and it's code?
    name = models.CharField(max_length=150)

    postcode = models.IntegerField()
    address = models.CharField(max_length=200)
    telephone = models.CharField(max_length=50)
    email = models.CharField(max_length=40)

    # Ids required to access data from izbirkom.ru
    tvd = models.IntegerField()
    root = models.IntegerField()
    vrnorg = models.IntegerField()
    vrnkomis = models.IntegerField()

    # Coordinates used in Yandex maps
    x_coord = models.FloatField()
    y_coord = models.FloatField()

    # TODO: make name unique?
    class Meta:
        unique_together = ('name', 'region', 'tik')

    #def level(self):
    #    # TODO: UIK, TIK or IKS
    #    if self.parent_1:
    #        return 2
    #    else:
    #        return 1

    def __unicode__(self, full_path=False):
        name = self.name
        if full_path:
            if self.parent_2:
                name = str(self.parent_2) + u'->' + name
            if self.parent_1:
                name = str(self.parent_1) + u'->' + name
        return name

    @models.permalink
    def get_absolute_url(self):
        return ('location', [self.id])

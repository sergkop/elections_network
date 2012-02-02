from django.db import models

class Location(models.Model):
    """ The number of non-null values of parent specifies the level of location """
    # keys to the parents of the corresponding level (if present)
    parent_1 = models.ForeignKey('self', null=True, blank=True, related_name='parents_1')
    parent_2 = models.ForeignKey('self', null=True, blank=True, related_name='parents_2')
    parent_3 = models.ForeignKey('self', null=True, blank=True, related_name='parents_3')
    # TODO: we only need 2 parents

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
    # TODO: location level 

    # TODO: make name unique?
    class Meta:
        unique_together = ('name', 'parent_1', 'parent_2', 'parent_3')

    #def level(self):
    #    # TODO: UIK, TIK or IKS
    #    if self.parent_1:
    #        return 2
    #    else:
    #        return 1

    def __unicode__(self, full_path=False):
        name = self.name
        if full_path:
            if self.parent_3:
                name = str(self.parent_3) + u'->' + name
            if self.parent_2:
                name = str(self.parent_2) + u'->' + name
            if self.parent_1:
                name = str(self.parent_1) + u'->' + name
        return name

    @models.permalink
    def get_absolute_url(self):
        return ('location', [self.id])

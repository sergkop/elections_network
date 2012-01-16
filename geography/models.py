from django.db import models

class LocationModel(models.Model):
    """ The number of non-null values of parent specifies the level of location """
    name = models.CharField(max_length=150)
     # keys to the parents of the corresponding level (if present)
    parent_1 = models.ForeignKey('self', null=True, blank=True, related_name='parents_1')
    parent_2 = models.ForeignKey('self', null=True, blank=True, related_name='parents_2')

    def level(self):
        if self.parent_1:
            return 2
        else:
            return 1

    def __unicode__(self, full_path=False):
        if full_path:
            if self.parent_1:
                return str(self.parent_1) + u'->' + self.name
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('location', [self.id])

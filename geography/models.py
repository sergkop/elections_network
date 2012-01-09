from django.db import models

class LocationModel(models.Model):
    name = models.CharField(max_length=150)
    parent_1 = models.ForeignKey('self', null=True, blank=True) # key to the parent of the level 1 (if present)

    def level(self):
        if self.parent_1:
            return 2
        else:
            return 1

    def __unicode__(self):
        return self.name

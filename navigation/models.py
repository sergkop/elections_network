from django.db import models

from tinymce.models import HTMLField

class Page(models.Model):
    name = models.CharField(max_length=20)
    content = HTMLField()

    class Meta:
        unique_together = ('name',)

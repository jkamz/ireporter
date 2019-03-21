from django.db import models
from django.core.validators import URLValidator
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model


class RedflagModel(models.Model):
    """The incident model."""

    createdBy = models.CharField(max_length=30, null=True)
    incident_type = 'red-flag'
    title = models.CharField(max_length=128)
    location = models.CharField(max_length=150)
    status = models.CharField(max_length=30, default="draft")
    Image = ArrayField(models.TextField(max_length=1000,
                                        validators=[URLValidator]
                                        ),
                       blank=True, default=list)
    Video = models.URLField(blank=True, null=True)
    comment = models.TextField(blank=False, null=False)
    createdOn = models.DateTimeField(auto_now_add=True, editable=False)
    twitter = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    linkedIn= models.URLField(blank=True, null=True)
    mail = models.TextField(blank=False, null=False, default="")

    def __str__(self):
        return "{}".format(self.title)

    class Meta:
        ordering = ["-createdOn"]


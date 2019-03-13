from django.db import models
import uuid
from django.contrib.auth import get_user_model

class RedflagModel(models.Model):
    """The incident model."""

    createdBy = models.CharField(max_length=30, null=True)
    incident_type = 'red-flag'
    title = models.CharField(max_length=128)
    location = models.CharField(max_length=150)
    status = models.CharField(max_length=30)
    Image = models.URLField(blank=True, null=True)
    Video = models.URLField(blank=True, null=True)
    comment = models.TextField(blank=False, null=False)
    createdOn = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "{}".format(self.title)        

    class Meta:
        ordering = ["-createdOn"]

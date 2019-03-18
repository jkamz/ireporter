from django.db import models
import uuid
from django.contrib.auth import get_user_model


class InterventionsModel(models.Model):
    """
    The interventions model
    """

    createdBy = models.CharField(max_length=30, null=True)
    incident_type = 'intervention'
    title = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    status = models.CharField(max_length=30, default="draft")
    Image = models.CharField(max_length=500, default="", blank=True)
    Video = models.CharField(max_length=500, default="", blank=True)
    comment = models.TextField(blank=False, null=False)
    createdOn = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "{}".format(self.title)

    class Meta:
        ordering = ["-createdOn"]

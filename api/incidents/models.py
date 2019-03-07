from django.db import models
import uuid
from django.contrib.auth import get_user_model

<<<<<<< HEAD
=======
def generate_incident_id():
    """generate unique incidet id"""
    return str(uuid.uuid4()).split("-")[-1]
>>>>>>> 7008aff155fae1763163852dd4b353092276038d

class Incident(models.Model):
    """The incident model."""

<<<<<<< HEAD
    incident_id = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)
=======
    incident_id = models.CharField(max_length=255, blank=True)
>>>>>>> 7008aff155fae1763163852dd4b353092276038d
    createdBy = models.ForeignKey(
        get_user_model(),
        related_name='createdBy',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    incident_type = models.CharField(max_length=30)
    title = models.CharField(max_length=128)
    location = models.CharField(max_length=150)
    status = models.CharField(max_length=30)
    Image = models.URLField(blank=True, null=True)
    Video = models.URLField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    createdOn = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "{} - {}".format(self.title, self.incident_id)


    class Meta:
        ordering = ["-createdOn"]

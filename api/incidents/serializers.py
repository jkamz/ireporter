from rest_framework import serializers
from django.apps import apps
from django.contrib.auth import get_user_model
from .models import Incident

TABLE = apps.get_model('incidents', 'Incident')


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TABLE
        fields = ('incident_id', 'createdBy', 'incident_type','title', 'location','status', 'Image', 'Video', 'comment', 'createdOn')

    def create(self, validated_data):
        incident = TABLE.objects.create(**validated_data)
        return incident
        
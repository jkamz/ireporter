from rest_framework import serializers
from django.apps import apps
from django.contrib.auth import get_user_model
from .models import RedflagModel
from rest_framework.response import Response
from rest_framework import status

TABLE = apps.get_model('incidents', 'RedflagModel')


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TABLE
        fields = (
            'id',
            'url',
            'createdBy',
            'title',
            'incident_type',
            'location',
            'status',
            'Image',
            'Video',
            'comment',
            'createdOn')

    def create(self, validated_data):
        incident = TABLE.objects.create(**validated_data)
        return incident

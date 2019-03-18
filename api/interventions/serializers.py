from rest_framework import serializers
from django.apps import apps
from django.contrib.auth import get_user_model
from .models import InterventionsModel
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import JsonResponse
import re

TABLE = apps.get_model('interventions', 'InterventionsModel')


class InterventionSerializer(serializers.ModelSerializer):
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
        intervention = TABLE.objects.create(**validated_data)
        return intervention

    def validate(self, data):
        """
        checks if the user provides a valid lat and long coordinates,
        Valid comment that does not have only special characters and
        a valid title that does not have only special characters
        """

        if not re.match(
                r"^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$", data['location']):

            raise serializers.ValidationError({
                "message": "Please user a valid lat and long "
                "coordinates separated by comma"

                })

        if re.match(
                r"^[!@#$%^&*()_-]+$", data['title']):

            raise serializers.ValidationError({
                "message": "A title cannot contain only special chars"

                })

        if re.match(
                r"^[!@#$%^&*()_-]+$", data['comment']):

            raise serializers.ValidationError({
                "message": "A comment cannot contain only special chars"

                })

        return data

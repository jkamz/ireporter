from django.shortcuts import render
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.response import Response
from .serializers import IncidentSerializer, TABLE
from django.contrib.auth.models import User
from .models import Incident
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
)

class CreateIncidentView(viewsets.ModelViewSet):
    """
    post:
    Create Incident.

    get:
    Get Incident.

    delete:
    Delete Incident.
    """

    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

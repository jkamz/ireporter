from django.shortcuts import render
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from .serializers import IncidentSerializer, TABLE
from django.contrib.auth.models import User
from .models import Incident
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
)

# Create your views here.

class CreateRedflagAPIView(generics.CreateAPIView):
    """
    post:
    Create Redflag.
    """

    serializer_class = IncidentSerializer
    permission_classes = [AllowAny]
    queryset = TABLE.objects.all()

    def perform_create(self, serializer):
        """Create article."""
        serializer.save()
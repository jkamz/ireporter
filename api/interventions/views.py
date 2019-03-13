from django.shortcuts import render
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.response import Response
from .serializers import InterventionSerializer, TABLE
from django.contrib.auth.models import User
from .models import InterventionsModel
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
)
from django.http import JsonResponse


class InterventionsView(viewsets.ModelViewSet):
    """
    post:
    Create an Intervention Record.

    get:
    Get an Intervention Record

    delete:
    Delete an Intervention Record

    patch:
    Update an Intervention Record
    """

    queryset = InterventionsModel.objects.all()
    serializer_class = InterventionSerializer
    permission_classes = [IsAuthenticated]

    def validate_record(self, request):
        """check for duplicate records by same user"""

        records = InterventionsModel.objects.filter(
            createdBy=request.data['createdBy'])
        duplicate_title = records.filter(
            title=request.data['title'])
        duplicate_comment = records.filter(
            comment=request.data['comment'])
        if duplicate_title.exists():
            return JsonResponse(
                {"status": 409,
                 "message": "This Intervention record title exists"},
                status=409)
        elif duplicate_comment.exists():
            return JsonResponse(
                {"status": 409,
                 "message": "This Intervention record comment exists"},
                status=409)
        else:
            return self.create_intervention(request)

    def create_intervention(self, request):
        response = super().create(request)
        response.data = {
            'status': 201,
            'data': response.data,
        }
        return response

    def create(self, request):
        request.data['createdBy'] = request.user.id
        return self.validate_record(request)

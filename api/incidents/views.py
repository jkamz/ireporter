from django.shortcuts import render
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.response import Response
from .serializers import IncidentSerializer, TABLE
from django.contrib.auth.models import User
from .models import RedflagModel
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
)
from django.http import JsonResponse

from django.http.response import Http404


class RedflagView(viewsets.ModelViewSet):
    """
    post:
    Create redflag.

    get:
    Get redflag.

    delete:
    Delete redflag.

    patch:
    Update redflag.
    """

    queryset = RedflagModel.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]

    def validate_record(self, request):
        records = RedflagModel.objects.filter(
            createdBy=request.data['createdBy'])
        duplicate_record = records.filter(
            title=request.data['title']).filter(
            comment=request.data['comment'])
        if duplicate_record.exists():
            return JsonResponse(
                {"status": 409,
                 "message": "record exists"},
                status=409)
        else:
            return self.create_redflag_record(request)

    def create_redflag_record(self, request):
        response = super().create(request)
        response.data = {
            'status': 201,
            'data': response.data,
        }
        return response

    def create(self, request):
        request.data['createdBy'] = request.user.id
        return self.validate_record(request)

    def destroy(self, request, **kwargs):

        user_id, response = request.user.id, {}

        try:
            instance = self.get_object()

            if int(instance.createdBy) != user_id:

                response['status'], response['error'] = 403, 'You can not delete a redflag you do not own'

            else:
                self.perform_destroy(instance)

                response['status'], response['message'] = 200, 'Redflag record successfully deleted'

        except Http404:

            response['status'], response['error'] = 404, 'Redflag record could not be found'

        return Response(data=response, status=response['status'])
        

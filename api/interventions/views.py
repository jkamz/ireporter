from django.shortcuts import render
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import (
    InterventionSerializer, TABLE, AdminInterventionSerializer

)
from django.contrib.auth.models import User
from users.models import User
from .models import InterventionsModel
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny

)
from django.http import JsonResponse
from django.http.response import Http404
import smtplib
from django.conf import settings
from incidents.views import send_email
record_type = "Intervention"
from file_utility.uploader import ImageUploader
from django.contrib.postgres.fields import ArrayField
import json


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
            return self.upload_image(request)

    def create(self, request):
        request.POST._mutable = True
        request.data['createdBy'] = request.user.id
        return self.validate_record(request)

    def user_name(self, uid):
        user = User.objects.filter(id=uid)[0]
        return user.username

    def list(self, request):
        """
        get:
        Get all interventions.
        """
        queryset = self.queryset
        serializer = InterventionSerializer(queryset, many=True,
                                            context={'request': request})
        dictionary = None
        data = []
        for redflag in serializer.data:
            dictionary = dict(redflag)
            dictionary['createdBy'] = self.user_name(dictionary['createdBy'])
            data.append(dictionary)

        return JsonResponse({"status": 200,
                             "data": data},
                            status=200)

    def retrieve(self, request, pk=None):
        """
        get:
        Get an intervention.
        """
        try:
            intervention = InterventionsModel.objects.filter(id=pk)[0]
        except:
            return JsonResponse({"status": 404,
                                 "message": "Intervention with id {} not found".format(pk)},
                                status=404)
        intervention.createdBy = self.user_name(intervention.createdBy)
        serializer = InterventionSerializer(intervention,
                                            context={'request': request})
        return JsonResponse({"status": 200,
                             "data": serializer.data},
                            status=200)


    @action(methods=['patch'], detail=True, permission_classes=[IsAdminUser],
            url_path='status', url_name='change_status')
    def update_status(self, request, pk=None):
        """
        patch:
        Update an Intervention Status
        """

        response, data, options = (
            {}, {}, ['draft', 'under investigation', 'resolved', 'rejected',
                     'Draft', 'Under Investigation', 'Resolved', 'Rejected']
        )

        try:
            intervention = self.get_object()

            try:
                status_data = request.data['status'].strip()

                if status_data in options:

                    data['status'] = status_data.lower()

                    updated_intervention = (
                        AdminInterventionSerializer(intervention,
                                                    data=data,
                                                    partial=True,
                                                    context={
                                                        'request': request}
                                                    )
                    )

                    updated_intervention.is_valid(raise_exception=True)

                    self.perform_update(updated_intervention)

                    response_data = updated_intervention.data

                    response_data['createdBy'] = self.user_name(
                        updated_intervention.data['createdBy'])

                    send_email(response_data['createdBy'],
                               status_data, response_data,
                               updated_intervention,
                               response, record_type
                               )

                else:

                    response['error'], response['status'] = (
                        "'status' field may only be either {}".format(
                            ' or '.join(options[:4])), 400)

            except KeyError:

                response['error'], response['status'] = {
                    "status": "This field is required."}, 400

        except Http404:

            response['error'], response['status'] = (
                "Intervention record with ID '{}' does not exist".format(
                    pk), 404)

        return Response(data=response, status=response['status'])

    def destroy(self, request, **kwargs):
        """
        This methods tries to delete an intevention
        when the user owns it, also, return error message
        when status is changed or user doesn't own it
        """

        user_id, response = request.user.id, {}

        try:
            instance = self.get_object()

            if int(instance.createdBy) != user_id:

                response['status'], response['error'] = 403, \
                    'You can not delete an intervention record you do not own'

            elif str.lower(instance.status) != str.lower('draft'):
                response['status'], response['error'] = 403, \
                    'You can not delete this intervention, it is already '\
                    + instance.status

            else:
                self.perform_destroy(instance)

                response['status'], response['message'] = 200, \
                    'Intervention record successfully deleted'

        except Http404:

            response['status'], response['error'] = 404, \
                'Intervention record could not be found'

        return Response(data=response, status=response['status'])

    def update(self, request, pk=None, *args, **kwargs):
        """
        put:
        user edit an intervention
        """

        request.POST._mutable = True
        try:
            intervention = InterventionsModel.objects.filter(id=pk)[0]
        except:
            return JsonResponse(
                {"status": 404,
                 "message": "Intervention with id {} not found".format(pk)},
                status=404)
        serializer = InterventionSerializer(intervention,
                                            context={'request': request})

        if int(request.user.id) != int(serializer.data['createdBy']):
            return JsonResponse(
                {"status": 403,
                 "message": "You cannot edit an intervention you do not own"},
                status=403)
        request.data['createdBy'] = serializer.data['createdBy']

        if intervention.status.lower() == 'draft':
            request.data['id'] = intervention.id
            return self.upload_image(request)

        return JsonResponse(
            {"status": 403,
             "message":
             ("You cannot edit the intervention since its "
              "status is: {}".format(intervention.status))},
            status=403)

    def upload_image(self, request, pk=None, *args, **kwargs):
        
        file_exists = request.FILES.get('file', False)
        id_exists = request.data.get('id', False)

        status = 0
        if request.method == 'POST':
            status = 201
        else:
            status = 200

        try:
            if id_exists:
                try:
                    intervention = InterventionsModel.objects.filter(id=int(request.data['id']))[0]
                    if file_exists:
                        if request.FILES['file'] is not None:
                            image = ImageUploader(request.FILES['file'])
                            if image is not None:
                                uploaded_image_url = image.get('secure_url', request.FILES['file'])
                                saved_images = intervention.Image
                                serializer = InterventionSerializer(intervention,
                                                    data=request.data,
                                                    context={'request': request})
                                serializer.is_valid(raise_exception=True)
                                saved_images.append(uploaded_image_url)
                                serializer.validated_data['Image'] = saved_images
                                serializer.save()
                                return Response({"status" : status,
                                    "data": serializer.data},
                                    status=status)
                            else:
                                serializer = InterventionSerializer(intervention,
                                                    data=request.data,
                                                    context={'request': request})
                                serializer.is_valid(raise_exception=True)
                                serializer.save()
                                return Response({"status" : status,
                                    "data": serializer.data},
                                    status=status)
                    else:
                        serializer = InterventionSerializer(intervention,
                                                    data=request.data,
                                                    context={'request': request})
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        return Response({"status" : status,
                            "data": serializer.data},
                            status=status)
                except Http404:
                    return JsonResponse({"status": 404,
                                    "message": "Intervention with id {} not found".format(request.data['id'])},
                                    status=404)

            else:
                if file_exists:
                        response = super().create(request)
                        request.data['id'] = response.data['id']
                        return self.upload_image(request)
                else:
                    response = super().create(request)
                    response.data = {
                        'status': status,
                        'data': response.data,
                    }
                    return response
        except Exception as e:
            return JsonResponse(
                {"status" : e.status_code,
                    "error": e.__dict__},
                status = e.status_code,
                safe = False)

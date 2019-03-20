from django.shortcuts import render
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from .serializers import IncidentSerializer, TABLE, AdminRedflagSerializer
from django.contrib.auth.models import User
from users.models import User
from .models import RedflagModel
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
)
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
import json

from django.http.response import Http404
import smtplib
from django.conf import settings

record_type = "Red-Flag"


def send_email(creator_name, new_status, response_data, updated_redflag, response, record_type):
    """
    This tries to send an email to the owner
    of an intervention record when admin changes the status
    """
    response_data['createdBy'] = RedflagView.user_name(uid=updated_redflag.data['createdBy'])

    creator_email = RedflagView.user_email(
        updated_redflag.data['createdBy'])

    FROM = settings.EMAIL_HOST_USER
    TO = [creator_email]
    SUBJECT = "iReporter {} Record Status change".format(record_type)
    MESSAGE = ("Hello {},\n\nYour {} record is "
                "now {}\n\nThank you for using our services.\n"
                "\nThe Ireporter Team"
                .format(creator_name, record_type, new_status))

    try:
        server = smtplib.SMTP(
            settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(
            FROM, settings.EMAIL_HOST_PASSWORD)
        msg = """From: %s\nTo: %s\nSubject: %s\n\n%s
                """ % (FROM, ", ".join(TO), SUBJECT, MESSAGE)
        server.sendmail(FROM, TO, msg)
        server.quit()

    except:
        response_data['message'] = (
            "status set to {}; could not send email to the "
            "user".format(new_status))

        response['data'], response['status'] = response_data, 200

        return Response(data=response, status=response['status'])

    response['data'], response['status'] = response_data, 200


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

    def upload_image(self, request):
        """
        Uploads an image
        """

        image, file_storage = (
            request.FILES['image'],
            FileSystemStorage()
        )

        file_name = file_storage.save(image.name, image)

        uploaded_image_url = file_storage.url(file_name)

        return uploaded_image_url

    def validate_record(self, request):
        """Checks if redlag record exists """

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
            if 'image' in request.FILES.keys():

                image = request.FILES['image'].name.lower()

                if not (image.endswith(".jpg") or image.endswith(".png")):

                    return Response(data={
                        "error": "Ensure the file is in JPEG or PNG format",
                        "status": 400}, status=status.HTTP_400_BAD_REQUEST)

                image_url = self.upload_image(request)

                if "media" not in image_url:

                    return Response(data={
                        "error": "Service unavailable. \
                        Please try again later.",
                        "status": 503
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

                request.data['Image'] = image_url

            return self.create_redflag_record(request)

    def create_redflag_record(self, request):
        response = super().create(request)
        response.data = {
            'status': 201,
            'data': response.data,
        }
        return response

    def create(self, request):
        request.POST._mutable = True
        request.data['createdBy'] = request.user.id
        return self.validate_record(request)

    def destroy(self, request, **kwargs):

        user_id, response = request.user.id, {}

        try:
            instance = self.get_object()

            if not 'draft' in instance.status.lower():

                response['status'], response['error'] = 403, 'This record is {}. You can not delete it.'.format(
                    instance.status.lower())

            elif int(instance.createdBy) != user_id:

                response['status'], response['error'] = 403, 'You can not delete a redflag you do not own'

            else:
                self.perform_destroy(instance)

                response['status'], response['message'] = 200, 'Redflag record successfully deleted'

        except Http404:

            response['status'], response['error'] = 404, 'Redflag record could not be found'

        return Response(data=response, status=response['status'])

    @staticmethod
    def user_name(uid):
        user = User.objects.filter(id=uid)[0]
        return user.username

    def list(self, request):
        """
        get:
        Get all redflags.
        """
        page_limit = request.GET.get('limit')

        if not page_limit or not page_limit.isdigit():
            page_limit = 10

        queryset = self.queryset
        paginator = PageNumberPagination()
        paginator.page_size = page_limit
        
        page = paginator.paginate_queryset(queryset, request)
        serializer = IncidentSerializer(page, many=True,
                                        context={'request': request})
        dictionary = None
        data = []
        for redflag in serializer.data:
            dictionary = dict(redflag)
            dictionary['createdBy'] = RedflagView.user_name(dictionary['createdBy'])
            data.append(dictionary)

        return paginator.get_paginated_response(data=data)


    def retrieve(self, request, pk=None):
        """
        get:
        Get a redflag.
        """
        try:
            redflag = RedflagModel.objects.filter(id=pk)[0]
        except:
            return JsonResponse({"status": 404,
                                 "message": "Redflag with id {} not found".format(pk)},
                                status=404)
        redflag.createdBy = self.user_name(redflag.createdBy)
        serializer = IncidentSerializer(redflag,
                                        context={'request': request})
        return JsonResponse({"status": 200,
                             "data": serializer.data},
                            status=200)

    def update(self, request, **kwargs):
        """
        update:
        update a redflag.
        """
        try:
            instance = self.get_object()

            if int(instance.createdBy) != request.user.id:
                return JsonResponse({"status": 403,
                                     "message": "You can not update a redflag you do not own"},
                                    status=403)

            if instance.status.lower() != 'draft':
                return JsonResponse({"status": 403,
                                     "message": "You can not update a redflag that is not a draft"},
                                    status=403)

            request.data['createdBy'] = request.user.id
            request.data['status'] = instance.status
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)

        except Http404:
            return JsonResponse({"status": 404,
                                 "message": "Redflag not found"},
                                status=404)

    @action(methods=['patch'], detail=True, permission_classes=[IsAdminUser],
            url_path='status', url_name='change_status')
    def update_status(self, request, pk=None):
        """
        patch:
        Update a redflag Status
        """

        response, data, options = (
            {}, {}, ['draft', 'under investigation', 'resolved', 'rejected',
                     'Draft', 'Under Investigation', 'Resolved', 'Rejected']
        )

        try:
            redflag = self.get_object()

            try:
                status_data = request.data['status'].strip()

                if status_data.lower() in options:

                    data['status'] = status_data.lower()

                    updated_redflag = (
                        AdminRedflagSerializer(redflag,
                                               data=data,
                                               partial=True,
                                               context={'request': request}))

                    updated_redflag.is_valid(raise_exception=True)

                    self.perform_update(updated_redflag)

                    response_data = updated_redflag.data

                    response_data['createdBy'] = self.user_name(
                        updated_redflag.data['createdBy'])

                    send_email(response_data['createdBy'], status_data, response_data, updated_redflag, response, record_type)

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

    @action(methods=['patch'], detail=True,
            permission_classes=[IsAuthenticated],
            url_path='addImage', url_name='add_images')
    def add_images(self, request, pk=None, *args, **kwargs):
        """
        patch:
        Add images to redflag record
        """

        user_id, data, response = request.user.id, {}, {}

        try:
            record = self.get_object()

            saved_images = record.Image

            if 'image' in request.FILES.keys():

                if int(record.createdBy) == user_id:

                    uploaded_image_url = self.upload_image(request)

                    saved_images.append(uploaded_image_url)

                    data['Image'] = saved_images

                    updated_flag = (
                        IncidentSerializer(record,
                                           data=data,
                                           partial=True,
                                           context={
                                               'request': request}
                                           )
                    )

                    updated_flag.is_valid(raise_exception=True)

                    self.perform_update(updated_flag)

                    response['data'], response['status'] = (
                        updated_flag.data, 200
                    )

                    response['message'] = 'Image added to red-flag record'

                else:

                    response['error'], response['status'] = (
                        "You can not update a record you do not own",
                        403
                    )

            else:
                response['error'], response['status'] = (
                    {"image": "This field is required."}, 400
                )

        except Http404:

            response['error'], response['status'] = (
                "Redflag record with ID '{}' does not exist".format(pk),
                404
            )

        return Response(data=response, status=response['status'])

    @staticmethod
    def user_email(uid):
        user = User.objects.filter(id=uid)[0]
        return user.email


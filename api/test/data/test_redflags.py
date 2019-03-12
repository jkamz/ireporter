from django.test import TestCase
from users.models import User
from incidents.models import RedflagModel
from incidents.views import RedflagView

from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse


class RedflagCaseTest(TestCase):

    def setUp(self):
        """ Define the test client and test variables. """

        self.client = APIClient()
        self.login_url = reverse('user_login')

        self.user_data = {
            "first_name": 'Adeline',
            "other_name": 'Ranger',
            "last_name": 'Goethe',
            "email": 'test@gmail.com',
            "username": 'Ranger',
            "mobile_number": '+254701020304',
            "password": 'adminPassw0rd'
        }

        self.valid_login_data = {
            "username": 'test@gmail.com',
            "password": 'adminPassw0rd'
        }

        self.incident_data = {
            'title': 'This is the title',
            'status': "pending",
            'Image': '',
            'Video': '',
            'comment': 'This is the comment',
            'incident_type': 'red-flag',
            'location': 'Narok'
        }

        self.token = self.activate_account_and_login()

    def signup_user_and_fetch_details(self, data=''):
        """
        This method signs up a user and returns
        user id and the token
        """
        data = self.user_data

        self.response = self.client.post(
            reverse('user_signup'),
            data,
            format="json"
        )

        user_id, token = self.response.context['uid'], \
            self.response.context['token']

        return user_id, token

    def activate_account_and_login(self, activate_data=''):
        """
        This method activates a user account using
        data from signup and also tries to login
        a user to the system
        """

        data = self.signup_user_and_fetch_details()

        self.activation_data = {
            "uid": data[0],
            "token": data[1]
        }

        if not activate_data:
            activate_data = self.activation_data

        self.client.post(
            reverse('user_activate'),
            self.activation_data,
            format="json"
        )

        self.response = self.client.post(
            self.login_url,
            self.valid_login_data,
            format="json"
        )

        return self.response.data['token']

    def test_can_create_redflag_record(self):
        view = RedflagView.as_view({'post': 'create'})
        response = self.client.post('/api/redflags/',
                                    self.incident_data, HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')

        assert response.status_code == 201, response.rendered_content

    def test_requires_title(self):
        new_incident = self.incident_data
        new_incident.update({'title': ''})
        response = self.client.post('/api/redflags/',
                                    new_incident, HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')

        assert response.status_code == 400, response.rendered_content

    def test_requires_status(self):
        new_incident = self.incident_data
        new_incident.update({'status': ''})
        response = self.client.post('/api/redflags/', new_incident,
                                    HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')

        assert response.status_code == 400, response.rendered_content

    def test_requires_comment(self):
        new_incident = self.incident_data
        new_incident.update({'comment': ''})
        response = self.client.post('/api/redflags/', new_incident,
                                    HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')

        assert response.status_code == 400, response.rendered_content

    def test_requires_location(self):
        new_incident = self.incident_data
        new_incident.update({'location': ''})
        response = self.client.post('/api/redflags/', new_incident,
                                    HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')

        assert response.status_code == 400, response.rendered_content

    def test_duplicate_redflag(self):
        view = RedflagView.as_view({'post': 'create'})
        self.client.post('/api/redflags/',
                         self.incident_data, HTTP_AUTHORIZATION='Bearer ' + self.token,
                         format='json')
        response = self.client.post('/api/redflags/',
                                    self.incident_data, HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')

        assert response.status_code == 409, response.rendered_content

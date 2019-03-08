import json
from django.test import TestCase
from users.models import User
from incidents.views import CreateIncidentView
from incidents.models import Incident

from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.shortcuts import redirect
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

class ModelTestCase(TestCase):
    """
    This class defines the test suite for user registration
    cases.
    """

    def setUp(self):
        """ Define the test client and test variables. """

        self.first_name = 'Johnny'
        self.other_name = 'Wilder'
        self.last_name = 'Walker'
        self.email = 'Johnny@wilder.com'
        self.username = 'Walker'
        self.mobile_number = '+254701020304'
        self.password = 'adminPassw0rd'

        self.user = User(first_name=self.first_name, last_name=self.last_name, other_name=self.other_name,
                         email=self.email, username=self.username, mobile_number=self.mobile_number, password=self.password)

    def test_model_can_create_a_user(self):
        old_count = User.objects.count()
        self.user.save()
        new_count = User.objects.count()
        self.assertNotEqual(old_count, new_count)


class UserSignupViewCase(TestCase):
    """ 
    Test suite for the user registration api view
    """

    def setUp(self):
        """ Define the test client and test variables. """

        self.client = APIClient()

        self.user_data = {
            "first_name": 'Adeline',
            "other_name": 'Ranger',
            "last_name": 'Goethe',
            "email": 'Ranger@gmail.com',
            "username": 'Ranger',
            "mobile_number": '+254701020304',
            "password": 'adminPassw0rd'
        }

        self.user_data_1 = {
            "first_name": 'Django',
            "other_name": 'ongajd',
            "last_name": 'Python',
            "email": 'Django@python.com',
            "username": 'Python',
            "mobile_number": '+254701020305',
            "password": 'adminPassw0rd'
        }

        self.missing_user_data = {
            "first_name": 'Django',
            "other_name": 'ongajd',
            "email": 'Django@python.com',
            "username": 'Python',
            "mobile_number": '+254701020305',
            "password": 'adminPassw0rd'
        }

        self.response = self.client.post(
            reverse('user_signup'),
            self.user_data,
            format="json"
        )

    def fetch_activation_details(self, data=''):
        """
        This method 'register_user' registers an account
        using provided a user's details and returns the 
        token and userlocation used for activation of data
        """

        if not data:
            data = self.user_data_1

        self.response = self.client.post(
            reverse('user_signup'),
            data,
            format="json"
        )

        user_id, token = self.response.context['uid'], self.response.context['token']

        return user_id, token

    def register_user(self, data=''):
        """
        This method 'register_user' registers an account
        using provided a user's details
        """

        if not data:
            data = self.user_data

        self.response = self.client.post(
            reverse('user_signup'),
            data,
            format="json"
        )

        return self.response

    def activate_account(self, activate_data=''):
        """ 
        This methods 'activate_account' activates a user
        account.
        """

        data = self.fetch_activation_details()

        self.activation_data = {
            "uid": data[0],
            "token": data[1]
        }

        if not activate_data:
            activate_data = self.activation_data

        self.response = self.client.post(
            reverse('user_activate'),
            activate_data,
            format="json"
        )

        return self.response

    def test_successful_registration_if_correct_details(self):
        """
        Test for successfull creation of user account
        if correct data provided. 
        """

        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_successful_activation_of_account(self):
        """
        Tests for successful activation of user account if correct
        user id and token.
        """

        self.assertEqual(self.activate_account().status_code,
                         status.HTTP_200_OK)

    def test_error_raised_if_missing_key(self):
        """
        Tests for failure to register user if missing data 
        """

        new_user = self.register_user(data=self.missing_user_data)

        self.assertEqual(new_user.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_to_activate_if_wrong_payload(self):
        """
        Test for Bad Request raised if incorrect user id
        or token is provided.
        """

        activate = {
            "uid": 4,
            "token": 'incorect.token.items.random'
        }

        self.assertEqual(self.activate_account(
            activate_data=activate).status_code, status.HTTP_400_BAD_REQUEST)


class IncidetCaseTest(TestCase):
    
    def setUp(self):
        """ Define the test client and test variables. """

        self.client = APIClient()

        self.user_data = {
            "first_name": 'Adeline',
            "other_name": 'Ranger',
            "last_name": 'Goethe',
            "email": 'Ranger@gmail.com',
            "username": 'Ranger',
            "mobile_number": '+254701020304',
            "password": 'adminPassw0rd'
        }
        
        self.incident_data = { 
             'title' : 'This is the title', 
             'status' : "pending", 
             'Image' : '', 
             'Video' : '', 
             'comment' : 'This is the comment', 
             'incident_type' : 'red-flag',
             'location' : 'Narok'
         }

        self.response = self.client.post(
            reverse('user_signup'),
            self.user_data,
            format="json"
        )

    def test_can_create_redflag_record(self):
        user = User.objects.get(username='Ranger')
        view = CreateIncidentView.as_view({'post': 'create'})
        factory = APIRequestFactory()
        request = factory.post('/api/redflags/', self.incident_data)
        force_authenticate(request, user=user, token=self.response.context['token'])
        response = view(request)

        assert response.status_code == 201, response.rendered_content

    def test_requires_title(self):
        new_incident = self.incident_data
        new_incident.update({'title':''})
        user = User.objects.get(username='Ranger')
        view = CreateIncidentView.as_view({'post': 'create'})
        factory = APIRequestFactory()
        request = factory.post('/api/redflags/', new_incident)
        force_authenticate(request, user=user, token=self.response.context['token'])
        response = view(request)

        assert response.status_code == 400, response.rendered_content

    def test_requires_status(self):
        new_incident = self.incident_data
        new_incident.update({'status':''})
        user = User.objects.get(username='Ranger')
        view = CreateIncidentView.as_view({'post': 'create'})
        factory = APIRequestFactory()
        request = factory.post('/api/redflags/', new_incident)
        force_authenticate(request, user=user, token=self.response.context['token'])
        response = view(request)

        assert response.status_code == 400, response.rendered_content

    def test_requires_comment(self):
        new_incident = self.incident_data
        new_incident.update({'comment':''})
        user = User.objects.get(username='Ranger')
        view = CreateIncidentView.as_view({'post': 'create'})
        factory = APIRequestFactory()
        request = factory.post('/api/redflags/', new_incident)
        force_authenticate(request, user=user, token=self.response.context['token'])
        response = view(request)
        
        assert response.status_code == 400, response.rendered_content

    def test_requires_location(self):
        new_incident = self.incident_data
        new_incident.update({'location':''})
        user = User.objects.get(username='Ranger')
        view = CreateIncidentView.as_view({'post': 'create'})
        factory = APIRequestFactory()
        request = factory.post('/api/redflags/', new_incident)
        force_authenticate(request, user=user, token=self.response.context['token'])
        response = view(request)

        assert response.status_code == 400, response.rendered_content

    def test_requires_incident_type(self):
        new_incident = self.incident_data
        new_incident.update({'incident_type':''})
        user = User.objects.get(username='Ranger')
        view = CreateIncidentView.as_view({'post': 'create'})
        factory = APIRequestFactory()
        request = factory.post('/api/redflags/', new_incident)
        force_authenticate(request, user=user, token=self.response.context['token'])
        response = view(request)

        assert response.status_code == 400, response.rendered_content
        
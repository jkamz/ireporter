from django.test import TestCase
from users.models import User
from incidents.models import RedflagModel
from incidents.views import RedflagView

from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
import json


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

        self.draft_status = {
            'title': 'This is the draft redflag',
            'status': "draft",
            'Image': '',
            'Video': '',
            'comment': 'This record has the status set to draft',
            'incident_type': 'red-flag',
            'location': 'Narok'
        }

        self.processed_status = {
            'title': 'This is the resolved redflag',
            'status': "resolved",
            'Image': '',
            'Video': '',
            'comment': 'This record has been resolved',
            'incident_type': 'red-flag',
            'location': 'Narok'
        }

        self.control_user_data = {
            "first_name": 'Jim',
            "other_name": 'Powel',
            "last_name": 'Goethe',
            "email": 'testers@gmail.com',
            "username": 'Powel',
            "mobile_number": '+254701020305',
            "password": 'adminPassw0rd'
        }

        self.token = self.activate_account_and_login()

        self.control_user = self.client.post(
            reverse('user_signup'),
            self.control_user_data,
            format="json"
        )

        self.activation_data = {
            "uid": self.control_user.data['id'],
            "token": self.control_user.data['token']
        }

        activation = self.client.post(
            reverse('user_activate'),
            self.activation_data,
            format="json"
        )

        self.control_login = {
            'username': 'testers@gmail.com',
            'password': 'adminPassw0rd'
        }

        self.login_control = self.client.post(
            self.login_url,
            data=self.control_login,
            format="json"
        )

        # print(json.loads(self.login_control.content))

        self.control_token = self.login_control.data['token']

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

    def delete_redflag(self, url='/api/redflags/redflag-id/'):
        """ Deletes a redflag record """

        response = self.client.delete(
            url, HTTP_AUTHORIZATION='Bearer ' + self.token)

        return response

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

    def test_deletes_redflag_if_correct_details(self):
        """
        Tests for successful deletion of redflag record if
        user owns an existing redflag record
        """

        new_incident = self.client.post('/api/redflags/', self.draft_status,
                                        HTTP_AUTHORIZATION='Bearer ' + self.token, format='json')

        flag_id = new_incident.data['data']['id']

        self.assertEqual(new_incident.status_code, status.HTTP_201_CREATED)

        self.assertEqual(self.delete_redflag(
            url='/api/redflags/{}/'.format(flag_id)).status_code, status.HTTP_200_OK)

    def test_raises_error_if_missing_record(self):
        """
        Tests for failure to delete if redflag record does
        not already exist
        """

        self.assertEqual(self.delete_redflag(
            url='/api/redflags/2000/').status_code, status.HTTP_404_NOT_FOUND)

    def test_raises_error_if_not_record_owner(self):
        """
        Tests for failure to delete if the user doesn't own
        the record
        """

        new_incident = self.client.post('/api/redflags/', self.draft_status,
                                        HTTP_AUTHORIZATION='Bearer ' + self.token, format='json')

        flag_id = new_incident.data['data']['id']

        self.assertEqual(new_incident.status_code, status.HTTP_201_CREATED)

        response = self.client.delete(
            '/api/redflags/{}/'.format(flag_id), HTTP_AUTHORIZATION='Bearer ' + self.control_token)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_raises_error_if_record_is_processed(self):
        """
        Test for failure to delete if the status
        of the record is 'under investigation' or
        'resolved' or 'rejected'.
        """

        new_incident = self.client.post('/api/redflags/', self.processed_status,
                                        HTTP_AUTHORIZATION='Bearer ' + self.token, format='json')

        flag_id = new_incident.data['data']['id']

        self.assertEqual(new_incident.status_code, status.HTTP_201_CREATED)

        response = self.client.delete(
            '/api/redflags/{}/'.format(flag_id), HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_redlfags(self):
        view = RedflagView.as_view({'post': 'create'})
        self.client.post('/api/redflags/',
                         self.incident_data,
                         HTTP_AUTHORIZATION='Bearer ' + self.token,
                         format='json')

        view = RedflagView.as_view({'get': 'list'})
        response = self.client.get('/api/redflags/',
                                   HTTP_AUTHORIZATION='Bearer ' + self.token,
                                   format='json')
        result = json.loads(response.content.decode('utf-8'))

        self.assertTrue(result['data'])
        assert response.status_code == 200, response.content

    def test_get_one_redlfag(self):
        view = RedflagView.as_view({'post': 'create'})
        response = self.client.post('/api/redflags/',
                                    self.incident_data,
                                    HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')
        flag_details = json.loads(response.content.decode('utf-8'))
        flag_url = flag_details['data']['url']

        view = RedflagView.as_view({'get': 'retrieve'})
        response = self.client.get(flag_url,
                                   HTTP_AUTHORIZATION='Bearer ' + self.token,
                                   format='json')
        result = json.loads(response.content.decode('utf-8'))

        self.assertTrue(result['data'])
        assert response.status_code == 200, response.content

    def test_redlag_not_found(self):
        view = RedflagView.as_view({'get': 'retrieve'})
        response = self.client.get('/api/redflags/20/',
                                   HTTP_AUTHORIZATION='Bearer ' + self.token,
                                   format='json')
        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual(result['message'], 'Redflag with id 20 not found')
        assert response.status_code == 404, response.content

    def test_can_update_redflag_record(self):

        # first create a redflag
        view = RedflagView.as_view({'post': 'create'})
        response = self.client.post('/api/redflags/',
                                    self.draft_status, HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')

        redflag_data = json.loads(response.content.decode('utf-8'))
        incident_url = redflag_data['data']['url']

        # update redflag
        view = RedflagView.as_view({'put': 'update'})
        update_data = self.incident_data
        update_data.update({'location': 'New Location'})
        response = self.client.put(
            incident_url, update_data, HTTP_AUTHORIZATION='Bearer ' + self.token, format='json')

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual(result['location'], 'New Location')
        assert response.status_code == 200, response.content

    def test_only_owner_can_update_redflag(self):
        # first create a redflag
        view = RedflagView.as_view({'post': 'create'})
        response = self.client.post('/api/redflags/',
                                    self.draft_status, HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')

        redflag_data = json.loads(response.content.decode('utf-8'))
        incident_url = redflag_data['data']['url']

        # update redflag
        view = RedflagView.as_view({'put': 'update'})
        update_data = self.incident_data
        update_data.update({'location': 'New Location'})
        response = self.client.put(
            incident_url, update_data, HTTP_AUTHORIZATION='Bearer ' + self.control_token, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_update_status(self):
        # first create a redflag
        view = RedflagView.as_view({'post': 'create'})
        response = self.client.post('/api/redflags/',
                                    self.draft_status, HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')

        redflag_data = json.loads(response.content.decode('utf-8'))
        incident_url = redflag_data['data']['url']

        # update redflag status
        view = RedflagView.as_view({'put': 'update'})
        update_data = self.incident_data
        update_data.update({'status': 'new status'})
        response = self.client.put(
            incident_url, update_data, HTTP_AUTHORIZATION='Bearer ' + self.token, format='json')

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual(result['status'], 'draft')
        assert response.status_code == 200, response.content

    def test_user_cannot_update_if_not_draft(self):
        # first create a redflag with a resolved status
        view = RedflagView.as_view({'post': 'create'})
        response = self.client.post('/api/redflags/',
                                    self.processed_status, HTTP_AUTHORIZATION='Bearer '
                                    + self.token, format='json')

        redflag_data = json.loads(response.content.decode('utf-8'))
        incident_url = redflag_data['data']['url']

        # update redflag
        view = RedflagView.as_view({'put': 'update'})
        update_data = self.incident_data
        update_data.update({'location': 'Nairobi'})
        response = self.client.put(
            incident_url, update_data, HTTP_AUTHORIZATION='Bearer ' + self.token, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

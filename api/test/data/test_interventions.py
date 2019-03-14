from django.test import TestCase
from interventions.models import InterventionsModel
from interventions.views import InterventionsView

from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
import json


class InterventionsTestsCase(TestCase):

    def setUp(self):
        """ Define the test client and test variables for Interventions. """

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

        self.intervention_data = {
            'title': 'Sample intervention title',
            'comment': 'Sample intervention comment',
            'location': '24.00, 45.006',
            'Image': '',
            'Video': ''
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

    def test_can_create_intervention(self):
        """test that can create intervention record"""

        self.response = self.client.post('/api/interventions/',
                                         self.intervention_data,
                                         HTTP_AUTHORIZATION='Bearer ' +
                                         self.token,
                                         format='json')

        self.assertEqual(self.response.status_code,
                         status.HTTP_201_CREATED)

    def test_cannot_create_intervention_missing_title(self):
        """test that title is required to create an intervention"""

        updated_data = self.intervention_data
        updated_data.update({'title': ''})
        self.response = self.client.post('/api/interventions/',
                                         updated_data,
                                         HTTP_AUTHORIZATION='Bearer ' +
                                         self.token,
                                         format='json')

        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_requires_comment_for_intervention(self):
        """test that cannot create intervention missing comment"""

        updated_data = self.intervention_data
        updated_data.update({'comment': ''})
        self.response = self.client.post('/api/interventions/', updated_data,
                                         HTTP_AUTHORIZATION='Bearer ' +
                                         self.token,
                                         format='json')

        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_throws_error_missing_lat_long(self):
        """test theres an error when user does not provide lat and long"""

        updated_data = self.intervention_data
        updated_data.update({'location': ''})
        self.response = self.client.post('/api/interventions/', updated_data,
                                         HTTP_AUTHORIZATION='Bearer ' +
                                         self.token,
                                         format='json')

        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_throws_error_on_duplicate_intervention(self):
        """test there an error on duplicate records by same user"""

        self.client.post('/api/interventions/',
                         self.intervention_data, HTTP_AUTHORIZATION='Bearer ' +
                         self.token,
                         format='json')
        self.response = self.client.post('/api/interventions/',
                                         self.intervention_data,
                                         HTTP_AUTHORIZATION='Bearer ' +
                                         self.token,
                                         format='json')

        self.assertEqual(self.response.status_code, status.HTTP_409_CONFLICT)

    def test_cannot_create_comment_with_special_chars_only(self):
        """
        test that an intervention comment cannot
        have only special characters
        """
        updated_data = self.intervention_data
        updated_data.update(
            {'comment': '##################$$$$$$$$$$$$$$$$$$$$$@@@@@@'})
        self.response = self.client.post('/api/interventions/',
                                         updated_data,
                                         HTTP_AUTHORIZATION='Bearer ' +
                                         self.token,
                                         format='json')

        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_title_with_special_chars_only(self):
        """
        test that an intervention title cannot have only special characters
        """

        updated_data = self.intervention_data
        updated_data.update(
            {'title': '##################$$$$$$$$$$$$$$$$$$$$$@@@@@@'})
        self.response = self.client.post('/api/interventions/',
                                         updated_data,
                                         HTTP_AUTHORIZATION='Bearer ' +
                                         self.token,
                                         format='json')

        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_intervention_with_invalid_lat_long_values(self):
        """
        test that an intervention title cannot have only special characters
        """

        updated_data = self.intervention_data
        updated_data.update({'location': '23.345, invalid'})
        self.response = self.client.post('/api/interventions/',
                                         updated_data,
                                         HTTP_AUTHORIZATION='Bearer ' +
                                         self.token,
                                         format='json')

        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)
    
    def test_get_all_interventions(self):
        view = InterventionsView.as_view({'post': 'create'})
        self.client.post('/api/interventions/',
                         self.intervention_data,
                         HTTP_AUTHORIZATION='Bearer ' + self.token,
                         format='json')

        view = InterventionsView.as_view({'get': 'list'})
        response = self.client.get('/api/interventions/',
                                   HTTP_AUTHORIZATION='Bearer ' + self.token,
                                   format='json')
        result = json.loads(response.content.decode('utf-8'))

        self.assertTrue(result['data'])
        assert response.status_code == 200, response.content

    def test_get_one_intervention(self):
        view = InterventionsView.as_view({'post': 'create'})
        response = self.client.post('/api/interventions/',
                                    self.intervention_data,
                                    HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')
        _details = json.loads(response.content.decode('utf-8'))
        _object = _details['data']
        _id = _object['id']

        view = InterventionsView.as_view({'get': 'retrieve'})
        response = self.client.get('/api/interventions/' + str(_id) + '/',
                                   HTTP_AUTHORIZATION='Bearer ' + self.token,
                                   format='json')
        result = json.loads(response.content.decode('utf-8'))

        self.assertTrue(result['data'])
        assert response.status_code == 200, response.content

    def test_intervention_not_found(self):
        view = InterventionsView.as_view({'get': 'retrieve'})
        response = self.client.get('/api/interventions/20/',
                                   HTTP_AUTHORIZATION='Bearer ' + self.token,
                                   format='json')
        result = json.loads(response.content.decode('utf-8'))


        self.assertEqual(result['message'], 'Intervention with id 20 not found')
        assert response.status_code == 404, response.content

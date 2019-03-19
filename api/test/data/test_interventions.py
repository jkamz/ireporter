from django.test import TestCase
from users.models import User
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

        self.adminuser = User.objects.create_user(
            'admin@test.com', 'rootpassword')
        self.adminuser.save()
        self.adminuser.is_superuser = True
        self.adminuser.is_staff = True
        self.adminuser.save()

        self.user_data = {
            "first_name": 'Adeline',
            "other_name": 'Ranger',
            "last_name": 'Goethe',
            "email": 'test@gmail.com',
            "username": 'Ranger',
            "mobile_number": '+254701020304',
            "password": 'adminPassw0rd'
        }

        # signup and login another user
        self.control_user_data = {
            "first_name": 'Jim',
            "other_name": 'Powel',
            "last_name": 'Goethe',
            "email": 'testers@gmail.com',
            "username": 'Powel',
            "mobile_number": '+254701020305',
            "password": 'adminPassw0rd'
        }

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

        self.control_token = self.login_control.data['token']

        self.admin_update_data = {
            "title": "Title update by Admin",
            "status": "resolved"
        }

        self.admin_incorrect_status = {
            "status": "Accepted"
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

        self.control_intervention_data = {
            'title': 'Sample control title',
            'comment': 'Sample control comment',
            'location': '84.00, 124.00',
            'Image': '',
            'Video': ''
        }

        self.admin_login = {
            'username': 'admin@test.com',
            'password': 'rootpassword'
        }

        self.admin_control = self.client.post(
            self.login_url,
            data=self.admin_login,
            format="json"
        )

        self.admin_token = self.admin_control.data['token']

        self.intervention_data_2 = {
            'title': 'intervention title',
            'comment': 'intervention comment',
            'location': '24.00, 45.006',
            'Image': '',
            'Video': '',
            'status': 'rejected'
        }

        self.token = self.activate_account_and_login()

        self.intervention_record = self.create_intervention_record(
            data=self.control_intervention_data)

        self.flag_id, self.flag_title, self.flag_comment = (
            self.intervention_record.data['data']['id'],
            self.intervention_record.data['data']['title'],
            self.intervention_record.data['data']['comment']
        )

        self.update_status_url = '/api/interventions/{}/status/'.format(
            self.flag_id)

    def signup_user_and_fetch_details(self, data=''):
        """
        This method signs up a user and returns
        user id and the token
        """
        if not data:
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
        if not activate_data:
            data = self.signup_user_and_fetch_details()
            self.activation_data = {
                "uid": data[0],
                "token": data[1]
            }
            activate_data = self.activation_data

        self.client.post(
            reverse('user_activate'),
            activate_data,
            format="json"
        )

        self.response = self.client.post(
            self.login_url,
            self.valid_login_data,
            format="json"
        )

        return self.response.data['token']

    def update_intervention_status(self, url="", data='', token=''):
        """
        Updates the status of a intervention record
        """

        if not token:
            token = self.token

        if not data:
            data = self.admin_update_data

        response = self.client.patch(
            url, data=data,
            format="json",
            HTTP_AUTHORIZATION='Bearer ' + token
        )

        return response

    def create_intervention_record(self, url='', data='', token=''):
        """
        Creates an intervention record with provided data
        """

        if not token:
            token = self.token

        if not data:
            data = self.intervention_data

        if not url:
            url = '/api/interventions/'

        response = self.client.post(url, data,
                                    HTTP_AUTHORIZATION='Bearer ' + token,
                                    format='json')

        return response

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

        self.assertEqual(result['message'],
                         'Intervention with id 20 not found')
        assert response.status_code == 404, response.content

    def test_updates_status_if_correct_details(self):
        """
        Tests for successful update of status if
        correct value provided for status and
        user is admin
        """

        intervention_update = self.update_intervention_status(
            self.update_status_url,
            data=self.admin_update_data,
            token=self.admin_token)

        self.assertEqual(intervention_update.status_code, status.HTTP_200_OK)

        self.assertEqual(
            intervention_update.data['data']['status'],
            self.admin_update_data['status'])

        self.assertEqual(
            intervention_update.data['data']['title'], self.flag_title)

        self.assertEqual(
            intervention_update.data['data']['comment'], self.flag_comment)

    def test_raises_bad_request_if_status_key_missing(self):
        """
        Test for failure to update if the 'status' key and value
        is not provided
        """

        intervention_update = self.update_intervention_status(
            self.update_status_url,
            data={"title": "intervention title"},
            token=self.admin_token
        )

        self.assertEqual(intervention_update.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_raises_bad_request_if_invalid_status_value(self):
        """
        Tests for failure to update if an invalid value
        is provided for the 'status'
        """

        intervention_update = self.update_intervention_status(
            self.update_status_url,
            data=self.admin_incorrect_status,
            token=self.admin_token
        )

        self.assertEqual(intervention_update.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_raises_error_if_not_admin_user(self):
        """
        Tests for failure to update if the user
        is not an 'Admin'.
        """

        intervention_update = self.update_intervention_status(
            self.update_status_url, data=self.admin_update_data)

        self.assertEqual(intervention_update.status_code,
                         status.HTTP_403_FORBIDDEN)

    def test_raises_not_found_if_record_missing(self):
        """
        Test for failure to update intervention if the
        record does not exist
        """

        intervention_update = self.update_intervention_status(
            url='/api/interventions/100000/status/',
            data=self.admin_update_data,
            token=self.admin_token
        )

        self.assertEqual(intervention_update.status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_deletes_intervention_if_correct_details(self):
        """
        Tests for successful deletion of intervention record if
        user owns the existing intervention record
        """

        new_intervention = self.client.post('/api/interventions/',
                                            self.intervention_data,
                                            HTTP_AUTHORIZATION='Bearer ' +
                                            self.token, format='json')

        id = new_intervention.data['data']['id']

        self.response = self.client.delete('/api/interventions/{}/'.format(id),
                                           HTTP_AUTHORIZATION='Bearer ' +
                                           self.token,
                                           format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_200_OK)

    def test_raises_error_on_nonexistent_record(self):
        """
        Test for error message if user tries to delete non existent record
        """
        self.response = self.client.delete('/api/interventions/9000/',
                                           HTTP_AUTHORIZATION='Bearer ' +
                                           self.token,
                                           format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_if_not_owner(self):
        """
        Test that a user cannot delete other peoples records
        """
        new_intervention = self.client.post('/api/interventions/',
                                            self.intervention_data,
                                            HTTP_AUTHORIZATION='Bearer ' +
                                            self.token, format='json')

        id = new_intervention.data['data']['id']

        self.response = self.client.delete('/api/interventions/{}/'.format(id),
                                           HTTP_AUTHORIZATION='Bearer ' +
                                           self.control_token,
                                           format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_if_status_is_changed(self):
        """
        Test that a user cannot delete their records if
        admin has changed their status to either resolved,
        rejected or under investigation
        """
        new_intervention = self.client.post('/api/interventions/',
                                            self.intervention_data,
                                            HTTP_AUTHORIZATION='Bearer ' +
                                            self.token, format='json')

        id = new_intervention.data['data']['id']

        self.update_intervention_status(
            '/api/interventions/{}/status/'.format(id),
            data=self.admin_update_data,
            token=self.admin_token)

        self.response = self.client.delete('/api/interventions/{}/'.format(id),
                                           HTTP_AUTHORIZATION='Bearer ' +
                                           self.token,
                                           format='json')
        self.assertEqual(self.response.status_code,
                         status.HTTP_403_FORBIDDEN)
    def test_update_an_intervention(self):
        """
        Test that a user can successfully update
        their intervention record
        """
        view = InterventionsView.as_view({'post': 'create'})
        response = self.client.post('/api/interventions/',
                                    self.intervention_data,
                                    HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')
        flag_details = json.loads(response.content.decode('utf-8'))
        flag_url = flag_details['data']['url']

        view = InterventionsView.as_view({'put': 'update'})
        data = self.intervention_data
        data.update({'title': 'Another title'})
        response = self.client.put(flag_url,
                                   data,
                                   HTTP_AUTHORIZATION='Bearer ' + self.token,
                                   format='json')
        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual(result['data']['title'], 'Another title')
        assert response.status_code == 200, response.content

    def test_only_owner_can_update_an_intervention(self):
        """
        Test that a user can only update
        an intervention they have created
        """
        view = InterventionsView.as_view({'post': 'create'})
        response = self.client.post('/api/interventions/',
                                    self.intervention_data,
                                    HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')
        flag_details = json.loads(response.content.decode('utf-8'))
        flag_url = flag_details['data']['url']

        sign_up_data = {
            "first_name": 'Adel',
            "other_name": 'singer',
            "last_name": 'leda',
            "email": 'adele@gmail.com',
            "username": 'Adele',
            "mobile_number": '+254701020324',
            "password": 'adminPassw0rd'}
        sign_up_user = self.signup_user_and_fetch_details(data=sign_up_data)
        activate_data = {'uid': sign_up_user[0], 'token': sign_up_user[1]}
        self.activate_account_and_login(activate_data=activate_data)
        self.response = self.client.post(self.login_url,
                                         data={"username": 'adele@gmail.com',
                                               "password": 'adminPassw0rd'},
                                         format="json")
        token = json.loads(self.response.content.decode('utf-8'))
        token = token['token']

        view = InterventionsView.as_view({'put': 'update'})
        data = self.intervention_data
        data.update({'title': 'A different title'})
        response2 = self.client.put(flag_url,
                                    data,
                                    HTTP_AUTHORIZATION='Bearer ' + token,
                                    format='json')
        result = json.loads(response2.content.decode('utf-8'))

        self.assertEqual(
            result['message'],
            'You cannot edit an intervention you do not own')
        assert response2.status_code == 403, response2.content

    def test_cannot_update_an_intervention_status(self):
        """
        Test that a user cannot update the status of
        an intervention record
        """
        view = InterventionsView.as_view({'post': 'create'})
        response = self.client.post('/api/interventions/',
                                    self.intervention_data,
                                    HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')
        flag_details = json.loads(response.content.decode('utf-8'))
        flag_url = flag_details['data']['url']

        view = InterventionsView.as_view({'put': 'update'})
        data = self.intervention_data_2
        data.update({'status': 'approve please'})

        response = self.client.put(flag_url,
                                   data,
                                   HTTP_AUTHORIZATION='Bearer ' + self.token,
                                   format='json')
        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual(
            result['data']['status'],
            'draft')

    def test_cannot_update_an_intervention_if_status_not_draft(self):
        """
        Test that a user cannot update an intervention record
        if the status has been changed by the admin
        """
        view = InterventionsView.as_view({'post': 'create'})
        response = self.client.post('/api/interventions/',
                                    self.intervention_data,
                                    HTTP_AUTHORIZATION='Bearer ' + self.token,
                                    format='json')
        flag_details = json.loads(response.content.decode('utf-8'))
        flag_url = flag_details['data']['url']

        intervention_update = self.update_intervention_status(
            flag_url+'status/',
            data=self.admin_update_data,
            token=self.admin_token)

        view = InterventionsView.as_view({'put': 'update'})
        data = self.intervention_data
        data.update({'title': 'I got robbed!'})

        response = self.client.put(flag_url,
                                   data,
                                   HTTP_AUTHORIZATION='Bearer ' + self.token,
                                   format='json')
        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual(
            result['message'],
            'You cannot edit the intervention since its status is: resolved')
        assert response.status_code == 403


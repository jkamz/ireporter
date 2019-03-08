import json
from django.test import TestCase
from users.models import User

from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse


class UserLoginTest(TestCase):
    """
    Test suite for the user login
    """

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
            "email": 'test@gmail.com',
            "password": 'adminPassw0rd'
        }

        self.wrong_login_data = {
            "email": 'test@gmail.com',
            "password": 'wrong'
        }

        self.missing_login_data = {
            "email": 'test@gmail.com'
        }

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

        # activate the account
        self.client.post(
            reverse('user_activate'),
            self.activation_data,
            format="json"
        )

        # login the user
        self.response = self.client.post(
            self.login_url,
            self.valid_login_data,
            format="json"
        )

        return self.response

    def test_success_login_using_correct_details(self):
        """
        Tests for successful login if correct details
        and activated account
        """
        self.assertEqual(self.activate_account_and_login().status_code,
                         status.HTTP_200_OK)

    def test_user_cannot_login_with_account_not_activated(self):
        """
        Test method to verify user cannot login
        with unverfied email address
        """
        # sign-up user
        data = self.user_data

        self.client.post(
            reverse('user_signup'),
            data,
            format="json"
        )
        # login the user without activating
        self.response = self.client.post(
            self.login_url,
            self.valid_login_data,
            format="json"
        )
        # assert
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_error_when_wrong_login_detail(self, activate_data=''):
        """
        Tests error thrown when a wrong login
        detail is provided
        """
        data = self.signup_user_and_fetch_details()

        self.activation_data = {
            "uid": data[0],
            "token": data[1]
        }

        if not activate_data:
            activate_data = self.activation_data

        # activate the account
        self.client.post(
            reverse('user_activate'),
            self.activation_data,
            format="json"
        )

        # login the user
        self.response = self.client.post(
            self.login_url,
            self.wrong_login_data,
            format="json"
        )
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_error_when_missing_field(self):
        """method to test when a field is missing during log in"""

        self.response = self.client.post(
            self.login_url,
            self.missing_login_data,
            format="json"
        )
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

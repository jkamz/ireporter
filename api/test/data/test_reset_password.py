import json
from django.test import TestCase
from users.models import User

from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse


class TestResetPassword(TestCase):
    """
    Test suite for the user reset password
    """

    def setUp(self):
        """ Define the test client and test variables. """

        self.client = APIClient()
        self.login_url = reverse('user_login')
        self.reset_password_url = reverse('reset_password')

        self.user_data = {
            "first_name": 'Adeline',
            "other_name": 'Ranger',
            "last_name": 'Goethe',
            "email": 'test@gmail.com',
            "username": 'Ranger',
            "mobile_number": '+254701020304',
            "password": 'adminPassw0rd'
        }

        self.unregistered_email = {
            "email": 'wrong@gmail.com',
        }

        self.empty_email = {
            "email": ''
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

    def test_activate_account_and_reset_password(self, activate_data=''):
        """
        This method tests for user activate account using
        data from signup, reset password, and confirms new password
        """

        data = self.signup_user_and_fetch_details()

        reset_password_confirm_url = reverse('reset_password_confirm')
        extra_params = ('?uid=%s&token=%s' % (data[0],data[1]))
        new_redirect_url = (reset_password_confirm_url + extra_params)

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

        self.client.post(
            reverse('reset_password'),
            self.user_data['email'],
            format="json"
        )

        self.reset_confirm_data = {
            "new_password": "pass123key",
            "re_new_password": "pass123key"
        }
 
        self.response = self.client.post(new_redirect_url,
            self.reset_confirm_data,
            format="json"
        )

        self.assertEqual(self.response.status_code,
                         status.HTTP_200_OK)

    def test_user_cannot_reset_password_with_account_not_activated(self):
        """
        Test method to ensure users cannot reset password with unverified
        email address
        """
        data = self.user_data

        self.client.post(
            reverse('user_signup'),
            data,
            format="json"
        )
        self.response = self.client.post(
            reverse('reset_password'),
            self.user_data['email'],
            format="json"
        )

        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_error_when_unregistered_email_used(self, activate_data=''):
        """
        Tests to test for unregistered email used to reset password
        """

        self.response = self.client.post(
            reverse('reset_password'),
            self.unregistered_email,
            format="json"
        )
        self.assertEqual(self.response.status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_error_when_missing_email_field(self):
        """Test for a missing field during password reset"""

        self.response = self.client.post(
            reverse('reset_password'),
            self.empty_email,
            format="json"
        )
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)



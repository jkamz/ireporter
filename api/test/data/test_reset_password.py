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

        self.email = {
            "email":self.user_data['email']
        }

        self.response = self.client.post(
            reverse('user_signup'),
            self.user_data,
            format="json")
        uid = self.response.context['uid']
        token = self.response.context['token']
        self.activation_data = {
            'uid': uid,
            'token': token
        }
        reset_password_confirm_url = reverse('reset_password_confirm')
        extra_params = ('?uid=%s&token=%s' % (uid,token))
        
        self.new_redirect_url = (reset_password_confirm_url + extra_params)
        self.activate = self.client.post(
            reverse('user_activate'),
            self.activation_data,
            format="json")
        self.reset_response = self.client.post(
            reverse('reset_password'),
            self.user_data['email'],
            format="json"
        )

    def test_reset_password(self):
        """
        This method tests for user reset confirm password
        """
        
        self.response
        self.activate
        response =  self.client.post(
            reverse('reset_password'),
            self.email,
            format="json"
        )

        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Check email to reset password.')

    def test_reset_password_confirm(self):
        """
        This method tests for user reset confirm password
        """

        self.reset_confirm_data = {
            "new_password": "pass123key",
            "re_new_password": "pass123key"
        }
 
        self.response = self.client.patch(self.new_redirect_url,
            self.reset_confirm_data,
            format="json"
        )

        self.assertEqual(self.response.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(self.response.data['message'], 'Password reset successfully.')
        self.assertEqual(self.response.data['status'], 200)

    def test_user_cannot_reset_password_with_account_not_activated(self):
        """
        Test method to ensure users cannot reset password with unverified
        email address
        """

        self.client.post(
            reverse('user_signup'),
            self.user_data,
            format="json"
        )
        self.response = self.client.post(
            reverse('reset_password'),
            self.user_data['email'],
            format="json"
        )

        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_error_when_unregistered_email_used(self):
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

    def test_error_when_reset_passwords_do_not_match(self):
        """Test for a missing field during password reset"""

        self.reset_response
        self.reset_confirm_data = {
            "new_password": "pass123key",
            "re_new_password": "passkey"
        }
 
        self.response = self.client.patch(self.new_redirect_url,
            self.reset_confirm_data,
            format="json"
        )
        
        self.assertEqual(self.response.status_code,
                         status.HTTP_400_BAD_REQUEST)

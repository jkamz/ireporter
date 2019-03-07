# from django.contrib.auth import get_user_model
# from django.contrib.auth.models import User
import json
from django.test import TestCaseteststests
from django.urls import reverse
from users.models import User
from rest_framework.test import APIClient
# from rest_framework.reverse import reverse as api_reverse
from rest_framework import status
from rest_framework.test import  APITestCase


class TestPasswordResetView(APITestCase):
    """
    This class tests for class that sends email to user for password reset
    """
    def setUp(self):
        """
        set up method to test email to be sent endpoint
        """
        self.client = APIClient()

        self.user = User.objects._create_user(
            nick_name = "test",
            email = "test@gmail.com",
            password = "test@123"
        )
        self.register_url = reverse('user_signup')
        self.activate_url = reverse('user_activate')
        self.reset_url = reverse('reset_password')
        self.client.post(self.register_url, self.user, format="json")
        self.client.post(self.activate_url, self.user, format="json")
        User.is_active = True

    def create_test_user(self):
        return self.client.post(self.register_url, self.user, format="json")

    def test_password_reset_email_sent(self, data=''):
        self.client.post(self.reset_url, self.user, format="json")

    def test_unregistered_email(self):
        """
        case where unregistered user tries to request a password
        """
        response = self.client.post(self.reset_url, data={"email":"wrong@gmail.com"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
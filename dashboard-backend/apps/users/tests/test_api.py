# API tests for users app
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User, Role
from apps.users.tests.factories import UserFactory, RoleFactory


class UserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_role = RoleFactory(name="admin")
        self.admin = UserFactory(role=self.admin_role)
        self.client.force_authenticate(user=self.admin)

    def test_user_list(self):
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_me(self):
        response = self.client.get('/api/v1/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

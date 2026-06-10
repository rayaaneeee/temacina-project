# Model tests for users app
from django.test import TestCase
from apps.users.models import User, Role, UserSector
from apps.users.tests.factories import UserFactory, RoleFactory, UserSectorFactory


class UserModelTest(TestCase):
    def setUp(self):
        self.role = RoleFactory(name="admin")
        self.sector = UserSectorFactory()

    def test_user_creation(self):
        user = UserFactory(role=self.role, sector=self.sector)
        self.assertIsNotNone(user.id)
        self.assertTrue(user.is_active)

    def test_user_full_name(self):
        user = UserFactory(first_name="John", last_name="Doe", role=self.role)
        self.assertEqual(user.full_name, "John Doe")

    def test_user_role_name(self):
        user = UserFactory(role=self.role)
        self.assertEqual(user.role_name, "admin")

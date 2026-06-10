# Service tests for users app
from django.test import TestCase
from apps.users.models import User, Role
from apps.users.services.user import UserService
from apps.users.tests.factories import UserFactory, RoleFactory


class UserServiceTest(TestCase):
    def setUp(self):
        self.admin_role = RoleFactory(name="admin")
        self.user_role = RoleFactory(name="user")
        self.admin = UserFactory(role=self.admin_role)

    def test_get_all_users(self):
        UserFactory.create_batch(5, role=self.user_role)
        users = UserService.get_all()
        self.assertEqual(users.count(), 6)  # 5 + admin

    def test_get_by_id(self):
        user = UserFactory(role=self.user_role)
        retrieved = UserService.get_by_id(user.id)
        self.assertEqual(retrieved.id, user.id)

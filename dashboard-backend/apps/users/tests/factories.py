# Test factories for creating test objects
import factory
from apps.users.models import User, Role, UserSector


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role

    name = factory.Faker('word')


class UserSectorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserSector

    name = factory.Faker('word')


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'Test@1234')
    role = factory.SubFactory(RoleFactory)
    is_active = True

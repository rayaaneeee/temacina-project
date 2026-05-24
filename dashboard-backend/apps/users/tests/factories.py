import factory
from factory.django import DjangoModelFactory
from faker import Faker
from apps.users.models import User

fake = Faker()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email      = factory.LazyAttribute(lambda _: fake.unique.email())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name  = factory.LazyAttribute(lambda _: fake.last_name())
    password   = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active  = True
    role       = User.Role.ANALYST

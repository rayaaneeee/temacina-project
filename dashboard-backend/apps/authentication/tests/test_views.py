import pytest
from django.urls import reverse
from apps.users.tests.factories import UserFactory

@pytest.mark.django_db
class TestLoginView:
    def test_login_success(self, client):
        user = UserFactory(email="test@example.com")
        user.set_password("strongpass123")
        user.save()

        url  = reverse("auth-login")
        resp = client.post(url, {"email": "test@example.com",
                                 "password": "strongpass123"},
                           content_type="application/json")
        assert resp.status_code == 200
        assert "access" in resp.json()["data"]

    def test_login_wrong_password(self, client):
        url  = reverse("auth-login")
        resp = client.post(url, {"email": "x@x.com", "password": "wrong"},
                           content_type="application/json")
        assert resp.status_code in (400, 401)

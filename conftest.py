import pytest
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from envios.models import Empleado


@pytest.fixture(autouse=True)
def limpiar_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    user = User.objects.create_user(
        username="test_empleado",
        email="empleado@encomiendas.pe",
        password="test1234",
    )
    Empleado.objects.create(
        codigo="EMP-TEST",
        nombres="Test",
        apellidos="Empleado",
        cargo="Tester",
        email=user.email,
        fecha_ingreso="2025-01-01",
    )
    return user


@pytest.fixture
def auth_client(api_client, user):
    """Cliente de API con JWT valido"""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
    )
    return api_client

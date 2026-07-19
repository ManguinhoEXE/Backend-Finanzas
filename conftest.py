"""
Configuración compartida de tests.

Define fixtures que se usan en múltiples archivos de test.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import AccessKey

# Obtener el modelo de usuario configurado
User = get_user_model()


@pytest.fixture
def user(db):
    """
    Fixture que crea un usuario de prueba.

    Returns:
        User: Usuario creado con nombre 'Usuario Test'
    """
    return User.objects.create_user(name='Usuario Test')


@pytest.fixture
def user_two(db):
    """
    Fixture que crea un segundo usuario de prueba.

    Returns:
        User: Usuario creado con nombre 'Usuario Dos'
    """
    return User.objects.create_user(name='Usuario Dos')


@pytest.fixture
def access_key(db):
    """
    Fixture que crea una llave de acceso no utilizada.

    Returns:
        AccessKey: Llave disponible para activar
    """
    return AccessKey.objects.create(key='LLAVE-TEST-001')


@pytest.fixture
def used_access_key(db):
    """
    Fixture que crea una llave de acceso ya utilizada.

    Returns:
        AccessKey: Llave marcada como usada
    """
    from django.utils import timezone
    return AccessKey.objects.create(
        key='LLAVE-TEST-USADA',
        used=True,
        used_at=timezone.now()
    )


@pytest.fixture
def auth_headers(user):
    """
    Fixture que retorna headers de autenticación JWT.

    Args:
        user: Usuario para generar el token

    Returns:
        dict: Headers con el token de autenticación
    """
    refresh = RefreshToken.for_user(user)
    return {
        'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'
    }


@pytest.fixture
def auth_headers_user_two(user_two):
    """
    Fixture que retorna headers de autenticación JWT para el segundo usuario.

    Args:
        user_two: Segundo usuario para generar el token

    Returns:
        dict: Headers con el token de autenticación
    """
    refresh = RefreshToken.for_user(user_two)
    return {
        'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'
    }

"""
Tests unitarios para la app de autenticación.

Prueba el endpoint POST /api/activate-key/ y todos los casos de uso:
- Activación exitosa con llave válida
- Error con llave inexistente
- Error con llave ya utilizada
- Generación correcta de JWT
- Estructura de la respuesta
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import AccessKey, User


@pytest.fixture
def api_client():
    """
    Fixture que crea un cliente de API para las pruebas.

    Returns:
        APIClient: Cliente de API sin autenticación
    """
    return APIClient()


@pytest.mark.django_db
class TestActivateKeySuccess:
    """
    Suite de tests para activación exitosa de llave.

    Verifica que el endpoint funcione correctamente
    cuando se proporciona una llave válida y no utilizada.
    """

    def test_activate_key_returns_201(self, api_client, access_key):
        """Verifica que retorna HTTP 201 al activar una llave válida."""
        url = reverse('activate-key')
        data = {'key': 'LLAVE-TEST-001', 'name': 'Juan'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_activate_key_creates_user(self, api_client, access_key):
        """Verifica que se crea un usuario en la base de datos."""
        url = reverse('activate-key')
        data = {'key': 'LLAVE-TEST-001', 'name': 'Juan'}
        api_client.post(url, data, format='json')
        assert User.objects.filter(name='Juan').exists()

    def test_activate_key_marks_key_as_used(self, api_client, access_key):
        """Verifica que la llave se marca como utilizada."""
        url = reverse('activate-key')
        data = {'key': 'LLAVE-TEST-001', 'name': 'Juan'}
        api_client.post(url, data, format='json')
        access_key.refresh_from_db()
        assert access_key.used is True
        assert access_key.used_at is not None

    def test_activate_key_returns_user_info(self, api_client, access_key):
        """Verifica que la respuesta contiene la información del usuario."""
        url = reverse('activate-key')
        data = {'key': 'LLAVE-TEST-001', 'name': 'Juan'}
        response = api_client.post(url, data, format='json')
        assert 'user' in response.data
        assert response.data['user']['name'] == 'Juan'

    def test_activate_key_returns_tokens(self, api_client, access_key):
        """Verifica que la respuesta contiene los tokens JWT."""
        url = reverse('activate-key')
        data = {'key': 'LLAVE-TEST-001', 'name': 'Juan'}
        response = api_client.post(url, data, format='json')
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']

    def test_activate_key_success_message(self, api_client, access_key):
        """Verifica que el mensaje de éxito es correcto."""
        url = reverse('activate-key')
        data = {'key': 'LLAVE-TEST-001', 'name': 'Juan'}
        response = api_client.post(url, data, format='json')
        assert response.data['detail'] == 'Cuenta activada exitosamente.'


@pytest.mark.django_db
class TestActivateKeyErrors:
    """
    Suite de tests para errores en la activación de llave.

    Verifica que el endpoint retorne errores adecuados
    cuando los datos de entrada son incorrectos.
    """

    def test_invalid_key_returns_400(self, api_client):
        """Verifica que retorna HTTP 400 con llave inexistente."""
        url = reverse('activate-key')
        data = {'key': 'LLAVE-NO-EXISTE', 'name': 'Juan'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_key_error_message(self, api_client):
        """Verifica el mensaje de error para llave inexistente."""
        url = reverse('activate-key')
        data = {'key': 'LLAVE-NO-EXISTE', 'name': 'Juan'}
        response = api_client.post(url, data, format='json')
        assert response.data['detail'] == 'La llave ingresada no es válida.'

    def test_used_key_returns_400(self, api_client, used_access_key):
        """Verifica que retorna HTTP 400 con llave ya utilizada."""
        url = reverse('activate-key')
        data = {'key': 'LLAVE-TEST-USADA', 'name': 'Juan'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_used_key_error_message(self, api_client, used_access_key):
        """Verifica el mensaje de error para llave ya utilizada."""
        url = reverse('activate-key')
        data = {'key': 'LLAVE-TEST-USADA', 'name': 'Juan'}
        response = api_client.post(url, data, format='json')
        assert response.data['detail'] == 'La llave ya fue utilizada anteriormente.'

    def test_missing_key_returns_400(self, api_client):
        """Verifica que retorna HTTP 400 si no se envía la llave."""
        url = reverse('activate-key')
        data = {'name': 'Juan'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_name_returns_400(self, api_client, access_key):
        """Verifica que retorna HTTP 400 si no se envía el nombre."""
        url = reverse('activate-key')
        data = {'key': 'LLAVE-TEST-001'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_empty_body_returns_400(self, api_client):
        """Verifica que retorna HTTP 400 si el body está vacío."""
        url = reverse('activate-key')
        response = api_client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestActivateKeyJWT:
    """
    Suite de tests para verificar la generación de JWT.

    Verifica que los tokens generados sean válidos
    y puedan usarse para autenticar peticiones.
    """

    def test_generated_token_is_valid(self, api_client, access_key):
        """Verifica que el token generado es válido para autenticación."""
        url = reverse('activate-key')
        data = {'key': 'LLAVE-TEST-001', 'name': 'Juan'}
        response = api_client.post(url, data, format='json')

        # Usar el token para acceder a un endpoint protegido
        token = response.data['tokens']['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Intentar acceder a la lista de gastos (requiere auth)
        expenses_url = reverse('expense-list')
        expenses_response = api_client.get(expenses_url)
        # Debería retornar 200 (aunque la lista esté vacía)
        assert expenses_response.status_code == status.HTTP_200_OK

    def test_token_belongs_to_created_user(self, api_client, access_key):
        """Verifica que el token pertenece al usuario creado."""
        from rest_framework_simplejwt.tokens import AccessToken

        url = reverse('activate-key')
        data = {'key': 'LLAVE-TEST-001', 'name': 'Juan'}
        response = api_client.post(url, data, format='json')

        token = response.data['tokens']['access']
        access_token = AccessToken(token)

        # Obtener el usuario del token
        user_id = access_token['user_id']
        user = User.objects.get(id=user_id)
        assert user.name == 'Juan'

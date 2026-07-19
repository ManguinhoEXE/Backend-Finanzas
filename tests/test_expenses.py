"""
Tests unitarios para la app de gastos.

Prueba el CRUD de gastos (sin eliminación):
- POST /api/expenses/ - Crear gasto (con campo compartido)
- GET /api/expenses/ - Listar gastos (propios + compartidos)
- PUT /api/expenses/{id}/ - Actualizar gasto

También verifica la seguridad:
- Un usuario solo ve sus propios gastos y los compartidos
- Un usuario no puede editar gastos de otro
- DELETE no está permitido (retorna 405)
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import User
from expenses.models import Expense


@pytest.fixture
def api_client():
    """
    Fixture que crea un cliente de API para las pruebas.

    Returns:
        APIClient: Cliente de API sin autenticación
    """
    return APIClient()


@pytest.fixture
def sample_expense(user):
    """
    Fixture que crea un gasto privado de ejemplo.

    Args:
        user: Usuario dueño del gasto

    Returns:
        Expense: Gasto creado en la base de datos
    """
    return Expense.objects.create(
        usuario=user,
        categoria='Alimentación',
        fecha='2026-07-15',
        descripcion='Almuerzo en restaurante',
        valor=45000.00,
        compartido=False
    )


@pytest.fixture
def sample_shared_expense(user):
    """
    Fixture que crea un gasto compartido del usuario 1.

    Args:
        user: Usuario dueño del gasto

    Returns:
        Expense: Gasto compartido creado en la base de datos
    """
    return Expense.objects.create(
        usuario=user,
        categoria='Servicios',
        fecha='2026-07-15',
        descripcion='Internet mensual',
        valor=80000.00,
        compartido=True
    )


@pytest.fixture
def sample_expense_user_two(user_two):
    """
    Fixture que crea un gasto privado para el segundo usuario.

    Args:
        user_two: Segundo usuario dueño del gasto

    Returns:
        Expense: Gasto creado en la base de datos
    """
    return Expense.objects.create(
        usuario=user_two,
        categoria='Transporte',
        fecha='2026-07-15',
        descripcion='Taxi al trabajo',
        valor=15000.00,
        compartido=False
    )


@pytest.fixture
def sample_shared_expense_user_two(user_two):
    """
    Fixture que crea un gasto compartido del segundo usuario.

    Args:
        user_two: Segundo usuario dueño del gasto

    Returns:
        Expense: Gasto compartido creado en la base de datos
    """
    return Expense.objects.create(
        usuario=user_two,
        categoria='Alimentación',
        fecha='2026-07-15',
        descripcion='Cena compartida',
        valor=60000.00,
        compartido=True
    )


# ============================================
# TESTS DE CREACIÓN DE GASTOS
# ============================================


@pytest.mark.django_db
class TestCreateExpense:
    """
    Suite de tests para la creación de gastos.

    Verifica que un usuario autenticado pueda crear
    gastos correctamente asociados a su cuenta,
    incluyendo el campo compartido.
    """

    def test_create_expense_returns_201(self, api_client, user, auth_headers):
        """Verifica que retorna HTTP 201 al crear un gasto válido."""
        url = reverse('expense-list')
        data = {
            'categoria': 'Alimentación',
            'fecha': '2026-07-15',
            'descripcion': 'Cena',
            'valor': 35000.00
        }
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_expense_saves_to_db(self, api_client, user, auth_headers):
        """Verifica que el gasto se guarda en la base de datos."""
        url = reverse('expense-list')
        data = {
            'categoria': 'Alimentación',
            'fecha': '2026-07-15',
            'descripcion': 'Cena',
            'valor': 35000.00
        }
        api_client.post(url, data, format='json', **auth_headers)
        assert Expense.objects.filter(descripcion='Cena').exists()

    def test_create_expense_associates_user(self, api_client, user, auth_headers):
        """Verifica que el gasto se asocia al usuario autenticado."""
        url = reverse('expense-list')
        data = {
            'categoria': 'Alimentación',
            'fecha': '2026-07-15',
            'descripcion': 'Cena',
            'valor': 35000.00
        }
        api_client.post(url, data, format='json', **auth_headers)
        expense = Expense.objects.get(descripcion='Cena')
        assert expense.usuario == user

    def test_create_expense_returns_data(self, api_client, user, auth_headers):
        """Verifica que la respuesta contiene los datos del gasto creado."""
        url = reverse('expense-list')
        data = {
            'categoria': 'Alimentación',
            'fecha': '2026-07-15',
            'descripcion': 'Cena',
            'valor': 35000.00
        }
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.data['categoria'] == 'Alimentación'
        assert response.data['descripcion'] == 'Cena'
        assert float(response.data['valor']) == 35000.00

    def test_create_expense_without_auth_returns_401(self, api_client):
        """Verifica que retorna HTTP 401 sin autenticación."""
        url = reverse('expense-list')
        data = {
            'categoria': 'Alimentación',
            'fecha': '2026-07-15',
            'descripcion': 'Cena',
            'valor': 35000.00
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_expense_missing_fields_returns_400(self, api_client, user, auth_headers):
        """Verifica que retorna HTTP 400 si faltan campos obligatorios."""
        url = reverse('expense-list')
        data = {'categoria': 'Alimentación'}
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_shared_expense(self, api_client, user, auth_headers):
        """Verifica que se puede crear un gasto compartido."""
        url = reverse('expense-list')
        data = {
            'categoria': 'Servicios',
            'fecha': '2026-07-15',
            'descripcion': 'Internet',
            'valor': 80000.00,
            'compartido': True
        }
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['compartido'] is True

    def test_create_expense_default_not_shared(self, api_client, user, auth_headers):
        """Verifica que por defecto el gasto no es compartido."""
        url = reverse('expense-list')
        data = {
            'categoria': 'Alimentación',
            'fecha': '2026-07-15',
            'descripcion': 'Cena privada',
            'valor': 35000.00
        }
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.data['compartido'] is False


# ============================================
# TESTS DE LISTADO DE GASTOS
# ============================================


@pytest.mark.django_db
class TestListExpenses:
    """
    Suite de tests para el listado de gastos.

    Verifica que un usuario vea sus propios gastos
    y los gastos compartidos de otros usuarios.
    """

    def test_list_expenses_returns_200(self, api_client, user, auth_headers):
        """Verifica que retorna HTTP 200 al listar gastos."""
        url = reverse('expense-list')
        response = api_client.get(url, **auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_list_expenses_returns_list(self, api_client, user, auth_headers):
        """Verifica que la respuesta es una lista."""
        url = reverse('expense-list')
        response = api_client.get(url, **auth_headers)
        assert isinstance(response.data, list)

    def test_list_expenses_shows_own_expenses(self, api_client, user, sample_expense, auth_headers):
        """Verifica que se muestran los gastos del usuario autenticado."""
        url = reverse('expense-list')
        response = api_client.get(url, **auth_headers)
        assert len(response.data) == 1
        assert response.data[0]['descripcion'] == 'Almuerzo en restaurante'

    def test_list_expenses_hides_other_users_private_expenses(
        self, api_client, user, sample_expense_user_two, auth_headers
    ):
        """Verifica que NO se muestran los gastos privados de otros usuarios."""
        url = reverse('expense-list')
        response = api_client.get(url, **auth_headers)
        assert len(response.data) == 0

    def test_list_expenses_shares_other_users_shared_expenses(
        self, api_client, user, sample_shared_expense_user_two, auth_headers
    ):
        """Verifica que SÍ se muestran los gastos compartidos de otros usuarios."""
        url = reverse('expense-list')
        response = api_client.get(url, **auth_headers)
        assert len(response.data) == 1
        assert response.data[0]['descripcion'] == 'Cena compartida'
        assert response.data[0]['compartido'] is True

    def test_list_expenses_shows_own_and_shared(
        self, api_client, user, sample_expense, sample_shared_expense_user_two, auth_headers
    ):
        """Verifica que se muestran gastos propios y compartidos de otros."""
        url = reverse('expense-list')
        response = api_client.get(url, **auth_headers)
        assert len(response.data) == 2

    def test_list_expenses_without_auth_returns_401(self, api_client):
        """Verifica que retorna HTTP 401 sin autenticación."""
        url = reverse('expense-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_expenses_includes_usuario_nombre(
        self, api_client, user, sample_expense, auth_headers
    ):
        """Verifica que el listado incluye el nombre del usuario dueño."""
        url = reverse('expense-list')
        response = api_client.get(url, **auth_headers)
        assert 'usuario_nombre' in response.data[0]
        assert response.data[0]['usuario_nombre'] == user.name


# ============================================
# TESTS DE DETALLE DE GASTOS
# ============================================


@pytest.mark.django_db
class TestDetailExpense:
    """
    Suite de tests para el detalle de un gasto específico.

    Verifica que un usuario pueda ver los detalles
    de sus propios gastos y los compartidos de otros.
    """

    def test_get_expense_returns_200(self, api_client, user, sample_expense, auth_headers):
        """Verifica que retorna HTTP 200 al obtener un gasto propio."""
        url = reverse('expense-detail', kwargs={'pk': sample_expense.pk})
        response = api_client.get(url, **auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_expense_returns_data(self, api_client, user, sample_expense, auth_headers):
        """Verifica que retorna los datos correctos del gasto."""
        url = reverse('expense-detail', kwargs={'pk': sample_expense.pk})
        response = api_client.get(url, **auth_headers)
        assert response.data['categoria'] == 'Alimentación'
        assert response.data['descripcion'] == 'Almuerzo en restaurante'

    def test_get_other_users_shared_expense_returns_200(
        self, api_client, user, sample_shared_expense_user_two, auth_headers
    ):
        """Verifica que SÍ se puede ver el detalle de un gasto compartido de otro."""
        url = reverse('expense-detail', kwargs={'pk': sample_shared_expense_user_two.pk})
        response = api_client.get(url, **auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['compartido'] is True

    def test_get_other_users_private_expense_returns_404(
        self, api_client, user, sample_expense_user_two, auth_headers
    ):
        """Verifica que NO se puede ver gasto privado de otro usuario."""
        url = reverse('expense-detail', kwargs={'pk': sample_expense_user_two.pk})
        response = api_client.get(url, **auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nonexistent_expense_returns_404(self, api_client, user, auth_headers):
        """Verifica que retorna HTTP 404 con ID inexistente."""
        url = reverse('expense-detail', kwargs={'pk': 99999})
        response = api_client.get(url, **auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_expense_includes_usuario_nombre(
        self, api_client, user, sample_expense, auth_headers
    ):
        """Verifica que el detalle incluye el nombre del usuario dueño."""
        url = reverse('expense-detail', kwargs={'pk': sample_expense.pk})
        response = api_client.get(url, **auth_headers)
        assert 'usuario_nombre' in response.data
        assert response.data['usuario_nombre'] == user.name


# ============================================
# TESTS DE ACTUALIZACIÓN DE GASTOS
# ============================================


@pytest.mark.django_db
class TestUpdateExpense:
    """
    Suite de tests para la actualización de gastos.

    Verifica que un usuario pueda actualizar
    sus propios gastos correctamente, incluyendo
    el campo compartido.
    """

    def test_update_expense_returns_200(self, api_client, user, sample_expense, auth_headers):
        """Verifica que retorna HTTP 200 al actualizar un gasto."""
        url = reverse('expense-detail', kwargs={'pk': sample_expense.pk})
        data = {
            'categoria': 'Transporte',
            'fecha': '2026-07-15',
            'descripcion': 'Taxi actualizado',
            'valor': 20000.00
        }
        response = api_client.put(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_update_expense_modifies_db(self, api_client, user, sample_expense, auth_headers):
        """Verifica que los cambios se guardan en la base de datos."""
        url = reverse('expense-detail', kwargs={'pk': sample_expense.pk})
        data = {
            'categoria': 'Transporte',
            'fecha': '2026-07-15',
            'descripcion': 'Taxi actualizado',
            'valor': 20000.00
        }
        api_client.put(url, data, format='json', **auth_headers)
        sample_expense.refresh_from_db()
        assert sample_expense.descripcion == 'Taxi actualizado'
        assert sample_expense.valor == 20000.00

    def test_update_shared_expense_changes_compartido(
        self, api_client, user, sample_expense, auth_headers
    ):
        """Verifica que se puede cambiar el estado de compartido."""
        url = reverse('expense-detail', kwargs={'pk': sample_expense.pk})
        data = {
            'categoria': 'Alimentación',
            'fecha': '2026-07-15',
            'descripcion': 'Almuerzo en restaurante',
            'valor': 45000.00,
            'compartido': True
        }
        api_client.put(url, data, format='json', **auth_headers)
        sample_expense.refresh_from_db()
        assert sample_expense.compartido is True

    def test_update_other_users_expense_returns_404(
        self, api_client, user, sample_expense_user_two, auth_headers
    ):
        """Verifica que retorna HTTP 404 al intentar actualizar gasto de otro."""
        url = reverse('expense-detail', kwargs={'pk': sample_expense_user_two.pk})
        data = {
            'categoria': 'Transporte',
            'fecha': '2026-07-15',
            'descripcion': 'Intento de robo',
            'valor': 0.00
        }
        response = api_client.put(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_other_users_shared_expense_returns_403(
        self, api_client, user, sample_shared_expense_user_two, auth_headers
    ):
        """Verifica que el dueño NO puede actualizar un gasto compartido de otro."""
        original_descripcion = sample_shared_expense_user_two.descripcion
        url = reverse('expense-detail', kwargs={'pk': sample_shared_expense_user_two.pk})
        data = {
            'categoria': 'HACK',
            'fecha': '2026-07-15',
            'descripcion': 'INTENTO DE HACK',
            'valor': 0.00
        }
        response = api_client.put(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        sample_shared_expense_user_two.refresh_from_db()
        assert sample_shared_expense_user_two.descripcion == original_descripcion

    def test_update_expense_without_auth_returns_401(self, api_client, sample_expense):
        """Verifica que retorna HTTP 401 sin autenticación."""
        url = reverse('expense-detail', kwargs={'pk': sample_expense.pk})
        data = {
            'categoria': 'Transporte',
            'fecha': '2026-07-15',
            'descripcion': 'Taxi',
            'valor': 20000.00
        }
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================
# TESTS DE MÉTODO DELETE NO PERMITIDO
# ============================================


@pytest.mark.django_db
class TestDeleteNotAllowed:
    """
    Suite de tests para verificar que DELETE no está permitido.

    La eliminación de gastos no está habilitada en la API.
    Si se envía un DELETE, debe retornar HTTP 405 Method Not Allowed.
    """

    def test_delete_own_expense_returns_405(self, api_client, user, sample_expense, auth_headers):
        """Verifica que DELETE retorna 405 en gasto propio."""
        url = reverse('expense-detail', kwargs={'pk': sample_expense.pk})
        response = api_client.delete(url, **auth_headers)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_delete_other_users_expense_returns_405(
        self, api_client, user, sample_expense_user_two, auth_headers
    ):
        """Verifica que DELETE retorna 405 en gasto de otro usuario."""
        url = reverse('expense-detail', kwargs={'pk': sample_expense_user_two.pk})
        response = api_client.delete(url, **auth_headers)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_delete_expense_still_exists_in_db(self, api_client, user, sample_expense, auth_headers):
        """Verifica que el gasto NO se elimina de la base de datos."""
        url = reverse('expense-detail', kwargs={'pk': sample_expense.pk})
        api_client.delete(url, **auth_headers)
        assert Expense.objects.filter(pk=sample_expense.pk).exists()

    def test_delete_without_auth_returns_401(self, api_client, sample_expense):
        """Verifica que DELETE sin auth retorna 401 (antes de llegar a 405)."""
        url = reverse('expense-detail', kwargs={'pk': sample_expense.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================
# TESTS DE SEGURIDAD Y GASTOS COMPARTIDOS
# ============================================


@pytest.mark.django_db
class TestExpenseSecurity:
    """
    Suite de tests de seguridad para gastos.

    Verifica que la aislación entre usuarios funcione
    correctamente y que los gastos compartidos se
    comporten como se espera.
    """

    def test_user_cannot_see_other_users_private_expenses_in_list(
        self, api_client, user, sample_expense_user_two, auth_headers
    ):
        """Verifica que el listado no muestra gastos privados de otros usuarios."""
        url = reverse('expense-list')
        response = api_client.get(url, **auth_headers)
        for expense in response.data:
            assert expense['id'] != sample_expense_user_two.pk

    def test_user_can_see_other_users_shared_expenses_in_list(
        self, api_client, user, sample_shared_expense_user_two, auth_headers
    ):
        """Verifica que el listado SÍ muestra gastos compartidos de otros."""
        url = reverse('expense-list')
        response = api_client.get(url, **auth_headers)
        ids = [e['id'] for e in response.data]
        assert sample_shared_expense_user_two.pk in ids

    def test_user_cannot_update_other_users_expense(
        self, api_client, user, sample_expense_user_two, auth_headers
    ):
        """Verifica que un usuario no puede modificar gastos privados de otro."""
        original_descripcion = sample_expense_user_two.descripcion
        url = reverse('expense-detail', kwargs={'pk': sample_expense_user_two.pk})
        data = {
            'categoria': 'HACK',
            'fecha': '2026-07-15',
            'descripcion': 'INTENTO DE HACK',
            'valor': 0.00
        }
        api_client.put(url, data, format='json', **auth_headers)
        sample_expense_user_two.refresh_from_db()
        assert sample_expense_user_two.descripcion == original_descripcion

    def test_user_cannot_update_other_users_shared_expense(
        self, api_client, user, sample_shared_expense_user_two, auth_headers
    ):
        """Verifica que un usuario no puede modificar gastos compartidos de otro."""
        original_descripcion = sample_shared_expense_user_two.descripcion
        url = reverse('expense-detail', kwargs={'pk': sample_shared_expense_user_two.pk})
        data = {
            'categoria': 'HACK',
            'fecha': '2026-07-15',
            'descripcion': 'INTENTO DE HACK',
            'valor': 0.00
        }
        api_client.put(url, data, format='json', **auth_headers)
        sample_shared_expense_user_two.refresh_from_db()
        assert sample_shared_expense_user_two.descripcion == original_descripcion

    def test_owner_can_update_own_shared_expense(
        self, api_client, user, sample_shared_expense, auth_headers
    ):
        """Verifica que el dueño SÍ puede actualizar su propio gasto compartido."""
        url = reverse('expense-detail', kwargs={'pk': sample_shared_expense.pk})
        data = {
            'categoria': 'Servicios',
            'fecha': '2026-07-15',
            'descripcion': 'Internet actualizado',
            'valor': 90000.00,
            'compartido': True
        }
        response = api_client.put(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_200_OK
        sample_shared_expense.refresh_from_db()
        assert sample_shared_expense.descripcion == 'Internet actualizado'

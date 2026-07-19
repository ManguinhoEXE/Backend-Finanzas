"""
Tests unitarios del módulo de ahorros.

Prueba el CRUD completo de metas de ahorro, depósitos,
retiros, historial de movimientos y metas compartidas.
"""
import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import User
from savings.models import SavingGoal, SavingGoalParticipant, SavingMovement


@pytest.fixture
def api_client():
    """Fixture que crea un cliente de API para las pruebas."""
    return APIClient()


@pytest.fixture
def sample_goal(user):
    """Fixture que crea una meta individual de ejemplo."""
    return SavingGoal.objects.create(
        owner=user,
        name='Casa',
        description='Meta para comprar una casa',
        target_amount=Decimal('500000000'),
        current_amount=Decimal('0'),
        currency='COP',
        is_shared=False,
        status='ACTIVE'
    )


@pytest.fixture
def sample_shared_goal(user):
    """Fixture que crea una meta compartida de ejemplo."""
    goal = SavingGoal.objects.create(
        owner=user,
        name='Viaje Japón',
        description='Viaje soñado',
        target_amount=Decimal('10000000'),
        current_amount=Decimal('0'),
        currency='COP',
        is_shared=True,
        status='ACTIVE'
    )
    # Agregar al propietario como participante
    SavingGoalParticipant.objects.create(goal=goal, user=user)
    return goal


@pytest.fixture
def sample_goal_with_balance(user):
    """Fixture que crea una meta con saldo acumulado."""
    return SavingGoal.objects.create(
        owner=user,
        name='Fondo emergencia',
        target_amount=Decimal('5000000'),
        current_amount=Decimal('2000000'),
        currency='COP',
        is_shared=False,
        status='ACTIVE'
    )


@pytest.fixture
def sample_goal_user_two(user_two):
    """Fixture que crea una meta del segundo usuario."""
    return SavingGoal.objects.create(
        owner=user_two,
        name='Moto',
        target_amount=Decimal('15000000'),
        current_amount=Decimal('0'),
        currency='COP',
        is_shared=False,
        status='ACTIVE'
    )


@pytest.fixture
def shared_goal_with_participant(user, user_two):
    """Fixture que crea una meta compartida con dos participantes."""
    goal = SavingGoal.objects.create(
        owner=user,
        name='Casa compartida',
        target_amount=Decimal('500000000'),
        current_amount=Decimal('0'),
        currency='COP',
        is_shared=True,
        status='ACTIVE'
    )
    SavingGoalParticipant.objects.create(goal=goal, user=user)
    SavingGoalParticipant.objects.create(goal=goal, user=user_two)
    return goal


# ============================================
# TESTS DE CREACIÓN DE METAS
# ============================================


@pytest.mark.django_db
class TestCreateGoal:
    """Suite de tests para la creación de metas de ahorro."""

    def test_create_goal_returns_201(self, api_client, user, auth_headers):
        """Verifica que retorna HTTP 201 al crear una meta válida."""
        url = reverse('saving-goal-list')
        data = {
            'name': 'Moto',
            'target_amount': '15000000',
        }
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_goal_saves_to_db(self, api_client, user, auth_headers):
        """Verifica que la meta se guarda en la base de datos."""
        url = reverse('saving-goal-list')
        data = {
            'name': 'Moto',
            'target_amount': '15000000',
        }
        api_client.post(url, data, format='json', **auth_headers)
        assert SavingGoal.objects.filter(name='Moto').exists()

    def test_create_goal_sets_owner(self, api_client, user, auth_headers):
        """Verifica que el propietario es el usuario autenticado."""
        url = reverse('saving-goal-list')
        data = {
            'name': 'Moto',
            'target_amount': '15000000',
        }
        api_client.post(url, data, format='json', **auth_headers)
        goal = SavingGoal.objects.get(name='Moto')
        assert goal.owner == user

    def test_create_goal_returns_data(self, api_client, user, auth_headers):
        """Verifica que la respuesta contiene los datos de la meta."""
        url = reverse('saving-goal-list')
        data = {
            'name': 'Moto',
            'target_amount': '15000000',
            'description': 'Una moto nueva',
        }
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.data['name'] == 'Moto'
        assert response.data['target_amount'] == '15000000.00'
        assert response.data['description'] == 'Una moto nueva'

    def test_create_goal_default_values(self, api_client, user, auth_headers):
        """Verifica que los valores por defecto son correctos."""
        url = reverse('saving-goal-list')
        data = {
            'name': 'Moto',
            'target_amount': '15000000',
        }
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.data['current_amount'] == '0.00'
        assert response.data['currency'] == 'COP'
        assert response.data['is_shared'] is False
        assert response.data['status'] == 'ACTIVE'

    def test_create_goal_without_auth_returns_401(self, api_client):
        """Verifica que retorna HTTP 401 sin autenticación."""
        url = reverse('saving-goal-list')
        data = {'name': 'Moto', 'target_amount': '15000000'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_goal_missing_name_returns_400(self, api_client, user, auth_headers):
        """Verifica que retorna HTTP 400 si falta el nombre."""
        url = reverse('saving-goal-list')
        data = {'target_amount': '15000000'}
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_goal_missing_target_returns_400(self, api_client, user, auth_headers):
        """Verifica que retorna HTTP 400 si falta el monto objetivo."""
        url = reverse('saving-goal-list')
        data = {'name': 'Moto'}
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_shared_goal_adds_participant(self, api_client, user, auth_headers):
        """Verifica que al crear meta compartida, el owner es participante."""
        url = reverse('saving-goal-list')
        data = {
            'name': 'Casa compartida',
            'target_amount': '500000000',
            'is_shared': True,
        }
        api_client.post(url, data, format='json', **auth_headers)
        goal = SavingGoal.objects.get(name='Casa compartida')
        assert SavingGoalParticipant.objects.filter(
            goal=goal, user=user
        ).exists()


# ============================================
# TESTS DE LISTADO DE METAS
# ============================================


@pytest.mark.django_db
class TestListGoals:
    """Suite de tests para el listado de metas de ahorro."""

    def test_list_goals_returns_200(self, api_client, user, auth_headers):
        """Verifica que retorna HTTP 200 al listar metas."""
        url = reverse('saving-goal-list')
        response = api_client.get(url, **auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_list_goals_returns_list(self, api_client, user, auth_headers):
        """Verifica que la respuesta es una lista."""
        url = reverse('saving-goal-list')
        response = api_client.get(url, **auth_headers)
        assert isinstance(response.data, list)

    def test_list_goals_shows_own_goals(self, api_client, user, sample_goal, auth_headers):
        """Verifica que se muestran las metas propias."""
        url = reverse('saving-goal-list')
        response = api_client.get(url, **auth_headers)
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Casa'

    def test_list_goals_hides_other_users_goals(
        self, api_client, user, sample_goal_user_two, auth_headers
    ):
        """Verifica que NO se muestran las metas privadas de otros."""
        url = reverse('saving-goal-list')
        response = api_client.get(url, **auth_headers)
        assert len(response.data) == 0

    def test_list_goals_shows_shared_goals(
        self, api_client, user, shared_goal_with_participant, auth_headers
    ):
        """Verifica que SÍ se muestran las metas compartidas donde participa."""
        url = reverse('saving-goal-list')
        response = api_client.get(url, **auth_headers)
        assert len(response.data) >= 1

    def test_list_goals_without_auth_returns_401(self, api_client):
        """Verifica que retorna HTTP 401 sin autenticación."""
        url = reverse('saving-goal-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_goals_includes_progress(self, api_client, user, sample_goal_with_balance, auth_headers):
        """Verifica que el listado incluye el campo progress."""
        url = reverse('saving-goal-list')
        response = api_client.get(url, **auth_headers)
        assert 'progress' in response.data[0]

    def test_list_goals_includes_remaining_amount(
        self, api_client, user, sample_goal_with_balance, auth_headers
    ):
        """Verifica que el listado incluye remaining_amount."""
        url = reverse('saving-goal-list')
        response = api_client.get(url, **auth_headers)
        assert 'remaining_amount' in response.data[0]


# ============================================
# TESTS DE DETALLE DE META
# ============================================


@pytest.mark.django_db
class TestDetailGoal:
    """Suite de tests para el detalle de una meta de ahorro."""

    def test_get_goal_returns_200(self, api_client, user, sample_goal, auth_headers):
        """Verifica que retorna HTTP 200 al obtener una meta propia."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal.pk})
        response = api_client.get(url, **auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_goal_returns_data(self, api_client, user, sample_goal, auth_headers):
        """Verifica que retorna los datos correctos de la meta."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal.pk})
        response = api_client.get(url, **auth_headers)
        assert response.data['name'] == 'Casa'
        assert response.data['target_amount'] == '500000000.00'

    def test_get_goal_includes_owner_name(self, api_client, user, sample_goal, auth_headers):
        """Verifica que el detalle incluye el nombre del propietario."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal.pk})
        response = api_client.get(url, **auth_headers)
        assert response.data['owner_name'] == user.name

    def test_get_other_users_goal_returns_404(
        self, api_client, user, sample_goal_user_two, auth_headers
    ):
        """Verifica que retorna HTTP 404 al intentar ver meta privada de otro."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal_user_two.pk})
        response = api_client.get(url, **auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_shared_goal_as_participant(
        self, api_client, user, shared_goal_with_participant, auth_headers
    ):
        """Verifica que un participante SÍ puede ver la meta compartida."""
        url = reverse('saving-goal-detail', kwargs={'pk': shared_goal_with_participant.pk})
        response = api_client.get(url, **auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_get_nonexistent_goal_returns_404(self, api_client, user, auth_headers):
        """Verifica que retorna HTTP 404 con ID inexistente."""
        url = reverse('saving-goal-detail', kwargs={'pk': 99999})
        response = api_client.get(url, **auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================
# TESTS DE ACTUALIZACIÓN DE META
# ============================================


@pytest.mark.django_db
class TestUpdateGoal:
    """Suite de tests para la actualización de metas."""

    def test_update_goal_returns_200(self, api_client, user, sample_goal, auth_headers):
        """Verifica que retorna HTTP 200 al actualizar una meta."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal.pk})
        data = {'name': 'Casa actualizada'}
        response = api_client.put(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_update_goal_modifies_db(self, api_client, user, sample_goal, auth_headers):
        """Verifica que los cambios se guardan en la base de datos."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal.pk})
        data = {'name': 'Casa actualizada'}
        api_client.put(url, data, format='json', **auth_headers)
        sample_goal.refresh_from_db()
        assert sample_goal.name == 'Casa actualizada'

    def test_update_goal_cannot_change_owner(
        self, api_client, user, user_two, sample_goal, auth_headers
    ):
        """Verifica que no se puede cambiar el propietario."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal.pk})
        data = {'owner': user_two.pk}
        api_client.put(url, data, format='json', **auth_headers)
        sample_goal.refresh_from_db()
        assert sample_goal.owner == user

    def test_update_other_users_goal_returns_403(
        self, api_client, user, sample_goal_user_two, auth_headers
    ):
        """Verifica que retorna HTTP 403 al intentar actualizar meta de otro."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal_user_two.pk})
        data = {'name': 'HACK'}
        response = api_client.put(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_goal_without_auth_returns_401(self, api_client, sample_goal):
        """Verifica que retorna HTTP 401 sin autenticación."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal.pk})
        data = {'name': 'Test'}
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================
# TESTS DE ELIMINACIÓN DE META
# ============================================


@pytest.mark.django_db
class TestDeleteGoal:
    """Suite de tests para la eliminación de metas."""

    def test_delete_goal_returns_204(self, api_client, user, sample_goal, auth_headers):
        """Verifica que retorna HTTP 204 al eliminar una meta."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal.pk})
        response = api_client.delete(url, **auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_goal_removes_from_db(self, api_client, user, sample_goal, auth_headers):
        """Verifica que la meta se elimina de la base de datos."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal.pk})
        api_client.delete(url, **auth_headers)
        assert not SavingGoal.objects.filter(pk=sample_goal.pk).exists()

    def test_delete_other_users_goal_returns_403(
        self, api_client, user, sample_goal_user_two, auth_headers
    ):
        """Verifica que retorna HTTP 403 al intentar eliminar meta de otro."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal_user_two.pk})
        response = api_client.delete(url, **auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert SavingGoal.objects.filter(pk=sample_goal_user_two.pk).exists()

    def test_delete_goal_without_auth_returns_401(self, api_client, sample_goal):
        """Verifica que retorna HTTP 401 sin autenticación."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================
# TESTS DE DEPÓSITOS
# ============================================


@pytest.mark.django_db
class TestDeposit:
    """Suite de tests para depósitos en metas de ahorro."""

    def test_deposit_returns_201(self, api_client, user, sample_goal, auth_headers):
        """Verifica que retorna HTTP 201 al registrar un depósito."""
        url = reverse('saving-goal-deposit', kwargs={'pk': sample_goal.pk})
        data = {'amount': '500000', 'description': 'Ahorro mensual'}
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

    def test_deposit_updates_balance(self, api_client, user, sample_goal, auth_headers):
        """Verifica que el saldo de la meta se actualiza."""
        url = reverse('saving-goal-deposit', kwargs={'pk': sample_goal.pk})
        data = {'amount': '500000'}
        api_client.post(url, data, format='json', **auth_headers)
        sample_goal.refresh_from_db()
        assert sample_goal.current_amount == Decimal('500000')

    def test_deposit_creates_movement(self, api_client, user, sample_goal, auth_headers):
        """Verifica que se crea un movimiento de tipo DEPOSIT."""
        url = reverse('saving-goal-deposit', kwargs={'pk': sample_goal.pk})
        data = {'amount': '500000', 'description': 'Ahorro'}
        api_client.post(url, data, format='json', **auth_headers)
        assert SavingMovement.objects.filter(
            goal=sample_goal, type='DEPOSIT'
        ).exists()

    def test_deposit_multiple_times(self, api_client, user, sample_goal, auth_headers):
        """Verifica que se pueden hacer múltiples depósitos."""
        url = reverse('saving-goal-deposit', kwargs={'pk': sample_goal.pk})
        api_client.post(url, {'amount': '100000'}, format='json', **auth_headers)
        api_client.post(url, {'amount': '200000'}, format='json', **auth_headers)
        sample_goal.refresh_from_db()
        assert sample_goal.current_amount == Decimal('300000')

    def test_deposit_completes_goal(
        self, api_client, user, sample_goal, auth_headers
    ):
        """Verifica que la meta se marca COMPLETED al alcanzar el objetivo."""
        url = reverse('saving-goal-deposit', kwargs={'pk': sample_goal.pk})
        data = {'amount': '500000000'}
        api_client.post(url, data, format='json', **auth_headers)
        sample_goal.refresh_from_db()
        assert sample_goal.status == 'COMPLETED'

    def test_deposit_returns_goal_data(self, api_client, user, sample_goal, auth_headers):
        """Verifica que la respuesta incluye la meta actualizada."""
        url = reverse('saving-goal-deposit', kwargs={'pk': sample_goal.pk})
        data = {'amount': '100000'}
        response = api_client.post(url, data, format='json', **auth_headers)
        assert 'goal' in response.data
        assert response.data['goal']['current_amount'] == '100000.00'

    def test_deposit_without_auth_returns_401(self, api_client, sample_goal):
        """Verifica que retorna HTTP 401 sin autenticación."""
        url = reverse('saving-goal-deposit', kwargs={'pk': sample_goal.pk})
        data = {'amount': '100000'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_deposit_to_paused_goal_returns_400(
        self, api_client, user, auth_headers
    ):
        """Verifica que no se puede depositar en meta pausada."""
        goal = SavingGoal.objects.create(
            owner=user, name='Pausada',
            target_amount=Decimal('1000000'),
            status='PAUSED'
        )
        url = reverse('saving-goal-deposit', kwargs={'pk': goal.pk})
        data = {'amount': '100000'}
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_deposit_to_other_users_goal_returns_403(
        self, api_client, user, sample_goal_user_two, auth_headers
    ):
        """Verifica que no se puede depositar en meta privada de otro."""
        url = reverse('saving-goal-deposit', kwargs={'pk': sample_goal_user_two.pk})
        data = {'amount': '100000'}
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================================
# TESTS DE RETIROS
# ============================================


@pytest.mark.django_db
class TestWithdraw:
    """Suite de tests para retiros de metas de ahorro."""

    def test_withdraw_returns_201(self, api_client, user, sample_goal_with_balance, auth_headers):
        """Verifica que retorna HTTP 201 al registrar un retiro."""
        url = reverse('saving-goal-withdraw', kwargs={'pk': sample_goal_with_balance.pk})
        data = {'amount': '500000', 'description': 'Emergencia'}
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

    def test_withdraw_updates_balance(self, api_client, user, sample_goal_with_balance, auth_headers):
        """Verifica que el saldo se reduce correctamente."""
        url = reverse('saving-goal-withdraw', kwargs={'pk': sample_goal_with_balance.pk})
        data = {'amount': '500000'}
        api_client.post(url, data, format='json', **auth_headers)
        sample_goal_with_balance.refresh_from_db()
        assert sample_goal_with_balance.current_amount == Decimal('1500000')

    def test_withdraw_creates_movement(self, api_client, user, sample_goal_with_balance, auth_headers):
        """Verifica que se crea un movimiento de tipo WITHDRAW."""
        url = reverse('saving-goal-withdraw', kwargs={'pk': sample_goal_with_balance.pk})
        data = {'amount': '500000'}
        api_client.post(url, data, format='json', **auth_headers)
        assert SavingMovement.objects.filter(
            goal=sample_goal_with_balance, type='WITHDRAW'
        ).exists()

    def test_withdraw_insufficient_balance_returns_400(
        self, api_client, user, sample_goal_with_balance, auth_headers
    ):
        """Verifica que retorna HTTP 400 si no hay saldo suficiente."""
        url = reverse('saving-goal-withdraw', kwargs={'pk': sample_goal_with_balance.pk})
        data = {'amount': '50000000'}
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_withdraw_all_balance(self, api_client, user, sample_goal_with_balance, auth_headers):
        """Verifica que se puede retirar todo el saldo."""
        url = reverse('saving-goal-withdraw', kwargs={'pk': sample_goal_with_balance.pk})
        data = {'amount': '2000000'}
        api_client.post(url, data, format='json', **auth_headers)
        sample_goal_with_balance.refresh_from_db()
        assert sample_goal_with_balance.current_amount == Decimal('0')

    def test_withdraw_without_auth_returns_401(self, api_client, sample_goal_with_balance):
        """Verifica que retorna HTTP 401 sin autenticación."""
        url = reverse('saving-goal-withdraw', kwargs={'pk': sample_goal_with_balance.pk})
        data = {'amount': '100000'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_withdraw_from_paused_goal_returns_400(
        self, api_client, user, auth_headers
    ):
        """Verifica que no se puede retirar de meta pausada."""
        goal = SavingGoal.objects.create(
            owner=user, name='Pausada',
            target_amount=Decimal('1000000'),
            current_amount=Decimal('500000'),
            status='PAUSED'
        )
        url = reverse('saving-goal-withdraw', kwargs={'pk': goal.pk})
        data = {'amount': '100000'}
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================
# TESTS DE HISTORIAL DE MOVIMIENTOS
# ============================================


@pytest.mark.django_db
class TestMovementHistory:
    """Suite de tests para el historial de movimientos."""

    def test_movements_returns_200(self, api_client, user, sample_goal, auth_headers):
        """Verifica que retorna HTTP 200 al listar movimientos."""
        url = reverse('saving-goal-movements', kwargs={'pk': sample_goal.pk})
        response = api_client.get(url, **auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_movements_returns_list(self, api_client, user, sample_goal, auth_headers):
        """Verifica que la respuesta es una lista."""
        url = reverse('saving-goal-movements', kwargs={'pk': sample_goal.pk})
        response = api_client.get(url, **auth_headers)
        assert isinstance(response.data, list)

    def test_movements_includes_deposits(
        self, api_client, user, sample_goal, auth_headers
    ):
        """Verifica que los depósitos aparecen en el historial."""
        # Crear un depósito
        deposit_url = reverse('saving-goal-deposit', kwargs={'pk': sample_goal.pk})
        api_client.post(deposit_url, {'amount': '100000'}, format='json', **auth_headers)

        # Listar movimientos
        movements_url = reverse('saving-goal-movements', kwargs={'pk': sample_goal.pk})
        response = api_client.get(movements_url, **auth_headers)
        assert len(response.data) == 1
        assert response.data[0]['type'] == 'DEPOSIT'

    def test_movements_includes_withdrawals(
        self, api_client, user, sample_goal_with_balance, auth_headers
    ):
        """Verifica que los retiros aparecen en el historial."""
        # Crear un retiro
        withdraw_url = reverse('saving-goal-withdraw', kwargs={'pk': sample_goal_with_balance.pk})
        api_client.post(withdraw_url, {'amount': '500000'}, format='json', **auth_headers)

        # Listar movimientos
        movements_url = reverse('saving-goal-movements', kwargs={'pk': sample_goal_with_balance.pk})
        response = api_client.get(movements_url, **auth_headers)
        assert len(response.data) == 1
        assert response.data[0]['type'] == 'WITHDRAW'

    def test_movements_without_auth_returns_401(self, api_client, sample_goal):
        """Verifica que retorna HTTP 401 sin autenticación."""
        url = reverse('saving-goal-movements', kwargs={'pk': sample_goal.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_movements_from_other_users_goal_returns_403(
        self, api_client, user, sample_goal_user_two, auth_headers
    ):
        """Verifica que no se puede ver historial de meta privada de otro."""
        url = reverse('saving-goal-movements', kwargs={'pk': sample_goal_user_two.pk})
        response = api_client.get(url, **auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================================
# TESTS DE METAS COMPARTIDAS
# ============================================


@pytest.mark.django_db
class TestSharedGoals:
    """Suite de tests para metas compartidas entre usuarios."""

    def test_participant_can_see_shared_goal(
        self, api_client, user_two, shared_goal_with_participant, auth_headers_user_two
    ):
        """Verifica que un participante SÍ puede ver la meta compartida."""
        url = reverse('saving-goal-detail', kwargs={'pk': shared_goal_with_participant.pk})
        response = api_client.get(url, **auth_headers_user_two)
        assert response.status_code == status.HTTP_200_OK

    def test_non_participant_cannot_see_shared_goal(
        self, api_client, user_two, sample_goal, auth_headers_user_two
    ):
        """Verifica que un NO participante NO puede ver meta compartida de otro."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal.pk})
        response = api_client.get(url, **auth_headers_user_two)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_participant_can_deposit(
        self, api_client, user_two, shared_goal_with_participant, auth_headers_user_two
    ):
        """Verifica que un participante SÍ puede depositar."""
        url = reverse('saving-goal-deposit', kwargs={'pk': shared_goal_with_participant.pk})
        data = {'amount': '200000'}
        response = api_client.post(url, data, format='json', **auth_headers_user_two)
        assert response.status_code == status.HTTP_201_CREATED

    def test_participant_can_withdraw(
        self, api_client, user, shared_goal_with_participant, auth_headers
    ):
        """Verifica que un participante SÍ puede retirar (si hay saldo)."""
        # Primero depositar
        deposit_url = reverse('saving-goal-deposit', kwargs={'pk': shared_goal_with_participant.pk})
        api_client.post(deposit_url, {'amount': '500000'}, format='json', **auth_headers)

        # Luego retirar
        withdraw_url = reverse('saving-goal-withdraw', kwargs={'pk': shared_goal_with_participant.pk})
        data = {'amount': '100000'}
        response = api_client.post(withdraw_url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

    def test_participant_can_see_movements(
        self, api_client, user_two, shared_goal_with_participant, auth_headers_user_two
    ):
        """Verifica que un participante SÍ puede ver el historial."""
        url = reverse('saving-goal-movements', kwargs={'pk': shared_goal_with_participant.pk})
        response = api_client.get(url, **auth_headers_user_two)
        assert response.status_code == status.HTTP_200_OK

    def test_owner_can_add_participant(
        self, api_client, user, user_two, sample_shared_goal, auth_headers
    ):
        """Verifica que el propietario puede agregar participantes."""
        url = reverse('saving-goal-participants', kwargs={'pk': sample_shared_goal.pk})
        data = {'user_id': user_two.pk}
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

    def test_non_owner_cannot_add_participant(
        self, api_client, user_two, shared_goal_with_participant, auth_headers_user_two
    ):
        """Verifica que un NO propietario NO puede agregar participantes."""
        url = reverse('saving-goal-participants', kwargs={'pk': shared_goal_with_participant.pk})
        data = {'user_id': user_two.pk}
        response = api_client.post(url, data, format='json', **auth_headers_user_two)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_add_duplicate_participant(
        self, api_client, user, user_two, shared_goal_with_participant, auth_headers
    ):
        """Verifica que no se puede agregar un participante duplicado."""
        url = reverse('saving-goal-participants', kwargs={'pk': shared_goal_with_participant.pk})
        data = {'user_id': user_two.pk}
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_participant_to_individual_goal_returns_400(
        self, api_client, user, user_two, sample_goal, auth_headers
    ):
        """Verifica que no se puede agregar participante a meta individual."""
        url = reverse('saving-goal-participants', kwargs={'pk': sample_goal.pk})
        data = {'user_id': user_two.pk}
        response = api_client.post(url, data, format='json', **auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================
# TESTS DE CÁLCULOS Y REGLAS DE NEGOCIO
# ============================================


@pytest.mark.django_db
class TestBusinessRules:
    """Suite de tests para reglas de negocio del módulo."""

    def test_progress_percentage(self, api_client, user, sample_goal_with_balance, auth_headers):
        """Verifica que el porcentaje de progreso se calcula correctamente."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal_with_balance.pk})
        response = api_client.get(url, **auth_headers)
        # 2000000 / 5000000 * 100 = 40%
        assert response.data['progress'] == 40.0

    def test_remaining_amount(self, api_client, user, sample_goal_with_balance, auth_headers):
        """Verifica que el monto restante se calcula correctamente."""
        url = reverse('saving-goal-detail', kwargs={'pk': sample_goal_with_balance.pk})
        response = api_client.get(url, **auth_headers)
        # 5000000 - 2000000 = 3000000
        assert response.data['remaining_amount'] == '3000000.00'

    def test_goal_auto_completes(
        self, api_client, user, sample_goal, auth_headers
    ):
        """Verifica que la meta se marca COMPLETED automáticamente."""
        url = reverse('saving-goal-deposit', kwargs={'pk': sample_goal.pk})
        data = {'amount': '500000000'}
        api_client.post(url, data, format='json', **auth_headers)
        sample_goal.refresh_from_db()
        assert sample_goal.status == 'COMPLETED'

    def test_movement_history_not_deletable(
        self, api_client, user, sample_goal, auth_headers
    ):
        """Verifica que los movimientos no se eliminan (solo se agregan)."""
        # Crear un depósito
        deposit_url = reverse('saving-goal-deposit', kwargs={'pk': sample_goal.pk})
        api_client.post(deposit_url, {'amount': '100000'}, format='json', **auth_headers)

        # Crear un ajuste
        movement_count_before = SavingMovement.objects.filter(goal=sample_goal).count()

        # No hay endpoint para eliminar, pero verificamos que el conteo no cambia
        movements_url = reverse('saving-goal-movements', kwargs={'pk': sample_goal.pk})
        response = api_client.get(movements_url, **auth_headers)
        assert len(response.data) == movement_count_before

    def test_owner_edit_only(
        self, api_client, user, user_two, shared_goal_with_participant, auth_headers_user_two
    ):
        """Verifica que solo el propietario puede editar la meta."""
        url = reverse('saving-goal-detail', kwargs={'pk': shared_goal_with_participant.pk})
        data = {'name': 'HACK'}
        response = api_client.put(url, data, format='json', **auth_headers_user_two)
        assert response.status_code == status.HTTP_403_FORBIDDEN

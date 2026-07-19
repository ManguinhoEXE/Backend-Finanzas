"""
Vistas del módulo de ahorros.

Define las vistas para el CRUD de metas, depósitos,
retiros y historial de movimientos.
"""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SavingGoal, SavingGoalParticipant, SavingMovement
from .permissions import IsGoalOwner, IsGoalParticipant
from .serializers import (
    DepositWithdrawSerializer,
    SavingGoalParticipantSerializer,
    SavingGoalSerializer,
    SavingMovementSerializer,
)


class SavingGoalListCreateView(APIView):
    """
    Vista para listar y crear metas de ahorro.

    GET /api/savings/goals/
        - Lista metas propias + metas compartidas donde participa
    POST /api/savings/goals/
        - Crea una nueva meta (el usuario es el propietario)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retorna las metas del usuario autenticado.
        Incluye metas propias y metas compartidas donde participa.
        """
        usuario = request.user

        # Metas propias + metas compartidas donde es participante
        goals = SavingGoal.objects.filter(
            Q(owner=usuario) | Q(is_shared=True)
        ).distinct()

        serializer = SavingGoalSerializer(goals, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Crea una nueva meta de ahorro.
        El propietario es el usuario autenticado.
        """
        serializer = SavingGoalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Crear la meta con el propietario actual
        goal = serializer.save(owner=request.user)

        # Si es compartida, agregar a todos los demás usuarios como participantes
        if goal.is_shared:
            from authentication.models import User
            other_users = User.objects.exclude(pk=request.user.pk)
            for user in other_users:
                SavingGoalParticipant.objects.create(goal=goal, user=user)

        return Response(
            SavingGoalSerializer(goal).data,
            status=status.HTTP_201_CREATED
        )


class SavingGoalDetailView(APIView):
    """
    Vista para ver, actualizar y eliminar una meta de ahorro.

    GET /api/savings/goals/{id}/
        - Detalle de una meta (propietario o participante)
    PUT /api/savings/goals/{id}/
        - Actualizar meta (solo propietario)
    DELETE /api/savings/goals/{id}/
        - Eliminar meta (solo propietario)
    """
    permission_classes = [IsAuthenticated, IsGoalOwner]

    def get_object(self, pk):
        """
        Obtiene la meta por ID con permisos verificados.

        Para GET: si el usuario no tiene permiso, retorna 404
        para ocultar la existencia de la meta.
        Para PUT/DELETE: retorna 403 (PermissionDenied normal).

        Args:
            pk: ID de la meta

        Returns:
            SavingGoal: Meta encontrada
        """
        from django.http import Http404
        from rest_framework.exceptions import PermissionDenied
        goal = get_object_or_404(SavingGoal, pk=pk)
        try:
            self.check_object_permissions(self.request, goal)
        except PermissionDenied:
            if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
                raise Http404
            raise
        return goal

    def get(self, request, pk):
        """Retorna el detalle de una meta."""
        goal = self.get_object(pk)
        serializer = SavingGoalSerializer(goal)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Actualiza una meta de ahorro.
        Solo el propietario puede actualizar.
        """
        goal = self.get_object(pk)
        serializer = SavingGoalSerializer(
            goal,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        # No permitir cambiar el propietario ni el monto actual directamente
        if 'owner' in serializer.validated_data:
            del serializer.validated_data['owner']
        if 'current_amount' in serializer.validated_data:
            del serializer.validated_data['current_amount']

        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        """
        Elimina una meta de ahorro.
        Solo el propietario puede eliminar.
        """
        goal = self.get_object(pk)
        goal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DepositView(APIView):
    """
    Vista para registrar un depósito en una meta.

    POST /api/savings/goals/{id}/deposit/
        - Registra un depósito y actualiza el saldo
    """
    permission_classes = [IsAuthenticated, IsGoalParticipant]

    def post(self, request, pk):
        """
        Registra un depósito en la meta.

        El monto se suma al current_amount de la meta.
        Si current_amount >= target_amount, la meta se marca COMPLETED.
        """
        goal = get_object_or_404(SavingGoal, pk=pk)
        self.check_object_permissions(request, goal)

        # Verificar que la meta esté activa
        if goal.status != 'ACTIVE':
            return Response(
                {'detail': 'No se pueden registrar depósitos en una meta que no está activa.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar datos del depósito
        serializer = DepositWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', '')

        # Crear el movimiento de depósito
        movement = SavingMovement.objects.create(
            goal=goal,
            user=request.user,
            type='DEPOSIT',
            amount=amount,
            description=description
        )

        # Actualizar el saldo de la meta
        goal.current_amount += amount
        goal.save(update_fields=['current_amount', 'updated_at'])

        # Verificar si la meta se completó
        goal.update_status()

        return Response({
            'detail': 'Depósito registrado exitosamente.',
            'movement': SavingMovementSerializer(movement).data,
            'goal': SavingGoalSerializer(goal).data,
        }, status=status.HTTP_201_CREATED)


class WithdrawView(APIView):
    """
    Vista para registrar un retiro en una meta.

    POST /api/savings/goals/{id}/withdraw/
        - Registra un retiro y actualiza el saldo
    """
    permission_classes = [IsAuthenticated, IsGoalParticipant]

    def post(self, request, pk):
        """
        Registra un retiro de la meta.

        El monto se resta al current_amount de la meta.
        No se permiten retiros que dejen el saldo negativo.
        """
        goal = get_object_or_404(SavingGoal, pk=pk)
        self.check_object_permissions(request, goal)

        # Verificar que la meta esté activa
        if goal.status != 'ACTIVE':
            return Response(
                {'detail': 'No se pueden registrar retiros en una meta que no está activa.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar datos del retiro
        serializer = DepositWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', '')

        # Verificar que haya saldo suficiente
        if amount > goal.current_amount:
            return Response(
                {'detail': 'Saldo insuficiente para realizar este retiro.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear el movimiento de retiro
        movement = SavingMovement.objects.create(
            goal=goal,
            user=request.user,
            type='WITHDRAW',
            amount=amount,
            description=description
        )

        # Actualizar el saldo de la meta
        goal.current_amount -= amount
        goal.save(update_fields=['current_amount', 'updated_at'])

        return Response({
            'detail': 'Retiro registrado exitosamente.',
            'movement': SavingMovementSerializer(movement).data,
            'goal': SavingGoalSerializer(goal).data,
        }, status=status.HTTP_201_CREATED)


class MovementListView(APIView):
    """
    Vista para listar el historial de movimientos de una meta.

    GET /api/savings/goals/{id}/movements/
        - Lista todos los movimientos de la meta
    """
    permission_classes = [IsAuthenticated, IsGoalParticipant]

    def get(self, request, pk):
        """
        Retorna el historial de movimientos de la meta.
        Solo el propietario o participantes pueden ver el historial.
        """
        goal = get_object_or_404(SavingGoal, pk=pk)
        self.check_object_permissions(request, goal)

        # Obtener todos los movimientos de la meta
        movements = SavingMovement.objects.filter(goal=goal)

        serializer = SavingMovementSerializer(movements, many=True)
        return Response(serializer.data)


class AddParticipantView(APIView):
    """
    Vista para agregar un participante a una meta compartida.

    POST /api/savings/goals/{id}/participants/
        - Agrega un usuario como participante
    """
    permission_classes = [IsAuthenticated, IsGoalOwner]

    def post(self, request, pk):
        """
        Agrega un participante a la meta.
        Solo el propietario puede agregar participantes.
        La meta debe ser compartida.
        """
        goal = get_object_or_404(SavingGoal, pk=pk)
        self.check_object_permissions(request, goal)

        # Verificar que la meta sea compartida
        if not goal.is_shared:
            return Response(
                {'detail': 'Solo se pueden agregar participantes a metas compartidas.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener el ID del usuario a agregar
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'detail': 'El campo user_id es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar que el usuario exista
        from authentication.models import User
        try:
            user_to_add = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'El usuario especificado no existe.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar que el usuario no sea ya participante
        if SavingGoalParticipant.objects.filter(goal=goal, user=user_to_add).exists():
            return Response(
                {'detail': 'El usuario ya es participante de esta meta.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear la participación
        participant = SavingGoalParticipant.objects.create(
            goal=goal,
            user=user_to_add
        )

        return Response(
            SavingGoalParticipantSerializer(participant).data,
            status=status.HTTP_201_CREATED
        )

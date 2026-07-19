"""
Serializers del módulo de ahorros.

Define la estructura de datos para metas, movimientos
y participantes de ahorro.
"""
from rest_framework import serializers

from .models import SavingGoal, SavingGoalParticipant, SavingMovement


class SavingGoalSerializer(serializers.ModelSerializer):
    """
    Serializer para metas de ahorro.

    Incluye campos calculados de progreso y información
    del propietario. El campo current_amount se actualiza
    automáticamente desde los movimientos.
    """
    # Nombre del propietario (solo lectura)
    owner_name = serializers.CharField(
        source='owner.name',
        read_only=True
    )

    # Monto restante calculado (solo lectura)
    remaining_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )

    # Porcentaje de progreso calculado (solo lectura)
    progress = serializers.SerializerMethodField()

    # Cantidad de participantes (solo para metas compartidas)
    participants_count = serializers.SerializerMethodField()

    class Meta:
        """Configuración del serializer."""
        model = SavingGoal
        fields = [
            'id',
            'owner_name',
            'name',
            'description',
            'target_amount',
            'current_amount',
            'remaining_amount',
            'currency',
            'deadline',
            'is_shared',
            'status',
            'progress',
            'participants_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'owner_name',
            'current_amount',
            'remaining_amount',
            'progress',
            'participants_count',
            'created_at',
            'updated_at',
        ]

    def get_progress(self, obj):
        """
        Calcula el porcentaje de progreso de la meta.

        Args:
            obj: Instancia de SavingGoal

        Returns:
            float: Porcentaje de progreso (0-100)
        """
        return round(obj.progress_percentage, 1)

    def get_participants_count(self, obj):
        """
        Retorna la cantidad de participantes de la meta.

        Args:
            obj: Instancia de SavingGoal

        Returns:
            int: Cantidad de participantes
        """
        return obj.participants.count()


class SavingMovementSerializer(serializers.ModelSerializer):
    """
    Serializer para movimientos de ahorro.

    Serializa la información de cada depósito, retiro
    o ajuste registrado en una meta.
    """
    # Nombre del usuario que realizó el movimiento
    user_name = serializers.CharField(
        source='user.name',
        read_only=True
    )

    class Meta:
        """Configuración del serializer."""
        model = SavingMovement
        fields = [
            'id',
            'user_name',
            'type',
            'amount',
            'description',
            'created_at',
        ]
        read_only_fields = ['id', 'user_name', 'created_at']


class DepositWithdrawSerializer(serializers.Serializer):
    """
    Serializer para depósitos y retiros.

    Valida el monto y la descripción del movimiento.
    El tipo (DEPOSIT o WITHDRAW) se define en la vista.
    """
    # Monto del movimiento (siempre positivo)
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0.01
    )

    # Descripción del movimiento
    description = serializers.CharField(
        max_length=255,
        required=False,
        default=''
    )


class SavingGoalParticipantSerializer(serializers.ModelSerializer):
    """
    Serializer para participantes de metas compartidas.
    """
    # Nombre del participante
    user_name = serializers.CharField(
        source='user.name',
        read_only=True
    )

    class Meta:
        """Configuración del serializer."""
        model = SavingGoalParticipant
        fields = [
            'id',
            'user_name',
            'joined_at',
        ]
        read_only_fields = ['id', 'user_name', 'joined_at']

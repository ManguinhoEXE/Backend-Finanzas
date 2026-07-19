"""
Serializers de la app de gastos.

Define la estructura de datos para el CRUD de gastos.
Incluye soporte para gastos compartidos.
"""
from rest_framework import serializers

from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo de gastos.

    Maneja la serialización y deserialización de datos
    de gastos. El campo usuario se obtiene automáticamente
    desde el JWT, no se envía en el request.

    El campo compartido indica si el gasto es visible
    para ambos usuarios.
    """
    # Campo de solo lectura que muestra el nombre del dueño
    usuario_nombre = serializers.CharField(
        source='usuario.name',
        read_only=True
    )

    class Meta:
        """Configuración del serializer."""
        model = Expense
        # Campos que se incluyen en la serialización
        fields = [
            'id',
            'usuario_nombre',
            'categoria',
            'fecha',
            'descripcion',
            'valor',
            'compartido',
            'created_at',
        ]
        # Campos de solo lectura (obtenidos automáticamente)
        read_only_fields = ['id', 'created_at', 'usuario_nombre']

"""
Serializers de la app de autenticación.

Define la estructura de datos para la activación de llaves.
"""
from rest_framework import serializers


class ActivateKeySerializer(serializers.Serializer):
    """
    Serializer para la activación de llave de acceso.

    Valida que se proporcione una llave y un nombre de usuario.
    """
    # La llave de acceso que ingresa el usuario
    key = serializers.CharField(max_length=255)

    # El nombre del usuario que se registrará
    name = serializers.CharField(max_length=255)

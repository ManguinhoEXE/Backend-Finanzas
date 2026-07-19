"""
Permisos de la app de autenticación.

Define permisos personalizados si son necesarios.
"""
from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """
    Permiso que verifica que el usuario esté autenticado con JWT.
    Se usa como respaldo del permiso por defecto de DRF.
    """
    def has_permission(self, request, view):
        """Verifica si el usuario tiene un JWT válido."""
        return request.user and request.user.is_authenticated

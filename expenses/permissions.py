"""
Permisos de la app de gastos.

Define permisos para garantizar que cada usuario
solo acceda a sus propios gastos y los compartidos.
"""
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Permiso que verifica acceso y propiedad del gasto.

    Reglas:
    - GET (ver): dueño O gasto compartido
    - PUT (actualizar): solo el dueño
    """
    def has_object_permission(self, request, view, obj):
        """
        Verifica permisos según el método HTTP.

        Args:
            request: Petición HTTP
            view: Vista actual
            obj: Objeto gasto a verificar

        Returns:
            bool: True si tiene permiso, False si no
        """
        # Si es una consulta (GET, HEAD, OPTIONS):
        # permitir si es el dueño O si el gasto es compartido
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return obj.usuario == request.user or obj.compartido

        # Para cualquier otra operación (PUT, PATCH, DELETE):
        # solo el dueño puede modificar
        return obj.usuario == request.user

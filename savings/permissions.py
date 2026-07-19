"""
Permisos del módulo de ahorros.

Define permisos para garantizar que cada usuario
solo acceda a sus propias metas y las compartidas.
"""
from rest_framework.permissions import BasePermission


class IsGoalOwner(BasePermission):
    """
    Permiso que verifica que el usuario sea el propietario de la meta.

    Reglas:
    - GET (ver): propietario O participante en meta compartida
    - PUT/PATCH (editar): solo el propietario
    - DELETE (eliminar): solo el propietario
    """
    def has_object_permission(self, request, view, obj):
        """
        Verifica permisos según el método HTTP.

        Args:
            request: Petición HTTP
            view: Vista actual
            obj: Objeto SavingGoal a verificar

        Returns:
            bool: True si tiene permiso, False si no
        """
        # Si es una consulta (GET, HEAD, OPTIONS):
        # permitir si es el dueño O si es participante de una meta compartida
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            if obj.owner == request.user:
                return True
            if obj.is_shared:
                return obj.participants.filter(user=request.user).exists()
            return False

        # Para cualquier otra operación (PUT, PATCH, DELETE):
        # solo el propietario puede modificar
        return obj.owner == request.user


class IsGoalParticipant(BasePermission):
    """
    Permiso que verifica que el usuario sea participante de la meta.

    Se usa para registrar depósitos y retiros.
    En metas individuales, solo el propietario puede registrar.
    En metas compartidas, cualquier participante puede registrar.
    """
    def has_object_permission(self, request, view, obj):
        """
        Verifica si el usuario puede registrar movimientos.

        Args:
            request: Petición HTTP
            view: Vista actual
            obj: Objeto SavingGoal a verificar

        Returns:
            bool: True si es participante, False si no
        """
        # Si es el propietario, siempre puede
        if obj.owner == request.user:
            return True

        # Si la meta es compartida, cualquier usuario autenticado puede acceder
        if obj.is_shared:
            return True

        # Meta individual: solo el propietario
        return False

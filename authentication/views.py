"""
Vistas de la app de autenticación.

Define la vista para la activación de llaves de acceso.
"""
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AccessKey, User
from .serializers import ActivateKeySerializer


class ActivateKeyView(APIView):
    """
    Vista para activar una llave de acceso.

    POST /api/activate-key/

    Flujo:
    1. Valida la llave ingresada
    2. Verifica que no haya sido utilizada
    3. Crea el usuario en la base de datos
    4. Marca la llave como usada
    5. Genera y retorna un JWT
    """
    # Esta vista no requiere autenticación
    permission_classes = []

    def post(self, request):
        """Maneja la petición POST para activar una llave."""
        # Serializar y validar los datos de entrada
        serializer = ActivateKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Obtener la llave y el nombre del request
        key_value = serializer.validated_data['key']
        user_name = serializer.validated_data['name']

        # Buscar la llave en la base de datos
        try:
            access_key = AccessKey.objects.get(key=key_value)
        except AccessKey.DoesNotExist:
            return Response(
                {'detail': 'La llave ingresada no es válida.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar que la llave no haya sido utilizada
        if access_key.used:
            return Response(
                {'detail': 'La llave ya fue utilizada anteriormente.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear el usuario si no existe, o reutilizar si ya existe
        user, _ = User.objects.get_or_create(name=user_name)

        # Marcar la llave como utilizada con la fecha y hora actual
        access_key.used = True
        access_key.used_at = timezone.now()
        access_key.save()

        # Generar tokens JWT para el usuario creado
        refresh = RefreshToken.for_user(user)

        # Retornar los tokens y la información del usuario
        return Response({
            'detail': 'Cuenta activada exitosamente.',
            'user': {
                'id': user.id,
                'name': user.name,
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
        }, status=status.HTTP_201_CREATED)

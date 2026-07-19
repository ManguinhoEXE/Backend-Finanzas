"""
Vistas de la app de gastos.

Define las vistas para el CRUD de gastos.
Soporta gastos compartidos entre usuarios.
"""
from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Expense
from .permissions import IsOwner
from .serializers import ExpenseSerializer


class ExpenseListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear gastos.

    GET /api/expenses/
        - Lista gastos propios (todos)
        - Lista gastos compartidos de otros usuarios
        - Filtros opcionales: start_date, end_date (YYYY-MM-DD)
    POST /api/expenses/
        - Crea un nuevo gasto para el usuario autenticado
        - Campo 'compartido' se envía en el body (default: False)
    """
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retorna los gastos del usuario autenticado
        más los gastos compartidos de otros usuarios.

        Filtros aplicados:
        - Gastos propios: usuario = request.user
        - Gastos compartidos: compartido = True Y usuario != request.user
        - Filtros de fecha opcionales: start_date, end_date
        """
        usuario = self.request.user
        queryset = Expense.objects.filter(
            Q(usuario=usuario) | Q(compartido=True)
        ).distinct()

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(fecha__gte=start_date)
        if end_date:
            queryset = queryset.filter(fecha__lte=end_date)

        return queryset.order_by('-fecha', '-created_at')

    def perform_create(self, serializer):
        """
        Asocia automáticamente el gasto al usuario autenticado.
        El campo 'compartido' se obtiene del body del request.
        """
        serializer.save(usuario=self.request.user)


class ExpenseDetailView(generics.RetrieveUpdateAPIView):
    """
    Vista para ver y actualizar un gasto específico.

    GET /api/expenses/{id}/
        - Detalle de un gasto propio
        - Detalle de un gasto compartido de otro usuario
    PUT /api/expenses/{id}/
        - Solo el dueño puede actualizar (aunque sea compartido)
    """
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """
        Retorna gastos propios y compartidos de otros usuarios.
        Solo el dueño puede editar (controlado por IsOwner).
        """
        usuario = self.request.user
        return Expense.objects.filter(
            Q(usuario=usuario) | Q(compartido=True)
        ).distinct()

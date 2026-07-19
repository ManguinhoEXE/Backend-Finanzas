"""
URLs de la app de gastos.

Define las rutas del CRUD de gastos.
"""
from django.urls import path

from . import views

urlpatterns = [
    # Lista y creación de gastos
    path('expenses/', views.ExpenseListCreateView.as_view(), name='expense-list'),

    # Detalle, actualización y eliminación de un gasto específico
    path('expenses/<int:pk>/', views.ExpenseDetailView.as_view(), name='expense-detail'),
]

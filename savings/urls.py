"""
URLs del módulo de ahorros.

Define las rutas para metas, depósitos, retiros
y historial de movimientos.
"""
from django.urls import path

from . import views

urlpatterns = [
    # Lista y creación de metas de ahorro
    path(
        'savings/goals/',
        views.SavingGoalListCreateView.as_view(),
        name='saving-goal-list'
    ),

    # Detalle, actualización y eliminación de una meta
    path(
        'savings/goals/<int:pk>/',
        views.SavingGoalDetailView.as_view(),
        name='saving-goal-detail'
    ),

    # Registrar un depósito en una meta
    path(
        'savings/goals/<int:pk>/deposit/',
        views.DepositView.as_view(),
        name='saving-goal-deposit'
    ),

    # Registrar un retiro de una meta
    path(
        'savings/goals/<int:pk>/withdraw/',
        views.WithdrawView.as_view(),
        name='saving-goal-withdraw'
    ),

    # Historial de movimientos de una meta
    path(
        'savings/goals/<int:pk>/movements/',
        views.MovementListView.as_view(),
        name='saving-goal-movements'
    ),

    # Agregar participante a una meta compartida
    path(
        'savings/goals/<int:pk>/participants/',
        views.AddParticipantView.as_view(),
        name='saving-goal-participants'
    ),
]

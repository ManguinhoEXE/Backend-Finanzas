"""
URLs de la app de autenticación.

Define las rutas relacionadas con la activación de llaves.
"""
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from . import views

urlpatterns = [
    # Endpoint para activar una llave de acceso
    path('activate-key/', views.ActivateKeyView.as_view(), name='activate-key'),

    # Endpoint para renovar el token de acceso
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]

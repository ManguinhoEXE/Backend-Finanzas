"""
Configuración de URLs principal del proyecto Finanzas.

Define las rutas raíz y distribuye las URLs a cada app.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Ruta del admin de Django (deshabilitado en producción)
    path('admin/', admin.site.urls),

    # URLs de autenticación
    path('api/', include('authentication.urls')),

    # URLs de gastos
    path('api/', include('expenses.urls')),

    # URLs de ahorros
    path('api/', include('savings.urls')),
]

"""
Configuración ASGI para el proyecto Finanzas.

Punto de entrada ASGI para servidores asincrónicos.
"""
import os

from django.core.asgi import get_asgi_application

# Establecer el módulo de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Obtener la aplicacion ASGI
application = get_asgi_application()

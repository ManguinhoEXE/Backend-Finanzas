"""
Configuración WSGI para el proyecto Finanzas.

Punto de entrada WSGI para despliegues en producción.
"""
import os

from django.core.wsgi import get_wsgi_application

# Establecer el módulo de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Obtener la aplicación WSGI
application = get_wsgi_application()

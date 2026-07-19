#!/usr/bin/env python
"""Script de gestión de Django para el proyecto Finanzas."""
import os
import sys


def main():
    """Ejecuta comandos de gestión de Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Asegúrate de que esté instalado y "
            "disponible en tu entorno virtual. Verifica que hayas activado "
            "el entorno virtual e instalado las dependencias."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

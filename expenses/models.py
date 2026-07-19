"""
Modelos de la app de gastos.

Define el modelo de gasto que almacena los registros financieros.
Incluye soporte para gastos compartidos entre usuarios.
"""
from django.db import models
from django.conf import settings


class Expense(models.Model):
    """
    Modelo de gasto personal.

    Almacena cada gasto registrado por un usuario.
    El campo usuario está vinculado al JWT autenticado.
    Si compartido=True, ambos usuarios pueden ver el gasto.
    """
    # Referencia al usuario dueño del gasto (obtenido desde el JWT)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gastos'
    )

    # Categoría del gasto (ej: alimentación, transporte, etc.)
    categoria = models.CharField(max_length=100)

    # Fecha en que se realizó el gasto
    fecha = models.DateField()

    # Descripción o detalle del gasto
    descripcion = models.CharField(max_length=255)

    # Valor monetario del gasto
    valor = models.DecimalField(max_digits=12, decimal_places=2)

    # Indica si el gasto es visible para ambos usuarios
    compartido = models.BooleanField(default=False)

    # Fecha de creación del registro
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Metadatos del modelo."""
        verbose_name = 'gasto'
        verbose_name_plural = 'gastos'
        # Ordenar por fecha de creación, del más reciente al más antiguo
        ordering = ['-created_at']

    def __str__(self):
        """Representación en texto del gasto."""
        estado = 'Compartido' if self.compartido else 'Privado'
        return f"{self.categoria} - {self.valor} ({estado})"

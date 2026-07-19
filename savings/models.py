"""
Modelos del módulo de ahorros.

Define las metas de ahorro, movimientos y participantes.
Soporta metas individuales y compartidas entre usuarios.
"""
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class SavingGoal(models.Model):
    """
    Meta de ahorro.

    Representa una meta financiera que un usuario (o grupo)
    desea alcanzar. Puede ser individual o compartida.
    """

    # Estados posibles de una meta
    STATUS_CHOICES = [
        ('ACTIVE', 'Activa'),
        ('COMPLETED', 'Completada'),
        ('PAUSED', 'Pausada'),
        ('CANCELLED', 'Cancelada'),
    ]

    # Usuario propietario que creó la meta
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='savings_goals'
    )

    # Nombre de la meta (ej: Casa, Moto, Viaje a Japón)
    name = models.CharField(max_length=255)

    # Descripción opcional de la meta
    description = models.TextField(blank=True, default='')

    # Monto objetivo a ahorrar
    target_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    # Monto actual ahorrar (calculado desde movimientos)
    current_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    # Moneda (preparado para uso futuro)
    currency = models.CharField(max_length=3, default='COP')

    # Fecha límite opcional para alcanzar la meta
    deadline = models.DateField(null=True, blank=True)

    # Indica si la meta es compartida entre usuarios
    is_shared = models.BooleanField(default=False)

    # Estado actual de la meta
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    # Fecha de creación
    created_at = models.DateTimeField(auto_now_add=True)

    # Fecha de última actualización
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadatos del modelo."""
        verbose_name = 'meta de ahorro'
        verbose_name_plural = 'metas de ahorro'
        ordering = ['-created_at']

    def __str__(self):
        """Representación en texto de la meta."""
        return f"{self.name} - {self.current_amount}/{self.target_amount}"

    @property
    def remaining_amount(self):
        """Calcula el monto faltante para alcanzar la meta."""
        restante = self.target_amount - self.current_amount
        return max(restante, 0)

    @property
    def progress_percentage(self):
        """Calcula el porcentaje de progreso hacia la meta."""
        if self.target_amount == 0:
            return 0
        porcentaje = (self.current_amount / self.target_amount) * 100
        return min(porcentaje, 100)

    def update_status(self):
        """
        Actualiza el estado de la meta según el monto actual.
        Si current_amount >= target_amount, cambia a COMPLETED.
        """
        if self.current_amount >= self.target_amount:
            self.status = 'COMPLETED'
            self.save(update_fields=['status', 'updated_at'])


class SavingMovement(models.Model):
    """
    Movimiento de ahorro.

    Registra cada depósito, retiro o ajuste realizado
    en una meta de ahorro. Los movimientos no se eliminan.
    """

    # Tipos de movimiento
    TYPE_CHOICES = [
        ('DEPOSIT', 'Depósito'),
        ('WITHDRAW', 'Retiro'),
        ('ADJUSTMENT', 'Ajuste'),
    ]

    # Meta de ahorro a la que pertenece el movimiento
    goal = models.ForeignKey(
        SavingGoal,
        on_delete=models.CASCADE,
        related_name='movements'
    )

    # Usuario que realizó el movimiento
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='savings_movements'
    )

    # Tipo de movimiento (depósito, retiro o ajuste)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    # Monto del movimiento (siempre positivo)
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    # Descripción del movimiento
    description = models.TextField(blank=True, default='')

    # Fecha y hora del movimiento
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Metadatos del modelo."""
        verbose_name = 'movimiento de ahorro'
        verbose_name_plural = 'movimientos de ahorro'
        ordering = ['-created_at']

    def __str__(self):
        """Representación en texto del movimiento."""
        return f"{self.type} - {self.amount} - {self.goal.name}"


class SavingGoalParticipant(models.Model):
    """
    Participante de una meta compartida.

    Relaciona usuarios con metas de ahorro compartidas.
    Solo existe para metas con is_shared=True.
    """

    # Meta de ahorro compartida
    goal = models.ForeignKey(
        SavingGoal,
        on_delete=models.CASCADE,
        related_name='participants'
    )

    # Usuario participante en la meta
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='savings_participations'
    )

    # Fecha en que se unió a la meta
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Metadatos del modelo."""
        verbose_name = 'participante de meta'
        verbose_name_plural = 'participantes de meta'
        # Un usuario solo puede participar una vez en la misma meta
        unique_together = ['goal', 'user']

    def __str__(self):
        """Representación en texto del participante."""
        return f"{self.user.name} en {self.goal.name}"

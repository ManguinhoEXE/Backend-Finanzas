"""
Modelos de la app de autenticación.

Define el modelo de usuario personalizado y las llaves de acceso.
El modelo User hereda de AbstractBaseUser para ser compatible
con JWT y el sistema de autenticación de Django.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Manager personalizado para el modelo User.

    Permite crear usuarios con solo el campo name.
    """

    def create_user(self, name):
        """
        Crea y retorna un usuario con el nombre proporcionado.

        Args:
            name: Nombre del usuario

        Returns:
            User: Usuario creado
        """
        if not name:
            raise ValueError('El nombre es obligatorio')

        # Crear usuario con el nombre proporcionado
        user = self.model(name=name)
        user.save(using=self._db)
        return user

    def create_superuser(self, name):
        """
        Crea un superusuario (requerido por Django, pero no se usa).

        Args:
            name: Nombre del superusuario

        Returns:
            User: Superusuario creado
        """
        return self.create_user(name)


class User(AbstractBaseUser):
    """
    Modelo de usuario minimalista.

    Hereda de AbstractBaseUser para ser compatible con JWT.
    Solo contiene los campos estrictamente necesarios.
    """
    # Nombre completo del usuario (debe ser único porque es el campo de identificación)
    name = models.CharField(max_length=255, unique=True)

    # Fecha de creación del registro
    created_at = models.DateTimeField(auto_now_add=True)

    # Campo usado como identificador (no hay email ni username)
    USERNAME_FIELD = 'name'

    # Campos requeridos al crear superusuario (vacío porque solo necesitamos name)
    REQUIRED_FIELDS = []

    # Asignar el manager personalizado
    objects = UserManager()

    class Meta:
        """Metadatos del modelo."""
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        """Representación en texto del usuario."""
        return self.name

    # El modelo no necesita permisos de staff ni superuser
    @property
    def is_staff(self):
        """Indica si el usuario es staff (siempre False)."""
        return False

    @property
    def is_superuser(self):
        """Indica si el usuario es superuser (siempre False)."""
        return False

    def has_perm(self, perm, obj=None):
        """Verifica permisos (siempre False)."""
        return False

    def has_module_perms(self, app_label):
        """Verifica permisos de módulo (siempre False)."""
        return False


class AccessKey(models.Model):
    """
    Modelo de llave de acceso.

    Cada llave es única y solo puede utilizarse una vez
    para activar una cuenta de usuario.
    """
    # La llave única de activación
    key = models.CharField(max_length=255, unique=True)

    # Indica si la llave ya fue utilizada
    used = models.BooleanField(default=False)

    # Fecha y hora en que se utilizó la llave
    used_at = models.DateTimeField(null=True, blank=True)

    # Fecha de creación de la llave
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Metadatos del modelo."""
        verbose_name = 'llave de acceso'
        verbose_name_plural = 'llaves de acceso'

    def __str__(self):
        """Representación en texto de la llave."""
        estado = 'Usada' if self.used else 'Disponible'
        return f"{self.key} - {estado}"

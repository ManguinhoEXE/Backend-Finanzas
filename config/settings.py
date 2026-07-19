"""
Configuracion principal del proyecto Finanzas.

Esta archivo contiene toda la configuracion de Django.
Los valores sensibles se obtienen desde variables de entorno (.env).
"""
import os
from pathlib import Path
from datetime import timedelta

import environ

# ============================================
# BASE DEL PROYECTO
# ============================================

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# VARIABLES DE ENTORNO
# ============================================

# Cargar variables de entorno desde el archivo .env
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    JWT_ACCESS_TOKEN_LIFETIME_MINUTES=(int, 60),
    DATABASE_URL=(str, ''),
    PORT=(int, 8000),
)

# Leer el archivo .env si existe
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# ============================================
# SEGURIDAD DE DJANGO
# ============================================

# Clave secreta de Django (obtenida desde .env)
SECRET_KEY = env('SECRET_KEY')

# Modo debug (obtenido desde .env)
DEBUG = env('DEBUG')

# Hosts permitidos (obtenidos desde .env)
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Puerto de la aplicacion (Belmo inyecta PORT)
PORT = env('PORT')

# ============================================
# APLICACIONES INSTALADAS
# ============================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones de terceros
    'rest_framework',
    'rest_framework_simplejwt',

    # Aplicaciones del proyecto
    'authentication',
    'expenses',
    'savings',
]

# ============================================
# MIDDLEWARE
# ============================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================
# CONFIGURACION DE URLs
# ============================================

ROOT_URLCONF = 'config.urls'

# ============================================
# PLANTILLAS
# ============================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ============================================
# WSGI
# ============================================

WSGI_APPLICATION = 'config.wsgi.application'

# ============================================
# BASE DE DATOS (PostgreSQL)
# ============================================

DATABASE_URL = env('DATABASE_URL')

if DATABASE_URL:
    # Produccion (Belmo) - usa DATABASE_URL
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    # Desarrollo local - usa variables individuales
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME'),
            'USER': env('USER'),
            'PASSWORD': env('PASSWORD'),
            'HOST': env('HOST'),
            'PORT': env('DB_PORT', default='5432'),
        }
    }

# ============================================
# VALIDACION DE CONTRASENAS
# ============================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================
# INTERNACIONALIZACION
# ============================================

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True

# ============================================
# ARCHIVOS ESTATICOS
# ============================================

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================
# MODELO DE USUARIO PERSONALIZADO
# ============================================

# Indica a Django usar nuestro modelo de usuario personalizado
AUTH_USER_MODEL = 'authentication.User'

# ============================================
# DJANGO REST FRAMEWORK
# ============================================

REST_FRAMEWORK = {
    # Autenticacion por defecto: JWT
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Permisos por defecto: autenticado
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# ============================================
# JWT - simplejwt
# ============================================

SIMPLE_JWT = {
    # Tiempo de vida del access token (obtenido desde .env)
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=env('JWT_ACCESS_TOKEN_LIFETIME_MINUTES')
    ),
    # Token de refresco (se usa para renovar el access token)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    # Algoritmo de codificacion
    'ALGORITHM': 'HS256',
    # Firma del token
    'SIGNING_KEY': SECRET_KEY,
}

# ============================================
# PK por defecto
# ============================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# SEGURIDAD EN PRODUCCION
# ============================================

if not DEBUG:
    # Seguridad en produccion (Belmo, Render, etc.)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

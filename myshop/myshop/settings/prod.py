from .base import *
from decouple import config

# Секретный ключ из .env
SECRET_KEY = config('SECRET_KEY')

DEBUG = False
ADMINS = [('Kuksin Alexandr', 'ritc4@rambler.ru'),]
ALLOWED_HOSTS = ['cozy.su', 'www.cozy.su', '77.232.132.90']


# Безопасность
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True


DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('POSTGRES_DB'),
            'USER': config('POSTGRES_USER'),
            'PASSWORD': config('POSTGRES_PASSWORD'),
            'HOST': config('POSTGRES_HOST', default='db'),  # Изменено на config для гибкости (по умолчанию 'db')
            'PORT': 5432,
        }
    }


# Конфигурация сервера электронной почты
EMAIL_HOST = 'smtp.rambler.ru'
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 465
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
from .base import *
from decouple import config

DEBUG = False
ADMINS = [('Antonio M', 'email@mydomain.com'),]
ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS = ['cozy.su', 'www.cozy.su']

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='db'),  # Изменено на config для гибкости (по умолчанию 'db')
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
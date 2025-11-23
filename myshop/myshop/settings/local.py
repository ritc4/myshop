from .base import *
from decouple import config



# Секретный ключ из .env
SECRET_KEY = config('SECRET_KEY')

DEBUG = True
ADMINS = [('Kuksin Alexandr', 'ritc4@rambler.ru'),]
ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql', 
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

# Для CELERY
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'

# Для RABBITMQ
RABBITMQ_DEFAULT_USER = 'guest'
RABBITMQ_DEFAULT_PASS = 'guest'

# Конфигурация сервера электронной почты
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 465
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')



# CACHES = { 
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#     }
# }



# Redis настройки (для dev: localhost; для prod переопределяем в prod.py через config)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',  # Используйте переменные из base
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor', # Опционально
            'IGNORE_EXCEPTIONS': True,
        }
    }
}
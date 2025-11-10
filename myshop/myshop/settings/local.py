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
EMAIL_HOST = 'smtp.rambler.ru'
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 465
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')



# Redis настройки (для dev: localhost; для prod переопределяем в prod.py через config)
REDIS_HOST = config('REDIS_HOST', default='localhost')
REDIS_PORT = config('REDIS_PORT', default=6379)
REDIS_DB = config('REDIS_DB', default=0)
from .base import *
from decouple import config

# Секретный ключ из .env
SECRET_KEY = config('SECRET_KEY')

DEBUG = False
ADMINS = [('Kuksin Alexandr', 'ccozy@yandex.ru'),]
ALLOWED_HOSTS = ['cozy.su', 'www.cozy.su', '77.232.132.90','127.0.0.1']


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
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 465
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

# Админский email для уведомлений (используется в задачах, например, для BCC)
ADMIN_EMAIL = config('ADMIN_EMAIL', default='ccozy@yandex.ru')


# В prod.py (после импорта из base)
# Redis настройки (для dev: localhost; для prod переопределяем в prod.py через config)
REDIS_HOST = config('REDIS_HOST')
REDIS_PORT = config('REDIS_PORT') 
REDIS_DB = config('REDIS_DB')
REDIS_PASSWORD = config('REDIS_PASSWORD')  # Переопределите, если нужно


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',  # Используйте переменные из base
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor', # Опционально
            'IGNORE_EXCEPTIONS': True,
        }
    }
}
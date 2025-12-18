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





# # рабочий парсер товаров очень, быстрый но не устанавливает первую фотографию товара а рандомна.
# # Бэкенд для результатов задач
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Или другой URL, если Redis на другом порту/хосте

# # Оpcционально: настройки для сериализации результатов (для совместимости)
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_ACCEPT_CONTENT = ['json']





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



# # Настройки сессий для корзины (долгое хранение, безопасное)
# SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'  # Хранение в Redis-кэше + БД (производительнее, чем 'db')
# SESSION_COOKIE_AGE = 604800  # 7 дней — корзина не теряется, если пользователь неактивен (компромисс; другие используют 14 дней)
# SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Корзина сохраняется после закрытия браузера (удобно для мобильных)
# SESSION_COOKIE_HTTPONLY = True  # Защита от XSS (стандартная практика)
# SESSION_SAVE_EVERY_REQUEST = False  # Не сохраняем на каждый запрос (экономит БД; сессия обновляется только при изменениях в cart.py)

# # Дополнительно для безопасности (вы уже имеете CSRF_COOKIE_SECURE)
# SESSION_COOKIE_SAMESITE = 'Lax'  # Предотвращает CSRF в кросс-доменах



# Админский email для уведомлений (используется в задачах, например, для BCC)
ADMIN_EMAIL = config('ADMIN_EMAIL', default='ccozy@yandex.ru')


# CACHES = { 
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#     }
# }



# Redis настройки (для dev: localhost; для prod переопределяем в prod.py через config)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        }
    }
}



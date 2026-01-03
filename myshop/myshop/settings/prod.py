from .base import *
from decouple import config


# Секретный ключ из .env
SECRET_KEY = config('SECRET_KEY')

DEBUG = False
ADMINS = [('Kuksin Alexandr', 'ritc4@rambler.ru'),]
ALLOWED_HOSTS = ['.cozy-opt.ru'] # '77.232.132.90','127.0.0.1','cozy-opt.ru', 'www.cozy-opt.ru'


# Безопасность
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000 


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




# В prod.py (после импорта из base)
# Redis настройки (для dev: localhost; для prod переопределяем в prod.py через config)
REDIS_HOST = config('REDIS_HOST')
REDIS_PORT = config('REDIS_PORT') 
REDIS_DB = config('REDIS_DB')
REDIS_PASSWORD = config('REDIS_PASSWORD')  # Переопределите, если нужно




# # рабочий парсер товаров очень быстрый но не устанавливает первую фотографию товара а рандомна.
# # Бэкенд для результатов задач
# CELERY_RESULT_BACKEND = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'  # Или другой URL, если Redis на другом порту/хосте

# настройки для сериализации результатов (для совместимости)
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_ACCEPT_CONTENT = ['json']




# Настройки сессий для корзины (долгое хранение, безопасное)
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'  # Хранение в Redis-кэше + БД (производительнее, чем 'db')
SESSION_COOKIE_AGE = 604800  # 7 дней — корзина не теряется, если пользователь неактивен (компромисс; другие используют 14 дней)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Корзина сохраняется после закрытия браузера (удобно для мобильных)
SESSION_COOKIE_HTTPONLY = True  # Защита от XSS (стандартная практика)
SESSION_SAVE_EVERY_REQUEST = False  # Не сохраняем на каждый запрос (экономит БД; сессия обновляется только при изменениях в cart.py)

# Дополнительно для безопасности (вы уже имеете CSRF_COOKIE_SECURE)
SESSION_COOKIE_SAMESITE = 'Lax'  # Предотвращает CSRF в кросс-доменах



CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',  # Используйте переменные из base
    }
}
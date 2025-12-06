# # Взять официальный базовый Docker-образ Python
# FROM python:3.12.3

# # Задать переменные среды (предотвращают создание .pyc файлов и буферизацию вывода)
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # Задать рабочий каталог
# WORKDIR /app

# RUN mkdir -p /app/myshop/static /app/myshop/media && \
#     chown -R www-data:www-data /app/myshop/static /app/myshop/media

# # !!! Используем стандарт XDG: Указываем корневую папку для кэшей пользователя !!!
# ENV XDG_CACHE_HOME=/app/myshop/.cache/

# # Создаём доступную для записи директорию кэша шрифтов внутри нашей папки XDG
# RUN mkdir -p /app/myshop/.cache/fontconfig && \
#     chown -R www-data:www-data /app/myshop/.cache/fontconfig

# # Установка системных зависимостей для WeasyPrint
# # для правильной работы WeasyPrint в контейнере (генерация PDF, рендеринг)
# RUN apt-get update && apt-get install -y \
#     libcairo2-dev \
#     libcairo-gobject2 \
#     libpango1.0-dev \
#     libpangocairo-1.0-0 \
#     libpangoft2-1.0-0 \
#     libgdk-pixbuf2.0-dev \
#     libgdk-pixbuf2.0-common \
#     libffi-dev \
#     libxml2-dev \
#     libxslt-dev \
#     pkg-config \
#     && rm -rf /var/lib/apt/lists/*


# # Обновить pip и установить зависимости (делаем это рано, чтобы кэшировать слой)
# RUN pip install --upgrade pip

# # Копировать requirements.txt (только файл, чтобы использовать кэширование)
# COPY requirements.txt .

# # Установить пакеты из requirements.txt (без кэша для уменьшения размера образа)
# RUN pip install --no-cache-dir -r requirements.txt

# # Копировать весь исходный код проекта (после зависимостей, чтобы изменения кода не пересчитывали pip)
# COPY . .

# # Теперь директория /app/myshop/ существует — меняем права
# RUN chown -R www-data:www-data /app

# # change to the app user
# USER www-data






# Взять официальный базовый Docker-образ Python (slim для меньшего размера, ~200MB)
FROM python:3.12-slim

# Задать переменные среды (предотвращают .pyc и буферизацию)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Установить системные зависимости для WeasyPrint и других (объединено для скорости)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libcairo2-dev \
    libpango1.0-dev \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libffi-dev \
    libharfbuzz-dev \
    pkg-config \
    libjpeg-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
&& rm -rf /var/lib/apt/lists/*

# Задать рабочий каталог
WORKDIR /app

# Создать необходимые директории и задать права для кэшей (объединено)
RUN mkdir -p /app/myshop/static /app/myshop/media /app/myshop/.cache/fontconfig && \
    chown -R www-data:www-data /app/myshop

# Задать XDG кэш для пользователя
ENV XDG_CACHE_HOME=/app/myshop/.cache/

# Установить зависимости Python (без dev-пакетов, используйте base-вариант requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /root/.cache/pip

# Копировать исходный код (после зависимостей для кэширования)
COPY . .

# Финальные права и переключение пользователя
RUN chown -R www-data:www-data /app
USER www-data
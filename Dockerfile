# Взять официальный базовый Docker-образ Python
FROM python:3.12.3

# Задать переменные среды (предотвращают создание .pyc файлов и буферизацию вывода)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Задать рабочий каталог
WORKDIR /app

RUN mkdir -p /app/myshop/static /app/myshop/media && \
    chown -R www-data:www-data /app/myshop/static /app/myshop/media

# !!! Используем стандарт XDG: Указываем корневую папку для кэшей пользователя !!!
ENV XDG_CACHE_HOME=/app/myshop/.cache/

# Создаём доступную для записи директорию кэша шрифтов внутри нашей папки XDG
RUN mkdir -p /app/myshop/.cache/fontconfig && \
    chown -R www-data:www-data /app/myshop/.cache/fontconfig

# Установка системных зависимостей для WeasyPrint
# для правильной работы WeasyPrint в контейнере (генерация PDF, рендеринг)
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    libcairo-gobject2 \
    libpango1.0-dev \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-dev \
    libgdk-pixbuf2.0-common \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*


# Обновить pip и установить зависимости (делаем это рано, чтобы кэшировать слой)
RUN pip install --upgrade pip

# Копировать requirements.txt (только файл, чтобы использовать кэширование)
COPY requirements.txt .

# Установить пакеты из requirements.txt (без кэша для уменьшения размера образа)
RUN pip install --no-cache-dir -r requirements.txt

# Копировать весь исходный код проекта (после зависимостей, чтобы изменения кода не пересчитывали pip)
COPY . .

# Теперь директория /app/myshop/ существует — меняем права
RUN chown -R www-data:www-data /app

# change to the app user
USER www-data
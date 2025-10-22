# Взять официальный базовый Docker-образ Python
FROM python:3.12.3

# Задать переменные среды (предотвращают создание .pyc файлов и буферизацию вывода)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Задать рабочий каталог
WORKDIR /app

# Обновить pip и установить зависимости (делаем это рано, чтобы кэшировать слой)
RUN pip install --upgrade pip

# Копировать requirements.txt (только файл, чтобы использовать кэширование)
COPY requirements.txt .

# Установить пакеты из requirements.txt (без кэша для уменьшения размера образа)
RUN pip install --no-cache-dir -r requirements.txt

# Копировать весь исходный код проекта (после зависимостей, чтобы изменения кода не пересчитывали pip)
COPY . .


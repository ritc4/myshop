# # Взять официальный базовый Docker-образ Python
# FROM python:3.12.3


# # Задать переменные среды
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # # Устанавливаем системные зависимости (для PostgreSQL, Pillow и т.д.)
# # RUN apt-get update && apt-get install -y \
# #     gcc \
# #     libpq-dev \
# #     && rm -rf /var/lib/apt/lists/*

# # Установить зависимости
# RUN pip install --upgrade pip

# # Создаём рабочую директорию
# WORKDIR /app

# # Копируем requirements из корня и устанавливаем зависимости
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Копируем весь проект (включая папку myshop/)
# COPY . .

# # Собираем статические файлы (если используете collectstatic)
# RUN python myshop/manage.py collectstatic --noinput

# # Экспонируем порт
# EXPOSE 8000

# # Запускаем сервер (для продакшена замените на gunicorn)
# CMD ["python", "myshop/manage.py", "runserver", "0.0.0.0:8000"]




# Взять официальный базовый Docker-образ Python
FROM python:3.12.3
# Задать переменные среды
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Задать рабочий каталог
WORKDIR /app
# Установить зависимости
RUN pip install --upgrade pip
# Шаг 5: Копируем requirements.txt
COPY requirements.txt .
# Шаг 7: Копируем весь исходный код проекта Django
COPY . .
RUN chmod +x ./wait-for-it.sh
# Шаг 6: Устанавливаем пакеты из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

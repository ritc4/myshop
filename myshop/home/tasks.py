from celery import shared_task
import asyncio
from .import_utils import import_products_from_csv  # Импорт твоей функции


@shared_task
def import_csv_task(file_path):
    """
    Celery-задача для асинхронного импорта из CSV.
    Вызывает asyncio.run внутри, чтобы обработать асинхронный код.
    """
    try:
        asyncio.run(import_products_from_csv(file_path))
        return f"Импорт из {file_path} завершён успешно."
    except Exception as e:
        return f"Ошибка импорта: {e}"

from celery import shared_task
import asyncio
from .import_utils import import_products_from_csv  # Импорт твоей функции
from imagekit import ImageSpec
from imagekit.processors import ResizeToFit
from .models import Review, ReviewImage
from django.core.files import File
from django.core.files.base import ContentFile
import base64
import io 
from PIL import Image




# асинхронная версия
# @shared_task
# def import_csv_task(file_path):
#     """
#     Celery-задача для асинхронного импорта из CSV.
#     Вызывает asyncio.run внутри, чтобы обработать асинхронный код.
#     """
#     try:
#         asyncio.run(import_products_from_csv(file_path))
#         return f"Импорт из {file_path} завершён успешно."
#     except Exception as e:
#         return f"Ошибка импорта: {e}"


# синхронная версия
@shared_task
def import_csv_task(file_path):
    """
    Celery-задача для синхронного импорта из CSV.
    Прямой вызов синхронной функции (без asyncio).
    """
    try:
        result = import_products_from_csv(file_path)  # Синхронный вызов
        return f"Импорт из {file_path} завершён успешно."  # Можно вернуть результат функции или просто сообщение
    except Exception as e:
        return f"Ошибка импорта: {e}"




@shared_task(bind=True, max_retries=3)
def process_images(self, review_id, images_data=None):
    if images_data is None:
        images_data = []
    
    try:
        review = Review.objects.get(id=review_id)
        review_images = []
        
        for data in images_data:
            try:
                # Извлекаем content (обрабатываем разные типы)
                raw_content = data['content']
                if isinstance(raw_content, io.BytesIO):
                    content = raw_content.getvalue()  # Из BytesIO в bytes
                elif isinstance(raw_content, str):
                    content = base64.b64decode(raw_content)  # Если base64-строка
                else:
                    content = raw_content  # Уже bytes или bytes-like
        
                # Создаём изображение в памяти
                img = Image.open(io.BytesIO(content))
                
                # Ресайз (Thumbnail сохраняет пропорции)
                img.thumbnail((500, 500), Image.Resampling.LANCZOS)
                
                # Конверсия в WebP и сохранение в BytesIO
                processed_io = io.BytesIO()
                img.save(processed_io, 'WEBP', quality=85, optimize=True)
                processed_bytes = processed_io.getvalue()
                
                # ContentFile с вебп-именем
                original_name = data.get('name', 'image').split('.')[0]
                webp_name = f"{original_name}.webp"
                processed_file = ContentFile(processed_bytes, name=webp_name)
                
                # Создаём ReviewImage
                review_images.append(ReviewImage(
                    review=review,
                    image=processed_file
                ))
            except Exception as img_error:
                print(f"Ошибка обработки изображения {data.get('name', 'unknown')}: {img_error}")
                continue  # Пропускаем проблемное изображение
        
        # Bulk-создание валидных изображений
        if review_images:
            ReviewImage.objects.bulk_create(review_images)
        
        return f"Обработка завершена для {review_id}: {len(review_images)}/{len(images_data)} WebP-изображений создано."
        
    except Review.DoesNotExist:
        return f"Отзыв {review_id} не найден."
    except Exception as e:
        print(f"Ошибка в process_images: {e}")
        raise self.retry(exc=e, countdown=5)





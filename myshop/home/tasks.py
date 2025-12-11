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



# # рабочий парсер товаров очень, быстрый но не устанавливает первую фотографию товара а рандомна.
# from home.import_utils import (
#     generate_slug, get_existing_images, import_images_parallel,
#     download_image_with_delay, get_or_create_size, get_or_create_category,
#     get_or_create_product, create_product, save_product, get_or_create_product_price,
#     update_product_price, parse_price
# )

# @shared_task(bind=True)
# def import_csv_batch_task(self, rows, start_num=1):  # Добавьте start_num
#     successful_imports = 0
#     errors = []
    
#     for row_num, row in enumerate(rows, start=start_num):  # Глобальная нумерация строк
#         try:
#             # Получаем или создаём размер
#             size, _ = get_or_create_size(row.get('Значение св-ва для модификации товара №1', ''))
#             if not size:
#                 size = None  # Если пустой размер, используем None

#             # Получаем или создаём категорию (в вашем коде всегда пустая, как указано)
#             category, _ = get_or_create_category('')

#             title = row.get('Название товара', '').strip()
#             if not title:
#                 raise ValueError("Пропуск строки: нет названия товара.")

#             article_number_str = row.get('Артикул', '').strip()
#             try:
#                 article_number = int(article_number_str)
#             except (ValueError, TypeError):
#                 raise ValueError(f"Пропуск строки: неверный артикул {article_number_str}.")

#             slug = generate_slug(title, article_number)

#             product = get_or_create_product(article_number)
#             stock = 100

#             if product:
#                 # Обновляем существующий продукт
#                 product.slug = slug
#                 product.title = title
#                 product.description = row.get('Полное описание товара', '')
#                 product.is_hidden = row.get('Скрыт ли товар на сайте?', '0').strip() == '1'
#                 product.unit = row.get('Ед. измерения', '')
#                 product.stock = stock
#                 product.category = category
#                 product = save_product(product)

#                 # Обновляем или создаем цену для продукта
#                 product_price, price_created = get_or_create_product_price(
#                     product,
#                     size,
#                     defaults={
#                         'price': parse_price(row.get('Цена продажи, без учёта скидок', 0)),
#                         'old_price': parse_price(row.get('Старая цена', '')),
#                         'zacup_price': parse_price(row.get('Закупочная цена', 0)),
#                     }
#                 )

#                 if not price_created:
#                     # Если цена уже существует, обновляем её
#                     update_product_price(product_price, row)
#             else:
#                 # Если продукт не существует, создаем новый
#                 product = create_product(
#                     slug,
#                     title,
#                     row.get('Полное описание товара', ''),
#                     row.get('Скрыт ли товар на сайте?', '0').strip() == '1',
#                     article_number,
#                     row.get('Ед. измерения', ''),
#                     stock,
#                     category
#                 )

#                 # Создание цены для нового продукта
#                 get_or_create_product_price(
#                     product,
#                     size,
#                     defaults={
#                         'price': parse_price(row.get('Цена продажи, без учёта скидок', 0)),
#                         'old_price': parse_price(row.get('Старая цена', '')),
#                         'zacup_price': parse_price(row.get('Закупочная цена', 0)),
#                     }
#                 )

#             # Если есть URL для изображений, загружаем их параллельно с ограничениями
#             image_urls = row.get('Изображения товара', '').strip()
#             if image_urls:
#                 import_images_parallel(image_urls, product)  # Параллельная загрузка с дросселем, чтобы не блокировать сервер

#             successful_imports += 1
#         except Exception as e:
#             error_msg = f"Ошибка при обработке строки {row_num}: {e}"
#             errors.append({'row_num': row_num, 'row': dict(row), 'error': error_msg})
    
#     total_processed = successful_imports + len(errors)
#     failed_count = len(errors)
    
#     # Возвращаем результат для отслеживания
#     return {
#         'total_processed': total_processed,
#         'successful_imports': successful_imports,
#         'failed_count': failed_count,
#         'errors': errors
#     }








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





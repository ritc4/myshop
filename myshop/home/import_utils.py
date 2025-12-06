# import csv
# import aiohttp
# import asyncio
# import aiofiles
# from django.core.files.base import ContentFile
# from asgiref.sync import sync_to_async
# from .models import Product, Size, ProductPrice, Category, ProductImage
# from slugify import slugify

# def generate_slug(title, article_number):
#     slug = slugify(f"{title}-{article_number}")
#     return slug

# async def import_images(image_urls, product):
#     # Разделяем URL по переносам строк
#     image_urls = [url.strip() for url in image_urls.splitlines() if url.strip()]

#     # Проверяем, есть ли уже изображения для данного продукта
#     existing_images = await get_existing_images(product)

#     if existing_images:
#         print(f"Изображения уже загружены для продукта {product.title}. Пропускаем загрузку.")
#         return  # Если изображения уже существуют, пропускаем загрузку

#     async with aiohttp.ClientSession() as session:
#         for url in image_urls:  # Загружаем изображения последовательно
#             await download_image(session, url, product)

# async def download_image(session, image_url, product):
#     try:
#         print(f"Попытка загрузки изображения: {image_url.strip()}")
#         async with session.get(image_url.strip(), timeout=aiohttp.ClientTimeout(total=10)) as response:
#             print(f"Статус ответа для {image_url.strip()}: {response.status}")
#             if response.status == 200:
#                 image_data = await response.read()
#                 image_file = ContentFile(image_data)

#                 # Извлечение имени файла из URL
#                 image_name = image_url.split("/")[-1]
#                 product_image = ProductImage(product=product)

#                 # Сохранение изображения
#                 await sync_to_async(product_image.image.save)(
#                     image_name, image_file
#                 )
#                 await sync_to_async(product_image.save)()  # Сохранение в асинхронном контексте
#                 print(f"Изображение {image_name} успешно загружено для продукта {product.title}.")
#             else:
#                 print(f"Ошибка при загрузке изображения {image_url.strip()}: статус {response.status}")
#     except Exception as img_e:
#         print(f"Ошибка при загрузке изображения {image_url.strip()}: {img_e}")

# @sync_to_async
# def get_existing_images(product):
#     return ProductImage.objects.filter(product=product).exists()

# @sync_to_async
# def get_or_create_size(size_title):
#     return Size.objects.get_or_create(title=size_title)

# @sync_to_async
# def get_or_create_category(category_name):
#     category_slug = slugify(category_name)
#     return Category.objects.get_or_create(name=category_name, slug=category_slug)

# @sync_to_async
# def get_or_create_product(article_number):
#     return Product.objects.filter(article_number=article_number).first()

# @sync_to_async
# def create_product(slug, title, description, is_hidden, article_number, unit, stock, category):
#     return Product.objects.create(
#         slug=slug,
#         title=title,
#         description=description,
#         is_hidden=is_hidden,
#         article_number=article_number,
#         unit=unit,
#         stock=stock,
#         category=category,
#     )

# @sync_to_async
# def save_product(product):
#     product.save()
#     return product

# @sync_to_async
# def get_or_create_product_price(product, size, defaults):
#     return ProductPrice.objects.get_or_create(product=product, size=size, defaults=defaults)

# @sync_to_async
# def update_product_price(product_price, row):
#     product_price.price = row['Цена продажи']
#     product_price.old_price = row.get('Старая цена')
#     product_price.zacup_price = row['Закупочная цена']
#     product_price.save()

# async def import_products_from_csv(file_path):
#     async with aiofiles.open(file_path, mode='r', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(await csvfile.readlines())
#         for row in reader:
#             try:
#                 size, _ = await get_or_create_size(row['Размер'])
#                 category_name = row.get('Категория', None)
#                 if category_name:
#                     category, _ = await get_or_create_category(category_name)
#                 else:
#                     default_category, _ = await get_or_create_category('Без категории')
#                     category = default_category

#                 title = row['Название товара']
#                 article_number = row['Артикул']
#                 slug = generate_slug(title, article_number)

#                 print(f"Генерируем slug для продукта: {slug}")

#                 product = await get_or_create_product(article_number)
                
#                 if product:
#                     product.slug = slug
#                     product.title = title
#                     product.description = row['Описание товара']
#                     product.is_hidden = row['Скрыт ли товар'].strip() == '1'
#                     product.unit = row['Ед. измерения']
#                     product.stock = row['Остаток']
#                     product.category = category
#                     await save_product(product)

#                     # Обновляем или создаем цену для продукта
#                     product_price, price_created = await get_or_create_product_price(
#                         product,
#                         size,
#                         defaults={
#                             'price': row['Цена продажи'],
#                             'old_price': row.get('Старая цена'),
#                             'zacup_price': row['Закупочная цена'],
#                         }
#                     )

#                     if not price_created:
#                         # Если цена уже существует, обновляем её
#                         await update_product_price(product_price, row)
#                 else:
#                     # Если продукт не существует, создаем новый
#                     product = await create_product(
#                         slug,
#                         title,
#                         row['Описание товара'],
#                         row['Скрыт ли товар'].strip() == '1',
#                         article_number,
#                         row['Ед. измерения'],
#                         row['Остаток'],
#                         category
#                     )

#                     # Создание цены для нового продукта
#                     await get_or_create_product_price(
#                         product,
#                         size,
#                         defaults={
#                             'price': row['Цена продажи'],
#                             'old_price': row.get('Старая цена'),
#                             'zacup_price': row['Закупочная цена'],
#                         }
#                     )

#                 # Если есть URL для изображений, загружаем их
#                 if 'Изображения' in row and row['Изображения']:
#                     image_urls = row['Изображения'].strip()
#                     await import_images(image_urls, product)  # Загрузка изображений только один раз для продукта

#                 print(f"Продукт {title} успешно импортирован.")

#             except Exception as e:
#                 print(f"Ошибка при обработке строки {row}: {e}")



# # последний рабочий
# import csv
# import aiohttp
# import asyncio
# import aiofiles
# from django.core.files.base import ContentFile
# from asgiref.sync import sync_to_async
# from .models import Product, Size, ProductPrice, Category, ProductImage
# from slugify import slugify
# from django.db.models import Q

# def generate_slug(title, article_number):
#     slug = slugify(f"{title}-{article_number}")
#     return slug

# async def import_images(image_urls, product):
#     # Разделяем URL по переносам строк
#     image_urls = [url.strip() for url in image_urls.splitlines() if url.strip()]

#     # Проверяем, есть ли уже изображения для данного продукта
#     existing_images = await get_existing_images(product)

#     if existing_images:
#         print(f"Изображения уже загружены для продукта {product.title}. Пропускаем загрузку.")
#         return  # Если изображения уже существуют, пропускаем загрузку

#     async with aiohttp.ClientSession() as session:
#         for url in image_urls:  # Загружаем изображения последовательно
#             await download_image(session, url, product)

# async def download_image(session, image_url, product):
#     try:
#         print(f"Попытка загрузки изображения: {image_url.strip()}")
#         async with session.get(image_url.strip(), timeout=aiohttp.ClientTimeout(total=10)) as response:
#             print(f"Статус ответа для {image_url.strip()}: {response.status}")
#             if response.status == 200:
#                 image_data = await response.read()
#                 image_file = ContentFile(image_data)

#                 # Извлечение имени файла из URL
#                 image_name = image_url.split("/")[-1]
#                 product_image = ProductImage(product=product)

#                 # Сохранение изображения
#                 await sync_to_async(product_image.image.save)(
#                     image_name, image_file
#                 )
#                 await sync_to_async(product_image.save)()  # Сохранение в асинхронном контексте
#                 print(f"Изображение {image_name} успешно загружено для продукта {product.title}.")
#             else:
#                 print(f"Ошибка при загрузке изображения {image_url.strip()}: статус {response.status}")
#     except Exception as img_e:
#         print(f"Ошибка при загрузке изображения {image_url.strip()}: {img_e}")

# @sync_to_async
# def get_existing_images(product):
#     return ProductImage.objects.filter(product=product).exists()

# @sync_to_async
# def get_or_create_size(size_title):
#     normalized_title = size_title.strip().upper()
#     size, created = Size.objects.get_or_create(
#         title__iexact=normalized_title,  # Используйте фильтр с iexact
#         defaults={'title': size_title}   # Сохраняйте оригинальный title
#     )
#     return size, created

# @sync_to_async
# def get_or_create_category(category_name):
#     category_slug = slugify(category_name)
#     return Category.objects.get_or_create(name=category_name, slug=category_slug)

# @sync_to_async
# def get_or_create_product(article_number):
#     return Product.objects.filter(article_number=article_number).first()

# @sync_to_async
# def create_product(slug, title, description, is_hidden, article_number, unit, stock, category):
#     return Product.objects.create(
#         slug=slug,
#         title=title,
#         description=description,
#         is_hidden=is_hidden,
#         article_number=article_number,
#         unit=unit,
#         stock=stock,
#         category=category,
#     )

# @sync_to_async
# def save_product(product):
#     product.save()
#     return product

# @sync_to_async
# def get_or_create_product_price(product, size, defaults):
#     return ProductPrice.objects.get_or_create(product=product, size=size, defaults=defaults)

# @sync_to_async
# def update_product_price(product_price, row):
#     product_price.price = row['Цена продажи']
#     product_price.old_price = row.get('Старая цена')
#     product_price.zacup_price = row['Закупочная цена']
#     product_price.save()

# async def import_products_from_csv(file_path):
#     async with aiofiles.open(file_path, mode='r', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(await csvfile.readlines())
#         for row in reader:
#             try:
#                 size, _ = await get_or_create_size(row['Размер'])
#                 category_name = row.get('Категория', None)
#                 if category_name:
#                     category, _ = await get_or_create_category(category_name)
#                 else:
#                     default_category, _ = await get_or_create_category('Без категории')
#                     category = default_category

#                 title = row['Название товара']
#                 article_number = row['Артикул']
#                 slug = generate_slug(title, article_number)

#                 print(f"Генерируем slug для продукта: {slug}")

#                 product = await get_or_create_product(article_number)
                
#                 if product:
#                     product.slug = slug
#                     product.title = title
#                     product.description = row['Описание товара']
#                     product.is_hidden = row['Скрыт ли товар'].strip() == '1'
#                     product.unit = row['Ед. измерения']
#                     product.stock = row['Остаток']
#                     product.category = category
#                     await save_product(product)

#                     # Обновляем или создаем цену для продукта
#                     product_price, price_created = await get_or_create_product_price(
#                         product,
#                         size,
#                         defaults={
#                             'price': row['Цена продажи'],
#                             'old_price': row.get('Старая цена'),
#                             'zacup_price': row['Закупочная цена'],
#                         }
#                     )

#                     if not price_created:
#                         # Если цена уже существует, обновляем её
#                         await update_product_price(product_price, row)
#                 else:
#                     # Если продукт не существует, создаем новый
#                     product = await create_product(
#                         slug,
#                         title,
#                         row['Описание товара'],
#                         row['Скрыт ли товар'].strip() == '1',
#                         article_number,
#                         row['Ед. измерения'],
#                         row['Остаток'],
#                         category
#                     )

#                     # Создание цены для нового продукта
#                     await get_or_create_product_price(
#                         product,
#                         size,
#                         defaults={
#                             'price': row['Цена продажи'],
#                             'old_price': row.get('Старая цена'),
#                             'zacup_price': row['Закупочная цена'],
#                         }
#                     )

#                 # Если есть URL для изображений, загружаем их
#                 if 'Изображения' in row and row['Изображения']:
#                     image_urls = row['Изображения'].strip()
#                     await import_images(image_urls, product)  # Загрузка изображений только один раз для продукта

#                 print(f"Продукт {title} успешно импортирован.")

#             except Exception as e:
#                 print(f"Ошибка при обработке строки {row}: {e}")







# синхронная версия
import csv
import os
import requests
from django.core.files.base import ContentFile
from .models import Product, Size, ProductPrice, Category, ProductImage
from slugify import slugify
from django.db.models import Q

def generate_slug(title, article_number):
    slug = slugify(f"{title}-{article_number}")
    return slug

def get_existing_images(product):
    return ProductImage.objects.filter(product=product).exists()

def import_images(image_urls, product):
    # Разделяем URL по переносам строк
    image_urls = [url.strip() for url in image_urls.splitlines() if url.strip()]

    # Проверяем, есть ли уже изображения для данного продукта
    if get_existing_images(product):
        print(f"Изображения уже загружены для продукта {product.title}. Пропускаем загрузку.")
        return  # Если изображения уже существуют, пропускаем загрузку

    for url in image_urls:  # Загружаем изображения последовательно
        download_image(url, product)

def download_image(image_url, product):
    try:
        print(f"Попытка загрузки изображения: {image_url.strip()}")
        response = requests.get(image_url.strip(), timeout=10)
        print(f"Статус ответа для {image_url.strip()}: {response.status_code}")
        if response.status_code == 200:
            image_data = response.content
            image_file = ContentFile(image_data)

            # Извлечение имени файла из URL
            image_name = os.path.basename(image_url.strip())
            if not image_name:
                image_name = 'image.jpg'  # Дефолтное имя, если не извлекли

            product_image = ProductImage(product=product)
            product_image.image.save(image_name, image_file, save=False)
            product_image.save()
            print(f"Изображение {image_name} успешно загружено для продукта {product.title}.")
        else:
            print(f"Ошибка при загрузке изображения {image_url.strip()}: статус {response.status_code}")
    except Exception as img_e:
        print(f"Ошибка при загрузке изображения {image_url.strip()}: {img_e}")

def get_or_create_size(size_title):
    if not size_title or not size_title.strip():
        return None, False
    normalized_title = size_title.strip().upper()
    size, created = Size.objects.get_or_create(
        title__iexact=normalized_title,  # Используйте фильтр с iexact
        defaults={'title': size_title.strip()}  # Сохраняйте оригинальный title
    )
    return size, created

def get_or_create_category(category_name):
    if not category_name or not category_name.strip():
        # Дефолтная категория
        category, created = Category.objects.get_or_create(
            name='Без категории',
            defaults={'slug': slugify('Без категории')}
        )
        return category, created
    category_slug = slugify(category_name.strip())
    return Category.objects.get_or_create(name=category_name.strip(), slug=category_slug)

def get_or_create_product(article_number):
    try:
        return Product.objects.filter(article_number=int(article_number)).first()
    except (ValueError, TypeError):
        # Если article_number не число, возвращаем None
        return None

def create_product(slug, title, description, is_hidden, article_number, unit, stock, category):
    return Product.objects.create(
        slug=slug,
        title=title,
        description=description,
        is_hidden=is_hidden,
        article_number=article_number,
        unit=unit,
        stock=stock,
        category=category,
    )

def save_product(product):
    product.save()
    return product

def get_or_create_product_price(product, size, defaults):
    return ProductPrice.objects.get_or_create(product=product, size=size, defaults=defaults)

def update_product_price(product_price, row):
    product_price.price = row['Цена продажи']
    product_price.old_price = row.get('Старая цена', '')
    product_price.zacup_price = row['Закупочная цена']
    product_price.save()

def import_products_from_csv(file_path):
    """Синхронная главная функция импорта из CSV."""
    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                # Получаем или создаём размер
                size, _ = get_or_create_size(row.get('Размер', ''))
                if not size:
                    size = None  # Если пустой размер, используем None

                # Получаем или создаём категорию
                category_name = row.get('Категория', '')
                category, _ = get_or_create_category(category_name)

                title = row.get('Название товара', '').strip()
                if not title:
                    print("Пропуск строки: нет названия товара.")
                    continue

                article_number_str = row.get('Артикул', '').strip()
                try:
                    article_number = int(article_number_str)
                except (ValueError, TypeError):
                    print(f"Пропуск строки: неверный артикул {article_number_str}.")
                    continue

                slug = generate_slug(title, article_number)
                print(f"Генерируем slug для продукта: {slug}")

                product = get_or_create_product(article_number)
                
                if product:
                    # Обновляем существующий продукт
                    product.slug = slug
                    product.title = title
                    product.description = row.get('Описание товара', '')
                    product.is_hidden = row.get('Скрыт ли товар', '0').strip() == '1'
                    product.unit = row.get('Ед. измерения', '')
                    product.stock = row.get('Остаток', 0)
                    product.category = category
                    save_product(product)

                    # Обновляем или создаем цену для продукта
                    product_price, price_created = get_or_create_product_price(
                        product,
                        size,
                        defaults={
                            'price': float(row.get('Цена продажи', 0)) if row.get('Цена продажи') else 0,
                            'old_price': row.get('Старая цена', ''),
                            'zacup_price': row.get('Закупочная цена', 0),
                        }
                    )

                    if not price_created:
                        # Если цена уже существует, обновляем её
                        update_product_price(product_price, row)
                else:
                    # Если продукт не существует, создаем новый
                    product = create_product(
                        slug,
                        title,
                        row.get('Описание товара', ''),
                        row.get('Скрыт ли товар', '0').strip() == '1',
                        article_number,
                        row.get('Ед. измерения', ''),
                        row.get('Остаток', 0),
                        category
                    )

                    # Создание цены для нового продукта
                    get_or_create_product_price(
                        product,
                        size,
                        defaults={
                            'price': float(row.get('Цена продажи', 0)) if row.get('Цена продажи') else 0,
                            'old_price': row.get('Старая цена', ''),
                            'zacup_price': row.get('Закупочная цена', 0),
                        }
                    )

                # Если есть URL для изображений, загружаем их
                image_urls = row.get('Изображения', '').strip()
                if image_urls:
                    import_images(image_urls, product)  # Загрузка изображений только один раз для продукта

                print(f"Продукт {title} успешно импортирован.")

            except KeyError as e:
                print(f"Ошибка: отсутствует ключ в CSV строке {row}: {e}")
            except Exception as e:
                print(f"Ошибка при обработке строки {row}: {e}")
    
    print("Импорт завершён.")










# import csv
# import aiohttp
# import asyncio
# import aiofiles
# from django.core.files.base import ContentFile
# from asgiref.sync import sync_to_async
# from .models import Product, Size, ProductPrice, Category, ProductImage
# from slugify import slugify

# def generate_slug(title, article_number):
#     slug = slugify(f"{title}-{article_number}")
#     return slug

# async def import_images(image_urls, product):
#     # Разделяем URL по переносам строк
#     image_urls = [url.strip() for url in image_urls.splitlines() if url.strip()]

#     # Проверяем, есть ли уже изображения для данного продукта
#     existing_images = await get_existing_images(product)

#     if existing_images:
#         print(f"Изображения уже загружены для продукта {product.title}. Пропускаем загрузку.")
#         return  # Если изображения уже существуют, пропускаем загрузку

#     async with aiohttp.ClientSession() as session:
#         # Создаем задачи для параллельной загрузки всех изображений
#         tasks = [download_image(session, url, product) for url in image_urls]
#         await asyncio.gather(*tasks)  # Параллельная загрузка с помощью gather

# async def download_image(session, image_url, product):
#     try:
#         print(f"Попытка загрузки изображения: {image_url.strip()}")
#         async with session.get(image_url.strip(), timeout=aiohttp.ClientTimeout(total=10)) as response:
#             print(f"Статус ответа для {image_url.strip()}: {response.status}")
#             if response.status == 200:
#                 image_data = await response.read()
#                 image_file = ContentFile(image_data)

#                 # Извлечение имени файла из URL
#                 image_name = image_url.split("/")[-1]
#                 product_image = ProductImage(product=product)

#                 # Сохранение изображения
#                 await sync_to_async(product_image.image.save)(
#                     image_name, image_file
#                 )
#                 await sync_to_async(product_image.save)()  # Сохранение в асинхронном контексте
#                 print(f"Изображение {image_name} успешно загружено для продукта {product.title}.")
#             else:
#                 print(f"Ошибка при загрузке изображения {image_url.strip()}: статус {response.status}")
#     except Exception as img_e:
#         print(f"Ошибка при загрузке изображения {image_url.strip()}: {img_e}")

# @sync_to_async
# def get_existing_images(product):
#     return ProductImage.objects.filter(product=product).exists()

# @sync_to_async
# def get_or_create_size(size_title):
#     return Size.objects.get_or_create(title=size_title)

# @sync_to_async
# def get_or_create_category(category_name):
#     category_slug = slugify(category_name)
#     return Category.objects.get_or_create(name=category_name, slug=category_slug)

# @sync_to_async
# def get_or_create_product(article_number):
#     return Product.objects.filter(article_number=article_number).first()

# @sync_to_async
# def create_product(slug, title, description, is_hidden, article_number, unit, stock, category):
#     return Product.objects.create(
#         slug=slug,
#         title=title,
#         description=description,
#         is_hidden=is_hidden,
#         article_number=article_number,
#         unit=unit,
#         stock=stock,
#         category=category,
#     )

# @sync_to_async
# def save_product(product):
#     product.save()
#     return product

# @sync_to_async
# def get_or_create_product_price(product, size, defaults):
#     return ProductPrice.objects.get_or_create(product=product, size=size, defaults=defaults)

# @sync_to_async
# def update_product_price(product_price, row):
#     product_price.price = row['Цена продажи']
#     product_price.old_price = row.get('Старая цена')
#     product_price.zacup_price = row['Закупочная цена']
#     product_price.save()

# async def import_products_from_csv(file_path):
#     async with aiofiles.open(file_path, mode='r', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(await csvfile.readlines())
#         for row in reader:
#             try:
#                 size, _ = await get_or_create_size(row['Размер'])
#                 category_name = row.get('Категория', None)
#                 if category_name:
#                     category, _ = await get_or_create_category(category_name)
#                 else:
#                     default_category, _ = await get_or_create_category('Без категории')
#                     category = default_category

#                 title = row['Название товара']
#                 article_number = row['Артикул']
#                 slug = generate_slug(title, article_number)

#                 print(f"Генерируем slug для продукта: {slug}")

#                 product = await get_or_create_product(article_number)
                
#                 if product:
#                     product.slug = slug
#                     product.title = title
#                     product.description = row['Описание товара']
#                     product.is_hidden = row['Скрыт ли товар'].strip() == '1'
#                     product.unit = row['Ед. измерения']
#                     product.stock = row['Остаток']
#                     product.category = category
#                     await save_product(product)

#                     # Обновляем или создаем цену для продукта
#                     product_price, price_created = await get_or_create_product_price(
#                         product,
#                         size,
#                         defaults={
#                             'price': row['Цена продажи'],
#                             'old_price': row.get('Старая цена'),
#                             'zacup_price': row['Закупочная цена'],
#                         }
#                     )

#                     if not price_created:
#                         # Если цена уже существует, обновляем её
#                         await update_product_price(product_price, row)
#                 else:
#                     # Если продукт не существует, создаем новый
#                     product = await create_product(
#                         slug,
#                         title,
#                         row['Описание товара'],
#                         row['Скрыт ли товар'].strip() == '1',
#                         article_number,
#                         row['Ед. измерения'],
#                         row['Остаток'],
#                         category
#                     )

#                     # Создание цены для нового продукта
#                     await get_or_create_product_price(
#                         product,
#                         size,
#                         defaults={
#                             'price': row['Цена продажи'],
#                             'old_price': row.get('Старая цена'),
#                             'zacup_price': row['Закупочная цена'],
#                         }
#                     )

#                 # Если есть URL для изображений, загружаем их
#                 if 'Изображения' in row and row['Изображения']:
#                     image_urls = row['Изображения'].strip()
#                     await import_images(image_urls, product)  # Загрузка изображений только один раз для продукта

#                 print(f"Продукт {title} успешно импортирован.")

#             except Exception as e:
#                 print(f"Ошибка при обработке строки {row}: {e}")

# # Запуск асинхронной функции импорта
# # asyncio.run(import_products_from_csv('path_to_your_csv_file.csv'))








# import csv  # Уже есть, оставляем
# import aiohttp
# import asyncio
# import aiofiles
# from django.core.files.base import ContentFile
# from asgiref.sync import sync_to_async
# from django.db import transaction  # Добавлен для атомарности MPTT
# from .models import Product, Size, ProductPrice, Category, ProductImage
# from slugify import slugify

# def generate_slug(title, article_number):
#     slug = slugify(f"{title}-{article_number}")
#     return slug

# def infer_category_from_title(title):
#     """
#     Анализирует название товара и присваивает родительскую категорию и подкатегорию (ребёнка) на основе ключевых слов.
#     Возвращает: {'parent': str, 'child': str or None}
#     """
#     title_lower = title.lower().strip()
    
#     # Словарь для родительских категорий (основные группы, включая сад/огород)
#     parent_keywords = {
#         'мужское': 'Мужское', 'муж': 'Мужское', 'для мужчин': 'Мужское', 'мужской': 'Мужское', 'мальчик': 'Мужское', 'для мальчиков': 'Мужское',
#         'женское': 'Женское', 'жен': 'Женское', 'для женщин': 'Женское', 'женский': 'Женское', 'девочка': 'Женское', 'для девочек': 'Женское',
#         'детское': 'Детское', 'для детей': 'Детское', 'ребенок': 'Детское', 'дети': 'Детское', 'малыши': 'Детское', 'новорожденный': 'Детское', 'для новорожденных': 'Детское',
#         'подростковое': 'Подростковое', 'подросток': 'Подростковое', 'для подростков': 'Подростковое', 'тинейджер': 'Подростковое',
#         'унисекс': 'Унисекс', 'для всех': 'Унисекс', 'универсальное': 'Унисекс',
#         'постельное': 'Постельное', 'постель': 'Постельное', 'спальня': 'Постельное',
#         'новый год': 'Новый год', 'рождество': 'Новый год', 'праздник': 'Новый год', 'елка': 'Новый год', 'новогодний': 'Новый год',
#         'спорт': 'Спорт', 'фитнес': 'Спорт', 'активный отдых': 'Спорт', 'тренировка': 'Спорт',
#         'дом': 'Дом', 'быт': 'Дом', 'интерьер': 'Дом', 'домашний': 'Дом',
#         'красота': 'Красота', 'косметика': 'Красота', 'уход за кожей': 'Красота', 'макияж': 'Красота',
#         'здоровье': 'Здоровье', 'медицина': 'Здоровье', 'аптека': 'Здоровье',
#         'авто': 'Авто', 'автомобиль': 'Авто', 'транспорт': 'Авто',
#         'еда': 'Еда', 'продукты': 'Еда', 'кулинария': 'Еда', 'питание': 'Еда',
#         'напитки': 'Напитки', 'вода': 'Напитки', 'сок': 'Напитки', 'чай': 'Напитки', 'кофе': 'Напитки', 'алкоголь': 'Напитки',
#         'музыка': 'Музыка', 'инструменты': 'Музыка', 'аудио': 'Музыка',
#         'искусство': 'Искусство', 'художественные товары': 'Искусство', 'рисование': 'Искусство',
#         'книги': 'Книги', 'литература': 'Книги', 'чтение': 'Книги',
#         'электроника': 'Электроника', 'гаджеты': 'Электроника', 'техника': 'Электроника',
#         'сад': 'Сад огород', 'огород': 'Сад огород', 'растения': 'Сад огород', 'ландшафт': 'Сад огород', 'саженцы': 'Сад огород', 'цветы': 'Сад огород', 'семена': 'Сад огород',
#         'животные': 'Животные', 'зоотовары': 'Животные', 'для собак': 'Животные', 'для кошек': 'Животные',
#         'туризм': 'Туризм', 'путешествия': 'Туризм', 'отдых': 'Туризм',
#         'подарки': 'Подарки', 'сувениры': 'Подарки', 'презенты': 'Подарки',
#     }
    
#     # Словарь для подкатегорий (дети в MPTT-дереве)
#     child_keywords = {
#         # Одежда и аксессуары
#         'куртка': 'Куртки', 'пальто': 'Куртки', 'ветровка': 'Куртки', 'плащ': 'Куртки', 'болонья': 'Куртки', 'дубленка': 'Куртки',
#         'футболка': 'Футболки', 'майка': 'Футболки', 'топ': 'Футболки', 'поло': 'Футболки',
#         'джинсы': 'Джинсы', 'брюки': 'Штаны', 'штаны': 'Штаны', 'юбка': 'Юбки', 'шорты': 'Шорты', 'леггинсы': 'Леггинсы',
#         'платье': 'Платья', 'сарафан': 'Платья', 'туника': 'Платья',
#         'кофта': 'Кофты', 'свитер': 'Кофты', 'толстовка': 'Кофты', 'худи': 'Кофты', 'кардиган': 'Кофты',
#         'обувь': 'Обувь', 'ботинки': 'Ботинки', 'кроссовки': 'Кроссовки', 'туфли': 'Туфли', 'сандалии': 'Сандалии', 'сапоги': 'Сапоги', 'балетки': 'Балетки', 'лоферы': 'Лоферы',
#         'шапка': 'Шапки', 'кепка': 'Кепки', 'шарф': 'Шарфы', 'перчатки': 'Перчатки', 'носки': 'Носки', 'носочки': 'Носки',
#         'очки': 'Очки', 'солнцезащитные очки': 'Очки', 'оправа': 'Очки',
#         'сумка': 'Сумки', 'рюкзак': 'Рюкзаки', 'кошелек': 'Кошельки', 'портмоне': 'Кошельки',
#         'ремень': 'Ремни', 'галстук': 'Галстуки', 'бабочка': 'Галстуки',
#         'бельё': 'Бельё', 'трусы': 'Бельё', 'бюстгальтер': 'Бельё', 'колготки': 'Колготки', 'чулки': 'Колготки',
#         'пижама': 'Пижамы', 'халат': 'Халаты', 'ночнушка': 'Пижамы',
#         'купальник': 'Купальники', 'бикини': 'Купальники', 'плавки': 'Купальники','тапочки':'Тапочки',
        
#         # Постельные принадлежности
#         'простыня': 'Простыни', 'наволочка': 'Наволочки', 'пододеяльник': 'Пододеяльники', 'одеяло': 'Одеяла', 'подушка': 'Подушки', 'матрас': 'Матрасы', 'покрывало': 'Покрывала',
        
#         # Игрушки
#         'игрушка': 'Игрушки', 'кукла': 'Куклы', 'машинка': 'Машинки', 'конструктор': 'Конструкторы', 'пазл': 'Пазлы', 'мяч': 'Мячи', 'кубики': 'Кубики',
#         'велосипед': 'Велосипеды', 'самокат': 'Самокаты', 'скейтборд': 'Скейтборды', 'ролики': 'Ролики',
        
#         # Электроника
#         'телефон': 'Телефоны', 'смартфон': 'Смартфоны', 'планшет': 'Планшеты', 'компьютер': 'Компьютеры', 'ноутбук': 'Ноутбуки', 'ультрабук': 'Ноутбуки',
#         'телевизор': 'Телевизоры', 'монитор': 'Мониторы', 'наушники': 'Наушники', 'колонки': 'Колонки', 'часы': 'Часы', 'умные часы': 'Часы',
#         'фотоаппарат': 'Фотоаппараты', 'видеокамера': 'Видеокамеры', 'принтер': 'Принтеры', 'сканер': 'Сканеры', 'роутер': 'Роутеры',
#         'консоль': 'Игровые консоли', 'приставка': 'Игровые консоли',
        
#         # Дом и сад (расширено для MPTT)
#         'растение': 'Растения', 'инструмент': 'Инструменты', 'лопата': 'Инструменты', 'грабли': 'Инструменты',
#         'саженцы': 'Саженцы', 'рассада': 'Саженцы', 'цветы': 'Цветы', 'ландшафт': 'Ландшафт', 'удобрения': 'Удобрения', 'почва': 'Почва', 'грунт': 'Почва', 'семена': 'Семена',
        
#         # Мебель и бытовая техника
#         'мебель': 'Мебель', 'стол': 'Мебель', 'стул': 'Мебель', 'кровать': 'Мебель', 'шкаф': 'Мебель', 'диван': 'Мебель', 'кресло': 'Кресла',
#         'бытовая техника': 'Бытовая техника', 'холодильник': 'Холодильники', 'стиральная машина': 'Стиральные машины', 'пылесос': 'Пылесосы', 'микроволновка': 'Микроволновки', 'чайник': 'Чайники',
#         'посуда': 'Посуда', 'тарелка': 'Посуда', 'кастрюля': 'Посуда', 'вилка': 'Посуда', 'ложка': 'Посуда', 'нож': 'Посуда',
#         'декор': 'Декор', 'картина': 'Декор', 'ваза': 'Декор', 'свеча': 'Декор', 'зеркало': 'Декор',
#         'освещение': 'Освещение', 'лампа': 'Лампы', 'люстра': 'Люстры',
        
#         # Книги и развлечения
#         'книга': 'Книги', 'роман': 'Книги', 'учебник': 'Книги', 'журнал': 'Журналы', 'комикс': 'Комиксы',
#         'DVD': 'DVD', 'Blu-ray': 'Blu-ray', 'игра': 'Игры', 'видео': 'Видео', 'фильм': 'Фильмы',
        
#         # Спорт и здоровье
#         'спорттовары': 'Спорттовары', 'гантели': 'Спорттовары', 'коврик': 'Спорттовары', 'беговая дорожка': 'Спорттовары', 'велотренажер': 'Спорттовары',
#         'витамины': 'Витамины', 'лекарства': 'Лекарства', 'пластыри': 'Лекарства', 'массажер': 'Массажеры',
        
#         # Авто
#         'запчасти': 'Запчасти', 'шины': 'Шины', 'аккумулятор': 'Аккумуляторы', 'масло': 'Масла', 'фильтр': 'Фильтры',
        
#         # Еда и напитки
#         'еда': 'Еда', 'продукты': 'Продукты', 'молоко': 'Молочные продукты', 'хлеб': 'Хлеб', 'мясо': 'Мясо', 'рыба': 'Рыба', 'фрукты': 'Фрукты', 'овощи': 'Овощи',
#         'напитки': 'Напитки', 'вода': 'Вода', 'сок': 'Соки', 'чай': 'Чай', 'кофе': 'Кофе', 'пиво': 'Пиво', 'вино': 'Вино',
        
#         # Музыка и искусство
#         'музыка': 'Музыка', 'инструменты': 'Инструменты', 'гитара': 'Гитары', 'пианино': 'Пианино', 'микрофон': 'Микрофоны',
#         'искусство': 'Искусство', 'краски': 'Краски', 'кисти': 'Кисти', 'холст': 'Холсты',
        
#         # Животные
#         'животные': 'Животные', 'корм': 'Корма', 'игрушки для собак': 'Игрушки для животных', 'ошейник': 'Ошейники',
        
#         # Туризм
#         'туризм': 'Туризм', 'рюкзак': 'Рюкзаки', 'палатка': 'Палатки', 'спальник': 'Спальники',
        
#         # Другое
#         'подарок': 'Подарки', 'сувенир': 'Сувениры', 'открытка': 'Открытки',
#     }
    
#     # Ищем родительскую категорию
#     parent = None
#     for keyword, cat in parent_keywords.items():
#         if keyword in title_lower:
#             parent = cat
#             break
    
#     # Если родитель не найден, проверяем на подкатегорию как fallback (для простых товаров)
#     if not parent:
#         for keyword in child_keywords.keys():
#             if keyword in title_lower:
#                 # Используем подкатегорию как родителя, если нет гендера/типа
#                 parent = child_keywords[keyword].split()[0] if ' ' in child_keywords[keyword] else child_keywords[keyword]
#                 break
#         if not parent:
#             parent = 'Сад огород'  # Резерв
    
#     # Ищем подкатегорию (ребёнка)
#     child = None
#     for keyword, sub in child_keywords.items():
#         if keyword in title_lower:
#             child = sub
#             break
    
#     return {'parent': parent, 'child': child}

# async def import_images(image_urls, product):
#     # Разделяем URL по переносам строк и фильтруем валидные (начинаются с http/https)
#     image_urls = [
#         url.strip() for url in image_urls.splitlines() 
#         if url.strip() and url.strip().startswith(('http://', 'https://'))
#     ]

#     if not image_urls:
#         print(f"Нет валидных URL изображений для продукта {product.title}.")
#         return

#     # Проверяем, есть ли уже изображения для данного продукта
#     existing_images = await get_existing_images(product)

#     if existing_images:
#         print(f"Изображения уже загружены для продукта {product.title}. Пропускаем загрузку.")
#         return  # Если изображения уже существуют, пропускаем загрузку

#     async with aiohttp.ClientSession() as session:
#         # Создаем задачи для параллельной загрузки всех изображений
#         tasks = [download_image(session, url, product) for url in image_urls]
#         await asyncio.gather(*tasks, return_exceptions=True)  # Параллельная загрузка с обработкой ошибок

# async def download_image(session, image_url, product):
#     try:
#         print(f"Попытка загрузки изображения: {image_url}")
#         async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as response:  # Увеличен таймаут до 30 сек
#             print(f"Статус ответа для {image_url}: {response.status}")
#             if response.status == 200:
#                 image_data = await response.read()
#                 image_file = ContentFile(image_data)

#                 # Извлечение имени файла из URL (или дефолт)
#                 image_name = image_url.split("/")[-1] or f"image_{product.article_number}.jpg"
#                 if '.' not in image_name:
#                     image_name += '.jpg'  # Добавляем расширение по умолчанию

#                 product_image = ProductImage(product=product)

#                 # Сохранение изображения
#                 await sync_to_async(product_image.image.save)(
#                     image_name, image_file, save=False  # save=False, чтобы не сохранять сразу
#                 )
#                 await sync_to_async(product_image.save)()  # Сохранение в асинхронном контексте
#                 print(f"Изображение {image_name} успешно загружено для продукта {product.title}.")
#             else:
#                 print(f"Ошибка при загрузке изображения {image_url}: статус {response.status}")
#     except Exception as img_e:
#         print(f"Ошибка при загрузке изображения {image_url}: {img_e}")

# @sync_to_async
# def get_existing_images(product):
#     return ProductImage.objects.filter(product=product).exists()

# @sync_to_async
# def get_or_create_size(size_title):
#     return Size.objects.get_or_create(title=size_title)

# @sync_to_async
# def get_or_create_category_with_mptt(parent_name, child_name=None):
#     """
#     Создаёт или находит категорию в MPTT-дереве.
#     Возвращает корневую категорию (родителя) или ребёнка.
#     """
#     # Найти или создать родителя (корень дерева)
#     parent_category, created = Category.objects.get_or_create(
#         name=parent_name, parent=None, defaults={'slug': slugify(parent_name)}
#     )
    
#     if child_name:
#         # Найти или создать ребёнка под родителем
#         child_category, created = Category.objects.get_or_create(
#             name=child_name, parent=parent_category, defaults={'slug': slugify(child_name)}
#         )
#         return child_category  # Возвращаем ребёнка как категорию товара
#     else:
#         return parent_category  # Если ребёнка нет, возвращаем родителя

# @sync_to_async
# def get_or_create_product(article_number):
#     return Product.objects.filter(article_number=article_number).first()

# @sync_to_async
# def create_product(slug, title, description, is_hidden, article_number, unit, stock, category):
#     return Product.objects.create(
#         slug=slug,
#         title=title,
#         description=description,
#         is_hidden=is_hidden,
#         article_number=article_number,
#         unit=unit,
#         stock=stock,
#         category=category,
#     )

# @sync_to_async
# def save_product(product):
#     product.save()
#     return product

# @sync_to_async
# def get_or_create_product_price(product, size, defaults):
#     return ProductPrice.objects.get_or_create(product=product, size=size, defaults=defaults)

# @sync_to_async
# def update_product_price(product_price, row):
#     product_price.price = row['Цена продажи']
#     product_price.old_price = row.get('Старая цена')
#     product_price.zacup_price = row['Закупочная цена']
#     product_price.save()

# @transaction.atomic  # Атомарность для MPTT (чтобы дерево не ломалось)
# async def import_products_from_csv(file_path):
#     async with aiofiles.open(file_path, mode='r', encoding='utf-8') as csvfile:
#         # Читаем все строки асинхронно и используем csv.DictReader
#         content = await csvfile.read()
#         reader = csv.DictReader(content.splitlines())
        
#         for row in reader:
#             try:
#                 size, _ = await get_or_create_size(row['Размер'])
                
#                 # Получаем название товара
#                 title = row['Название товара']
                
#                 # Категорию всегда берем из названия товара через автоматическую категоризацию
#                 category_data = infer_category_from_title(title)
#                 parent_name = category_data['parent']
#                 child_name = category_data['child']
                
#                 # Создаём/находим категорию в MPTT-дереве
#                 category = await get_or_create_category_with_mptt(parent_name, child_name)
#                 print(f"Автоматическая категория для '{title}': {category.name} (parent: {parent_name}, child: {child_name})")

#                 article_number = row['Артикул']
#                 slug = generate_slug(title, article_number)

#                 print(f"Генерируем slug для продукта: {slug}")

#                 product = await get_or_create_product(article_number)
                
#                 if product:
#                     product.slug = slug
#                     product.title = title
#                     product.description = row['Описание товара']
#                     product.is_hidden = row['Скрыт ли товар'].strip() == '1'
#                     product.unit = row['Ед. измерения']
#                     product.stock = row['Остаток']
#                     product.category = category
#                     await save_product(product)

#                     # Обновляем или создаем цену для продукта
#                     product_price, price_created = await get_or_create_product_price(
#                         product,
#                         size,
#                         defaults={
#                             'price': row['Цена продажи'],
#                             'old_price': row.get('Старая цена'),
#                             'zacup_price': row['Закупочная цена'],
#                         }
#                     )

#                     if not price_created:
#                         # Если цена уже существует, обновляем её
#                         await update_product_price(product_price, row)
#                 else:
#                     # Если продукт не существует, создаем новый
#                     product = await create_product(
#                         slug,
#                         title,
#                         row['Описание товара'],
#                         row['Скрыт ли товар'].strip() == '1',
#                         article_number,
#                         row['Ед. измерения'],
#                         row['Остаток'],
#                         category
#                     )

#                     # Создание цены для нового продукта
#                     await get_or_create_product_price(
#                         product,
#                         size,
#                         defaults={
#                             'price': row['Цена продажи'],
#                             'old_price': row.get('Старая цена'),
#                             'zacup_price': row['Закупочная цена'],
#                         }
#                     )

#                 # Если есть URL для изображений, загружаем их
#                 if 'Изображения' in row and row['Изображения']:
#                     image_urls = row['Изображения'].strip()
#                     await import_images(image_urls, product)  # Загрузка изображений только один раз для продукта

#                 print(f"Продукт {title} успешно импортирован.")

#             except KeyError as ke:
#                 print(f"Отсутствует ключ в строке: {ke}. Пропускаем строку.")
#             except Exception as e:
#                 print(f"Ошибка при обработке строки {row}: {e}")

# # Запуск асинхронной функции импорта
# # asyncio.run(import_products_from_csv('path_to_your_csv_file.csv'))






# import csv
# import aiohttp
# import asyncio
# import aiofiles
# from django.core.files.base import ContentFile
# from asgiref.sync import sync_to_async
# from urllib.parse import urlparse
# from .models import Product, Size, ProductPrice, Category, ProductImage
# from slugify import slugify
# import signal

# def generate_slug(title, article_number):
#     slug = slugify(f"{title}-{article_number}")
#     return slug

# async def import_images(image_urls, product):
#     # Разделяем URL по переносам строк
#     image_urls = [url.strip() for url in image_urls.splitlines() if url.strip()]

#     # Проверяем, есть ли уже изображения для данного продукта
#     existing_images = await get_existing_images(product)

#     if existing_images:
#         print(f"Изображения уже загружены для продукта {product.title}. Пропускаем загрузку.")
#         return

#     async with aiohttp.ClientSession() as session:
#         for url in image_urls:
#             try:
#                 await download_image(session, url, product)
#             except asyncio.CancelledError:
#                 print(f"Импорт изображений прерван для {product.title}.")
#                 raise

# async def download_image(session, image_url, product):
#     parsed_url = urlparse(image_url.strip())
#     if not parsed_url.scheme or not parsed_url.netloc:
#         print(f"Некорректный URL для изображения: {image_url.strip()}. Пропускаем.")
#         return
    
#     try:
#         print(f"Попытка загрузки изображения: {image_url.strip()}")
#         async with session.get(image_url.strip(), timeout=aiohttp.ClientTimeout(total=10)) as response:
#             print(f"Статус ответа для {image_url.strip()}: {response.status}")
#             if response.status == 200:
#                 image_data = await response.read()
#                 image_file = ContentFile(image_data)

#                 image_name = image_url.split("/")[-1]
#                 product_image = ProductImage(product=product)

#                 await sync_to_async(product_image.image.save)(
#                     image_name, image_file
#                 )
#                 await sync_to_async(product_image.save)()
#                 print(f"Изображение {image_name} успешно загружено для продукта {product.title}.")
#             else:
#                 print(f"Ошибка при загрузке изображения {image_url.strip()}: статус {response.status}")
#     except asyncio.CancelledError:
#         raise
#     except Exception as img_e:
#         print(f"Ошибка при загрузке изображения {image_url.strip()}: {img_e}")

# @sync_to_async
# def get_existing_images(product):
#     return ProductImage.objects.filter(product=product).exists()

# @sync_to_async
# def get_or_create_size(size_title):
#     return Size.objects.get_or_create(title=size_title)

# @sync_to_async
# def get_or_create_category(name, parent=None):
#     slug = slugify(name)
#     return Category.objects.get_or_create(name=name, slug=slug, defaults={'parent': parent})

# def parse_category_from_title(full_title):
#     """
#     Парсим название товара для определения категории и подкатегории.
#     Возвращает кортеж: (parent_category_name, subcategory_name, cleaned_title)
#     Если не найдено, возвращает (None, "Без категории", full_title)
#     """
#     title_lower = full_title.lower().strip()
#     print(f"Парсинг title: '{full_title}' (lower: '{title_lower}')")  # Для отладки
    
#     # Специальные категории (расширены, проверяем первыми для приоритета; убрали 'тройк', убрали 'Товары для дома', перенесли ключи в 'НОВЫЙ ГОД')
#     special_categories = {
#         # Новый год / праздники (расширено: добавлены 'ветка', 'ветв', перенесли ключи из 'Товары для дома' — постельное, лампы, ночники и т.д.)
#         'новый год': 'НОВЫЙ ГОД', 'новогодний': 'НОВЫЙ ГОД', 'новогодняя': 'НОВЫЙ ГОД', 'новогодние': 'НОВЫЙ ГОД',
#         'новогоднего': 'НОВЫЙ ГОД', 'новогодней': 'НОВЫЙ ГОД', 'новогодних': 'НОВЫЙ ГОД', 'рождество': 'НОВЫЙ ГОД',
#         'рождественский': 'НОВЫЙ ГОД', 'рождественская': 'НОВЫЙ ГОД', 'рождественские': 'НОВЫЙ ГОД', 'праздник': 'НОВЫЙ ГОД',
#         'праздники': 'НОВЫЙ ГОД', 'праздничный': 'НОВЫЙ ГОД', 'праздничная': 'НОВЫЙ ГОД', 'новогодние аксессуары': 'НОВЫЙ ГОД',
#         'гирлянд': 'НОВЫЙ ГОД', 'гирлянда': 'НОВЫЙ ГОД', 'гирлянды': 'НОВЫЙ ГОД', 'коврик': 'НОВЫЙ ГОД', 'фейерверк': 'НОВЫЙ ГОД',
#         'ветк': 'НОВЫЙ ГОД', 'ветка': 'НОВЫЙ ГОД', 'ветв': 'НОВЫЙ ГОД', 'елочн': 'НОВЫЙ ГОД', 'елочка': 'НОВЫЙ ГОД', 'снежинк': 'НОВЫЙ ГОД',
#         'снежинка': 'НОВЫЙ ГОД', 'игрушк': 'НОВЫЙ ГОД', 'игрушка': 'НОВЫЙ ГОД', 'украшени': 'НОВЫЙ ГОД', 'украшение': 'НОВЫЙ ГОД',
#         # Перенесено из 'Товары для дома' (постельное бельё, лампы и т.д.)
#         'постельное': 'НОВЫЙ ГОД', 'постельные': 'НОВЫЙ ГОД', 'постельной': 'НОВЫЙ ГОД', 'постель': 'НОВЫЙ ГОД',
#         'постели': 'НОВЫЙ ГОД', 'белье': 'НОВЫЙ ГОД', 'белья': 'НОВЫЙ ГОД', 'белью': 'НОВЫЙ ГОД',
#         'бельем': 'НОВЫЙ ГОД', 'бель': 'НОВЫЙ ГОД', 'домашний': 'НОВЫЙ ГОД', 'домашняя': 'НОВЫЙ ГОД',
#         'домашние': 'НОВЫЙ ГОД', 'полотенц': 'НОВЫЙ ГОД', 'полотенце': 'НОВЫЙ ГОД', 'салфетк': 'НОВЫЙ ГОД',
#         'салфетки': 'НОВЫЙ ГОД', 'настольн': 'НОВЫЙ ГОД', 'кухонн': 'НОВЫЙ ГОД', 'ночной': 'НОВЫЙ ГОД',
#         'ночник': 'НОВЫЙ ГОД', 'ламп': 'НОВЫЙ ГОД', 'лампа': 'НОВЫЙ ГОД', 'светильник': 'НОВЫЙ ГОД',
#         'настольный': 'НОВЫЙ ГОД', 'ванн': 'НОВЫЙ ГОД', 'ванная': 'НОВЫЙ ГОД', 'туалет': 'НОВЫЙ ГОД',
#         # Сад, огород (расширено: добавлены 'дерев', 'кустарник', 'овощ', 'фрукт', 'ягод')
#         'сад': 'Сад, огород', 'сада': 'Сад, огород', 'огород': 'Сад, огород', 'огорода': 'Сад, огород', 'семена': 'Сад, огород',
#         'семен': 'Сад, огород', 'растения': 'Сад, огород', 'растений': 'Сад, огород', 'цветы': 'Сад, огород', 'цветов': 'Сад, огород',
#         'инструмент': 'Сад, огород', 'инструменты': 'Сад, огород', 'удобрени': 'Сад, огород', 'удобрения': 'Сад, огород',
#         'горшок': 'Сад, огород', 'горшки': 'Сад, огород', 'кашпо': 'Сад, огород', 'теплиц': 'Сад, огород', 'теплица': 'Сад, огород',
#         'саженц': 'Сад, огород', 'саженцы': 'Сад, огород', 'рассад': 'Сад, огород', 'рассада': 'Сад, огород', 'газон': 'Сад, огород',
#         'клумб': 'Сад, огород', 'клумба': 'Сад, огород', 'мебель садовая': 'Сад, огород', 'полив': 'Сад, огород', 'поливные системы': 'Сад, огород',
#         'пестицид': 'Сад, огород', 'пестициды': 'Сад, огород', 'гербицид': 'Сад, огород', 'гербициды': 'Сад, огород',
#         'компост': 'Сад, огород', 'грунт': 'Сад, огород', 'дерев': 'Сад, огород', 'дерево': 'Сад, огород', 'кустарник': 'Сад, огород',
#         'овощ': 'Сад, огород', 'фрукт': 'Сад, огород', 'ягод': 'Сад, огород',
#         # Искусственные цветы (расширено: 'декоративн', 'украшени', 'растени')
#         'искусственн': 'Искусственные цветы', 'искусственные цветы': 'Искусственные цветы', 'искусственный цветок': 'Искусственные цветы',
#         'декоративные цветы': 'Искусственные цветы', 'декоративный цветок': 'Искусственные цветы', 'декоративн': 'Искусственные цветы',
#         'украшени': 'Искусственные цветы', 'украшение': 'Искусственные цветы', 'растени': 'Искусственные цветы', 'растение': 'Искусственные цветы',
#         # Косметика (расширено: 'парфюм', 'крем', 'маска', 'лосьон')
#         'косметик': 'Косметика', 'косметика': 'Косметика', 'уход за лицом': 'Косметика', 'уход за телом': 'Косметика',
#         'уход за волосами': 'Косметика', 'макияж': 'Косметика', 'парфюмери': 'Косметика', 'парфюмерия': 'Косметика',
#         'дух': 'Косметика', 'духи': 'Косметика', 'парфюм': 'Косметика', 'крем': 'Косметика', 'маска': 'Косметика', 'лосьон': 'Косметика',
#         # Игрушки (расширено: 'кукл', 'машинк', 'конструктор')
#         'игрушк': 'Игрушки', 'игрушка': 'Игрушки', 'игрушки': 'Игрушки', 'детские игрушки': 'Игрушки', 'развивающие игрушки': 'Игрушки',
#         'кукл': 'Игрушки', 'кукла': 'Игрушки', 'машинк': 'Игрушки', 'машинка': 'Игрушки', 'конструктор': 'Игрушки',
#         # Сумки и рюкзаки (расширено: 'портфел', 'чехол')
#         'сумк': 'Сумки и рюкзаки', 'сумка': 'Сумки и рюкзаки', 'сумки': 'Сумки и рюкзаки', 'рюкзак': 'Сумки и рюкзаки',
#         'рюкзаки': 'Сумки и рюкзаки', 'портфел': 'Сумки и рюкзаки', 'портфель': 'Сумки и рюкзаки', 'чехол': 'Сумки и рюкзаки',
#         # Подарки и текстиль (убрали 'тройк', расширили: 'комплект', 'ткан')
#         'подарочн': 'Подарки и текстиль', 'подарок': 'Подарки и текстиль', 'набор': 'Подарки и текстиль', 'набора': 'Подарки и текстиль',
#         'плед': 'Подарки и текстиль', 'пледа': 'Подарки и текстиль', 'комплект': 'Подарки и текстиль',
#         'ткан': 'Подарки и текстиль', 'ткань': 'Подарки и текстиль',
#     }
    
#     # Шаг 1: Ищем специальные категории (приоритет)
#     for special_key, cat_name in special_categories.items():
#         if special_key in title_lower:
#             print(f"Найдена специальная категория: '{special_key}' -> {cat_name}")
#             return None, cat_name, full_title
    
#     # Расширенные словари для гендеров
#     gender_keywords = {
#         # Женский (расширено: 'lady', 'girl', 'woman')
#         'для женщин': 'ЖЕНСКАЯ ОДЕЖДА', 'для женщины': 'ЖЕНСКАЯ ОДЕЖДА', 'женщина': 'ЖЕНСКАЯ ОДЕЖДА', 'женские': 'ЖЕНСКАЯ ОДЕЖДА',
#         'женских': 'ЖЕНСКАЯ ОДЕЖДА', 'женщинам': 'ЖЕНСКАЯ ОДЕЖДА', 'женщинами': 'ЖЕНСКАЯ ОДЕЖДА', 'женщинах': 'ЖЕНСКАЯ ОДЕЖДА',
#         'женская': 'ЖЕНСКАЯ ОДЕЖДА', 'женской': 'ЖЕНСКАЯ ОДЕЖДА', 'женскую': 'ЖЕНСКАЯ ОДЕЖДА', 'женский': 'ЖЕНСКАЯ ОДЕЖДА',
#         'женским': 'ЖЕНСКАЯ ОДЕЖДА', 'женское': 'ЖЕНСКАЯ ОДЕЖДА', 'жен.': 'ЖЕНСКАЯ ОДЕЖДА', 'жен': 'ЖЕНСКАЯ ОДЕЖДА', 'женск': 'ЖЕНСКАЯ ОДЕЖДА',
#         'lady': 'ЖЕНСКАЯ ОДЕЖДА', 'girl': 'ЖЕНСКАЯ ОДЕЖДА', 'woman': 'ЖЕНСКАЯ ОДЕЖДА',
#         # Мужской (расширено: 'man', 'boy', 'gentleman')
#         'для мужчин': 'МУЖСКАЯ ОДЕЖДА', 'для мужчины': 'МУЖСКАЯ ОДЕЖДА', 'мужчина': 'МУЖСКАЯ ОДЕЖДА', 'мужские': 'МУЖСКАЯ ОДЕЖДА',
#         'мужских': 'МУЖСКАЯ ОДЕЖДА', 'мужчинам': 'МУЖСКАЯ ОДЕЖДА', 'мужчинами': 'МУЖСКАЯ ОДЕЖДА', 'мужчинах': 'МУЖСКАЯ ОДЕЖДА',
#         'мужская': 'МУЖСКАЯ ОДЕЖДА', 'мужской': 'МУЖСКАЯ ОДЕЖДА', 'мужскую': 'МУЖСКАЯ ОДЕЖДА', 'муж.': 'МУЖСКАЯ ОДЕЖДА',
#         'муж': 'МУЖСКАЯ ОДЕЖДА', 'мужск': 'МУЖСКАЯ ОДЕЖДА', 'man': 'МУЖСКАЯ ОДЕЖДА', 'boy': 'МУЖСКАЯ ОДЕЖДА', 'gentleman': 'МУЖСКАЯ ОДЕЖДА',
#         # Детский (расширено: 'kid', 'child', 'baby')
#         'для детей': 'ДЕТСКАЯ ОДЕЖДА', 'для ребенка': 'ДЕТСКАЯ ОДЕЖДА', 'ребенок': 'ДЕТСКАЯ ОДЕЖДА', 'ребенка': 'ДЕТСКАЯ ОДЕЖДА',
#         'дети': 'ДЕТСКАЯ ОДЕЖДА', 'детская': 'ДЕТСКАЯ ОДЕЖДА', 'детской': 'ДЕТСКАЯ ОДЕЖДА', 'детскую': 'ДЕТСКАЯ ОДЕЖДА',
#         'детские': 'ДЕТСКАЯ ОДЕЖДА', 'детских': 'ДЕТСКАЯ ОДЕЖДА', 'дет': 'ДЕТСКАЯ ОДЕЖДА', 'детск': 'ДЕТСКАЯ ОДЕЖДА',
#         'kid': 'ДЕТСКАЯ ОДЕЖДА', 'child': 'ДЕТСКАЯ ОДЕЖДА', 'baby': 'ДЕТСКАЯ ОДЕЖДА',
#         # Подростковый (расширено: 'teen', 'youth')
#         'для подростков': 'ДЕТСКАЯ ОДЕЖДА', 'подросток': 'ДЕТСКАЯ ОДЕЖДА', 'подростки': 'ДЕТСКАЯ ОДЕЖДА', 'подростков': 'ДЕТСКАЯ ОДЕЖДА',
#         'подростковая': 'ДЕТСКАЯ ОДЕЖДА', 'подростковой': 'ДЕТСКАЯ ОДЕЖДА', 'подрос': 'ДЕТСКАЯ ОДЕЖДА', 'teen': 'ДЕТСКАЯ ОДЕЖДА', 'youth': 'ДЕТСКАЯ ОДЕЖДА',
#     }
    
#     # Словари для подкатегорий по гендерам (разделены, расширены: добавлены дублёнки, гендер к общим категориям)
#     subcategory_mappings = {
#         'ЖЕНСКАЯ ОДЕЖДА': {
#             # Рубашки, блузки
#             'рубашк': 'Рубашки, блузки', 'рубашка': 'Рубашки, блузки', 'рубашки': 'Рубашки, блузки', 'рубашек': 'Рубашки, блузки',
#             'блузк': 'Рубашки, блузки', 'блузка': 'Рубашки, блузки', 'блузки': 'Рубашки, блузки', 'блузок': 'Рубашки, блузки',
#             # Обувь (расширено: 'балетк', 'сапог', 'ботильон')
#             'обув': 'Обувь женская', 'обувь': 'Обувь женская', 'ботинк': 'Обувь женская', 'ботинки': 'Обувь женская', 'туфл': 'Обувь женская',
#             'тапочк': 'Обувь женская', 'тапочки': 'Обувь женская', 'сандал': 'Обувь женская', 'кроссовк': 'Обувь женская', 'балетк': 'Обувь женская',
#             'балетки': 'Обувь женская', 'сапог': 'Обувь женская', 'ботильон': 'Обувь женская',
#             # Свитеры, джемперы (гендер-специфично)
#             'свитер': 'Джемпер, свитер женский', 'свитера': 'Джемпер, свитер женский', 'джемпер': 'Джемпер, свитер женский', 'джемпера': 'Джемпер, свитер женский',
#             'кофт': 'Джемпер, свитер женский', 'кофта': 'Джемпер, свитер женский', 'кардиган': 'Джемпер, свитер женский',
#             # Верхняя одежда (добавлен бомбер, дублёнка)
#             'куртк': 'Верхняя одежда женская', 'куртка': 'Верхняя одежда женская', 'куртки': 'Верхняя одежда женская',
#             'пальт': 'Верхняя одежда женская', 'пальто': 'Верхняя одежда женская', 'плащ': 'Верхняя одежда женская',
#             'бомбер': 'Верхняя одежда женская', 'дублёнк': 'Верхняя одежда женская', 'дублёнка': 'Верхняя одежда женская',
#             # Платья, туники
#             'плат': 'Платья', 'платье': 'Платья', 'платья': 'Платья', 'туник': 'Платья', 'туника': 'Платья',
#             # Юбки
#             'юбк': 'Юбки', 'юбка': 'Юбки', 'юбки': 'Юбки',
#             # Джинсы, брюки, шорты (разделены)
#             'джинс': 'Джинсы женские', 'джинсы': 'Джинсы женские',
#             'брюк': 'Брюки женские', 'брюки': 'Брюки женские',
#             'шорт': 'Шорты женские', 'шорты': 'Шорты женские',
#             'леггин': 'Леггинсы женские', 'леггинсы': 'Леггинсы женские',
#             # Толстовки, свитшоты (гендер-специфично)
#             'толстовк': 'Толстовки, свитшоты женские', 'толстовка': 'Толстовки, свитшоты женские',
#             # Футболки, майки, топы
#             'футболк': 'Футболки, майки', 'футболка': 'Футболки, майки', 'майк': 'Футболки, майки', 'майка': 'Футболки, майки',
#             'топ': 'Футболки, майки', 'топа': 'Футболки, майки',
#             # Костюмы (добавлена тройка)
#             'костюм': 'Костюмы женские', 'костюма': 'Костюмы женские', 'костюмы': 'Костюмы женские', 'тройк': 'Костюмы женские',
#             # Пижамы (отдельная подкатегория)
#             'пижам': 'Пижамы женские', 'пижама': 'Пижамы женские',
#             # Халаты (отдельная подкатегория)
#             'халат': 'Халаты женские',
#             # Купальники, нижнее белье
#             'купальник': 'Купальники, нижнее белье', 'купальники': 'Купальники, нижнее белье', 'бель': 'Купальники, нижнее белье',
#             'белье': 'Купальники, нижнее белье', 'лифчик': 'Купальники, нижнее белье', 'трусики': 'Купальники, нижнее белье',
#             # Колготки, носки (гендер-специфично)
#             'колготк': 'Колготки женские', 'колготки': 'Колготки женские', 'носок': 'Колготки женские', 'носки': 'Колготки женские',
#             # Аксессуары (расширено: 'бижутери', 'ювелирк', 'браслет', 'серьги')
#             'шарф': 'Аксессуары женские', 'шарфы': 'Аксессуары женские', 'перчатк': 'Аксессуары женские', 'перчатки': 'Аксессуары женские',
#             'шляп': 'Аксессуары женские', 'шляпа': 'Аксессуары женские', 'очки': 'Аксессуары женские', 'очки солнцезащитные': 'Аксессуары женские',
#             'ремень': 'Аксессуары женские', 'ремни': 'Аксессуары женские', 'сумк': 'Аксессуары женские', 'сумка': 'Аксессуары женские',
#             'рюкзак': 'Аксессуары женские', 'рюкзаки': 'Аксессуары женские', 'бижутери': 'Аксессуары женские', 'бижутерия': 'Аксессуары женские',
#             'ювелирк': 'Аксессуары женские', 'ювелирка': 'Аксессуары женские', 'браслет': 'Аксессуары женские', 'серьги': 'Аксессуары женские',
#             # Другие
#             'боди': 'Боди, комбинезоны', 'боди': 'Боди, комбинезоны', 'комбинезон': 'Боди, комбинезоны', 'комбинезоны': 'Боди, комбинезоны',
#             'лосин': 'Лосины, леггинсы', 'лосины': 'Лосины, леггинсы', 'леггинс': 'Лосины, леггинсы', 'леггинсы': 'Лосины, леггинсы',
#         },
#         'МУЖСКАЯ ОДЕЖДА': {
#             # Аналогично расширено: рубахи, обувь, свитеры (гендер-специфично), верхняя одежда (дублёнка), брюки/джинсы/шорты, футболки, костюмы, пижамы, халаты, белье, носки, аксессуары
#             'рубашк': 'Рубашки', 'рубашка': 'Рубашки', 'рубашки': 'Рубашки', 'рубашек': 'Рубашки',
#             'обув': 'Обувь мужская', 'обувь': 'Обувь мужская', 'ботинк': 'Обувь мужская', 'ботинки': 'Обувь мужская',
#             'тапочк': 'Обувь мужская', 'тапочки': 'Обувь мужская', 'кроссовк': 'Обувь мужская', 'кроссовки': 'Обувь мужская',
#             'кед': 'Обувь мужская', 'кеды': 'Обувь мужская',
#             'свитер': 'Джемпер, свитер мужской', 'свитера': 'Джемпер, свитер мужской', 'джемпер': 'Джемпер, свитер мужской', 'джемпера': 'Джемпер, свитер мужской',
#             'кофт': 'Джемпер, свитер мужской', 'кофта': 'Джемпер, свитер мужской',
#             'куртк': 'Верхняя одежда мужская', 'куртка': 'Верхняя одежда мужская', 'куртки': 'Верхняя одежда мужская',
#             'пальт': 'Верхняя одежда мужская', 'пальто': 'Верхняя одежда мужская', 'плащ': 'Верхняя одежда мужская',
#             'дублёнк': 'Верхняя одежда мужская', 'дублёнка': 'Верхняя одежда мужская',
#             'джинс': 'Джинсы мужские', 'джинсы': 'Джинсы мужские',
#             'брюк': 'Брюки мужские', 'брюки': 'Брюки мужские',
#             'шорт': 'Шорты мужские', 'шорты': 'Шорты мужские',
#             'леггин': 'Леггинсы мужские', 'леггинсы': 'Леггинсы мужские',
#             'толстовк': 'Толстовки, свитшоты мужские', 'толстовка': 'Толстовки, свитшоты мужские',
#             'футболк': 'Футболки, майки', 'футболка': 'Футболки, майки', 'майк': 'Футболки, майки', 'майка': 'Футболки, майки',
#             'топ': 'Футболки, майки', 'топа': 'Футболки, майки',
#             'костюм': 'Костюмы мужские', 'костюма': 'Костюмы мужские', 'костюмы': 'Костюмы мужские', 'смокинг': 'Костюмы мужские',
#             'фрак': 'Костюмы мужские', 'тройк': 'Костюмы мужские',
#             'пижам': 'Пижамы мужские', 'пижама': 'Пижамы мужские',
#             'халат': 'Халаты мужские',
#             'плавк': 'Купальники, нижнее белье', 'плавки': 'Купальники, нижнее белье', 'бель': 'Купальники, нижнее белье',
#             'белье': 'Купальники, нижнее белье', 'трусы': 'Купальники, нижнее белье',
#             'носок': 'Носки мужские', 'носки': 'Носки мужские',
#             'галстук': 'Аксессуары мужские', 'галстуки': 'Аксессуары мужские', 'ремень': 'Аксессуары мужские', 'ремни': 'Аксессуары мужские',
#             'очки': 'Аксессуары мужские', 'очки солнцезащитные': 'Аксессуары мужские', 'шарф': 'Аксессуары мужские', 'шарфы': 'Аксессуары мужские',
#             'перчатк': 'Аксессуары мужские', 'перчатки': 'Аксессуары мужские', 'шляп': 'Аксессуары мужские', 'шляпа': 'Аксессуары мужские',
#             'сумк': 'Аксессуары мужские', 'сумка': 'Аксессуары мужские', 'рюкзак': 'Аксессуары мужские', 'рюкзаки': 'Аксессуары мужские',
#             'боди': 'Боди, комбинезоны', 'боди': 'Боди, комбинезоны', 'комбинезон': 'Боди, комбинезоны', 'комбинезоны': 'Боди, комбинезоны',
#         },
#         'ДЕТСКАЯ ОДЕЖДА': {
#             # Аналогично: рубахи, обувь, свитеры (гендер-специфично), верхняя одежда (дублёнка), платья/юбки, джинсы/брюки/шорты, футболки, костюмы, пижамы, халаты, колготки, аксессуары, боди
#             'рубашк': 'Рубашки, блузки', 'рубашка': 'Рубашки, блузки', 'рубашки': 'Рубашки, блузки', 'блузк': 'Рубашки, блузки',
#             'блузка': 'Рубашки, блузки', 'блузки': 'Рубашки, блузки',
#             'обув': 'Обувь детская', 'обувь': 'Обувь детская', 'ботинк': 'Обувь детская', 'ботинки': 'Обувь детская', 'тапочк': 'Обувь детская',
#             'тапочки': 'Обувь детская', 'кроссовк': 'Обувь детская', 'сандал': 'Обувь детская', 'кед': 'Обувь детская', 'кеды': 'Обувь детская',
#             'свитер': 'Джемпер, свитер детский', 'свитера': 'Джемпер, свитер детский', 'джемпер': 'Джемпер, свитер детский', 'джемпера': 'Джемпер, свитер детский',
#             'кофт': 'Джемпер, свитер детский', 'кофта': 'Джемпер, свитер детский',
#             'куртк': 'Верхняя одежда детская', 'куртка': 'Верхняя одежда детская', 'куртки': 'Верхняя одежда детская',
#             'пальт': 'Верхняя одежда детская', 'пальто': 'Верхняя одежда детская', 'плащ': 'Верхняя одежда детская',
#             'дублёнк': 'Верхняя одежда детская', 'дублёнка': 'Верхняя одежда детская',
#             'плат': 'Платья', 'платье': 'Платья', 'платья': 'Платья', 'туник': 'Платья', 'туника': 'Платья',
#             'юбк': 'Юбки', 'юбка': 'Юбки', 'юбки': 'Юбки',
#             'джинс': 'Джинсы детские', 'джинсы': 'Джинсы детские',
#             'брюк': 'Брюки детские', 'брюки': 'Брюки детские',
#             'шорт': 'Шорты детские', 'шорты': 'Шорты детские',
#             'толстовк': 'Толстовки, свитшоты детские', 'толстовка': 'Толстовки, свитшоты детские',
#             'футболк': 'Футболки, майки', 'футболка': 'Футболки, майки', 'майк': 'Футболки, майки', 'майка': 'Футболки, майки',
#             'топ': 'Футболки, майки', 'топа': 'Футболки, майки',
#             'костюм': 'Костюмы детские', 'костюма': 'Костюмы детские', 'костюмы': 'Костюмы детские', 'тройк': 'Костюмы детские',
#             'пижам': 'Пижамы детские', 'пижама': 'Пижамы детские',
#             'халат': 'Халаты детские',
#             'колготк': 'Колготки детские', 'колготки': 'Колготки детские', 'носок': 'Колготки детские', 'носки': 'Колготки детские',
#             'шарф': 'Аксессуары детские', 'шарфы': 'Аксессуары детские', 'перчатк': 'Аксессуары детские', 'перчатки': 'Аксессуары детские',
#             'шапка': 'Аксессуары детские', 'шапки': 'Аксессуары детские', 'сумк': 'Аксессуары детские', 'сумка': 'Аксессуары детские',
#             'рюкзак': 'Аксессуары детские', 'рюкзаки': 'Аксессуары детские', 'очки': 'Аксессуары детские', 'очки солнцезащитные': 'Аксессуары детские',
#             'боди': 'Боди, комбинезоны', 'боди': 'Боди, комбинезоны', 'комбинезон': 'Боди, комбинезоны', 'комбинезоны': 'Боди, комбинезоны',
#         }
#     }
    
#     parent_name = None
#     found_gender_key = None
#     # Шаг 2: Ищем гендер
#     for gender_key, p_name in gender_keywords.items():
#         if gender_key in title_lower:
#             parent_name = p_name
#             found_gender_key = gender_key
#             print(f"Найден гендер: '{gender_key}' -> {parent_name}")
#             break
    
#     subcategory_name = None
#     cleaned_title = full_title
    
#     if parent_name:
#         # Ищем подкатегорию
#         subs = subcategory_mappings.get(parent_name, {})
#         for sub_key, sub_name in subs.items():
#             if sub_key in title_lower:
#                 subcategory_name = sub_name
#                 print(f"Найдена подкатегория: '{sub_key}' -> {sub_name}")
#                 break
        
#         if not subcategory_name:
#             subcategory_name = parent_name
#             print(f"Подкатегория не найдена, fallback на {parent_name}")
        
#         # Очистка title (улучшена)
#         if found_gender_key:
#             cleaned_title = full_title.replace(f" {found_gender_key} ", " ").strip()
#             if cleaned_title == full_title:
#                 if title_lower.startswith(found_gender_key + " "):
#                     cleaned_title = full_title[len(found_gender_key) + 1:].strip()
#                 elif title_lower.endswith(" " + found_gender_key):
#                     cleaned_title = full_title[:-len(found_gender_key) - 1].strip()
#             print(f"Очищенный title: '{cleaned_title}' (удален гендер: '{found_gender_key}')")
#         return parent_name, subcategory_name, cleaned_title
    
#     # Шаг 3: Fallback
#     print("Ничего не найдено, fallback на 'Без категории'")
#     return None, "Без категории", full_title


# @sync_to_async
# def get_or_create_product(article_number):
#     return Product.objects.filter(article_number=article_number).first()

# @sync_to_async
# def create_product(slug, title, description, is_hidden, article_number, unit, stock, category):
#     return Product.objects.create(
#         slug=slug,
#         title=title,
#         description=description,
#         is_hidden=is_hidden,
#         article_number=article_number,
#         unit=unit,
#         stock=stock,
#         category=category,
#     )

# @sync_to_async
# def save_product(product):
#     product.save()
#     return product

# @sync_to_async
# def get_or_create_product_price(product, size, defaults):
#     return ProductPrice.objects.get_or_create(product=product, size=size, defaults=defaults)

# @sync_to_async
# def update_product_price(product_price, row):
#     product_price.price = row['Цена продажи']
#     product_price.old_price = row.get('Старая цена')
#     product_price.zacup_price = row['Закупочная цена']
#     product_price.save()

# async def import_products_from_csv(file_path):
#     # Функция для чтения CSV в отдельном потоке (синхронно)
#     def read_csv():
#         with open(file_path, mode='r', encoding='utf-8') as csvfile:
#             reader = csv.DictReader(csvfile)
#             return list(reader)  # Возвращаем список всех строк для асинхронной обработки

#     # Читаем CSV в фоне
#     rows = await asyncio.to_thread(read_csv)
#     total_rows = len(rows)
#     print(f"Начинаем импорт {total_rows} продуктов из {file_path}.")

#     processed = 0
#     for row in rows:
#         try:
#             size, _ = await get_or_create_size(row['Размер'])
            
#             full_title = row['Название товара'].strip()
#             parent_name, subcategory_name, cleaned_title = parse_category_from_title(full_title)
            
#             try:
#                 if parent_name:
#                     parent_category, _ = await get_or_create_category(parent_name)
#                     category, _ = await get_or_create_category(subcategory_name, parent=parent_category)
#                     print(f"Создана иерархия: {parent_name} > {subcategory_name}")
#                 else:
#                     category, _ = await get_or_create_category(subcategory_name)
#                     print(f"Создана категория: {subcategory_name}")
#             except Exception as cat_e:
#                 print(f"Ошибка создания категории для '{full_title}': {cat_e}. Fallback на 'Без категории'.")
#                 category, _ = await get_or_create_category("Без категории")
            
#             article_number = row['Артикул']
#             slug = generate_slug(cleaned_title, article_number)

#             print(f"Генерируем slug для продукта: {slug}")

#             product = await get_or_create_product(article_number)
            
#             if product:
#                 product.slug = slug
#                 product.title = cleaned_title
#                 product.description = row['Описание товара']
#                 product.is_hidden = row['Скрыт ли товар'].strip() == '1'
#                 product.unit = row['Ед. измерения']
#                 product.stock = row['Остаток']
#                 product.category = category
#                 await save_product(product)

#                 product_price, price_created = await get_or_create_product_price(
#                     product,
#                     size,
#                     defaults={
#                         'price': row['Цена продажи'],
#                         'old_price': row.get('Старая цена'),
#                         'zacup_price': row['Закупочная цена'],
#                     }
#                 )

#                 if not price_created:
#                     await update_product_price(product_price, row)
#             else:
#                 product = await create_product(
#                     slug,
#                     cleaned_title,
#                     row['Описание товара'],
#                     row['Скрыт ли товар'].strip() == '1',
#                     article_number,
#                     row['Ед. измерения'],
#                     row['Остаток'],
#                     category
#                 )

#                 await get_or_create_product_price(
#                     product,
#                     size,
#                     defaults={
#                         'price': row['Цена продажи'],
#                         'old_price': row.get('Старая цена'),
#                         'zacup_price': row['Закупочная цена'],
#                     }
#                 )

#             if 'Изображения' in row and row['Изображения']:
#                 image_urls = row['Изображения'].strip()
#                 try:
#                     await import_images(image_urls, product)
#                 except asyncio.CancelledError:
#                     print(f"Прерывание загрузки изображений для {product.title}.")
#                     break

#             print(f"Продукт {cleaned_title} успешно импортирован в категорию '{subcategory_name}'.")
            
#             processed += 1
#             if processed % 100 == 0:  # Логируем прогресс каждые 100 строк
#                 print(f"Обработано {processed}/{total_rows} продуктов.")

#         except KeyboardInterrupt:
#             print(f"\nИмпорт прерван пользователем на строке {processed + 1}. Завершаем gracefully.")
#             break
#         except Exception as e:
#             print(f"Ошибка при обработке строки {processed + 1} ({row.get('Название товара', 'N/A')}): {e}")
#             continue

#     print(f"Импорт завершён. Обработано {processed} из {total_rows} продуктов.")

# def run_import(file_path):
#     try:
#         asyncio.run(import_products_from_csv(file_path))
#     except KeyboardInterrupt:
#         print("Импорт завершён пользователем.")






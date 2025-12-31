# # старый рабочий
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










# # последний рабочий асинхронная версия
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















# # синхронная версия
# import csv
# import os
# import requests
# from django.core.files.base import ContentFile
# from .models import Product, Size, ProductPrice, Category, ProductImage
# from slugify import slugify
# from django.db.models import Q

# def generate_slug(title, article_number):
#     slug = slugify(f"{title}-{article_number}")
#     return slug

# def get_existing_images(product):
#     return ProductImage.objects.filter(product=product).exists()

# def import_images(image_urls, product):
#     # Разделяем URL по переносам строк
#     image_urls = [url.strip() for url in image_urls.splitlines() if url.strip()]

#     # Проверяем, есть ли уже изображения для данного продукта
#     if get_existing_images(product):
#         print(f"Изображения уже загружены для продукта {product.title}. Пропускаем загрузку.")
#         return  # Если изображения уже существуют, пропускаем загрузку

#     for url in image_urls:  # Загружаем изображения последовательно
#         download_image(url, product)

# def download_image(image_url, product):
#     try:
#         print(f"Попытка загрузки изображения: {image_url.strip()}")
#         response = requests.get(image_url.strip(), timeout=10)
#         print(f"Статус ответа для {image_url.strip()}: {response.status_code}")
#         if response.status_code == 200:
#             image_data = response.content
#             image_file = ContentFile(image_data)

#             # Извлечение имени файла из URL
#             image_name = os.path.basename(image_url.strip())
#             if not image_name:
#                 image_name = 'image.jpg'  # Дефолтное имя, если не извлекли

#             product_image = ProductImage(product=product)
#             product_image.image.save(image_name, image_file, save=False)
#             product_image.save()
#             print(f"Изображение {image_name} успешно загружено для продукта {product.title}.")
#         else:
#             print(f"Ошибка при загрузке изображения {image_url.strip()}: статус {response.status_code}")
#     except Exception as img_e:
#         print(f"Ошибка при загрузке изображения {image_url.strip()}: {img_e}")

# def get_or_create_size(size_title):
#     if not size_title or not size_title.strip():
#         return None, False
#     normalized_title = size_title.strip().upper()
#     size, created = Size.objects.get_or_create(
#         title__iexact=normalized_title,  # Используйте фильтр с iexact
#         defaults={'title': size_title.strip()}  # Сохраняйте оригинальный title
#     )
#     return size, created

# def get_or_create_category(category_name):
#     if not category_name or not category_name.strip():
#         # Дефолтная категория
#         category, created = Category.objects.get_or_create(
#             name='Без категории',
#             defaults={'slug': slugify('Без категории')}
#         )
#         return category, created
#     category_slug = slugify(category_name.strip())
#     return Category.objects.get_or_create(name=category_name.strip(), slug=category_slug)

# def get_or_create_product(article_number):
#     try:
#         return Product.objects.filter(article_number=int(article_number)).first()
#     except (ValueError, TypeError):
#         # Если article_number не число, возвращаем None
#         return None

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

# def save_product(product):
#     product.save()
#     return product

# def get_or_create_product_price(product, size, defaults):
#     return ProductPrice.objects.get_or_create(product=product, size=size, defaults=defaults)

# def update_product_price(product_price, row):
#     product_price.price = row['Цена продажи']
#     product_price.old_price = row.get('Старая цена', '')
#     product_price.zacup_price = row['Закупочная цена']
#     product_price.save()

# def import_products_from_csv(file_path):
#     """Синхронная главная функция импорта из CSV."""
#     if not os.path.exists(file_path):
#         print(f"Файл не найден: {file_path}")
#         return
    
#     with open(file_path, 'r', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             try:
#                 # Получаем или создаём размер
#                 size, _ = get_or_create_size(row.get('Размер', ''))
#                 if not size:
#                     size = None  # Если пустой размер, используем None

#                 # Получаем или создаём категорию
#                 category_name = row.get('Категория', '')
#                 category, _ = get_or_create_category(category_name)

#                 title = row.get('Название товара', '').strip()
#                 if not title:
#                     print("Пропуск строки: нет названия товара.")
#                     continue

#                 article_number_str = row.get('Артикул', '').strip()
#                 try:
#                     article_number = int(article_number_str)
#                 except (ValueError, TypeError):
#                     print(f"Пропуск строки: неверный артикул {article_number_str}.")
#                     continue

#                 slug = generate_slug(title, article_number)
#                 print(f"Генерируем slug для продукта: {slug}")

#                 product = get_or_create_product(article_number)
                
#                 if product:
#                     # Обновляем существующий продукт
#                     product.slug = slug
#                     product.title = title
#                     product.description = row.get('Описание товара', '')
#                     product.is_hidden = row.get('Скрыт ли товар', '0').strip() == '1'
#                     product.unit = row.get('Ед. измерения', '')
#                     product.stock = row.get('Остаток', 0)
#                     product.category = category
#                     save_product(product)

#                     # Обновляем или создаем цену для продукта
#                     product_price, price_created = get_or_create_product_price(
#                         product,
#                         size,
#                         defaults={
#                             'price': float(row.get('Цена продажи', 0)) if row.get('Цена продажи') else 0,
#                             'old_price': row.get('Старая цена', ''),
#                             'zacup_price': row.get('Закупочная цена', 0),
#                         }
#                     )

#                     if not price_created:
#                         # Если цена уже существует, обновляем её
#                         update_product_price(product_price, row)
#                 else:
#                     # Если продукт не существует, создаем новый
#                     product = create_product(
#                         slug,
#                         title,
#                         row.get('Описание товара', ''),
#                         row.get('Скрыт ли товар', '0').strip() == '1',
#                         article_number,
#                         row.get('Ед. измерения', ''),
#                         row.get('Остаток', 0),
#                         category
#                     )

#                     # Создание цены для нового продукта
#                     get_or_create_product_price(
#                         product,
#                         size,
#                         defaults={
#                             'price': float(row.get('Цена продажи', 0)) if row.get('Цена продажи') else 0,
#                             'old_price': row.get('Старая цена', ''),
#                             'zacup_price': row.get('Закупочная цена', 0),
#                         }
#                     )

#                 # Если есть URL для изображений, загружаем их
#                 image_urls = row.get('Изображения', '').strip()
#                 if image_urls:
#                     import_images(image_urls, product)  # Загрузка изображений только один раз для продукта

#                 print(f"Продукт {title} успешно импортирован.")

#             except KeyError as e:
#                 print(f"Ошибка: отсутствует ключ в CSV строке {row}: {e}")
#             except Exception as e:
#                 print(f"Ошибка при обработке строки {row}: {e}")
    
#     print("Импорт завершён.")









# # синхронная версия
# import csv
# import os
# import requests
# from django.core.files.base import ContentFile
# from .models import Product, Size, ProductPrice, Category, ProductImage
# from slugify import slugify

# def generate_slug(title, article_number):
#     slug = slugify(f"{title}-{article_number}")
#     return slug

# def get_existing_images(product):
#     return ProductImage.objects.filter(product=product).exists()

# def import_images(image_urls, product):
#     # Разделяем URL по переносам строк
#     image_urls = [url.strip() for url in image_urls.splitlines() if url.strip()]

#     # Проверяем, есть ли уже изображения для данного продукта
#     if get_existing_images(product):
#         print(f"Изображения уже загружены для продукта {product.title}. Пропускаем загрузку.")
#         return  # Если изображения уже существуют, пропускаем загрузку

#     for url in image_urls:  # Загружаем изображения последовательно
#         download_image(url, product)

# def download_image(image_url, product):
#     try:
#         print(f"Попытка загрузки изображения: {image_url.strip()}")
#         response = requests.get(image_url.strip(), timeout=10)
#         print(f"Статус ответа для {image_url.strip()}: {response.status_code}")
#         if response.status_code == 200:
#             image_data = response.content
#             image_file = ContentFile(image_data)

#             # Извлечение имени файла из URL
#             image_name = os.path.basename(image_url.strip())
#             if not image_name:
#                 image_name = 'image.jpg'  # Дефолтное имя, если не извлекли

#             product_image = ProductImage(product=product)
#             product_image.image.save(image_name, image_file, save=False)
#             product_image.save()
#             print(f"Изображение {image_name} успешно загружено для продукта {product.title}.")
#         else:
#             print(f"Ошибка при загрузке изображения {image_url.strip()}: статус {response.status_code}")
#     except Exception as img_e:
#         print(f"Ошибка при загрузке изображения {image_url.strip()}: {img_e}")

# def get_or_create_size(size_title):
#     if not size_title or not size_title.strip():
#         return None, False
#     normalized_title = size_title.strip().upper()
#     size, created = Size.objects.get_or_create(
#         title__iexact=normalized_title,  
#         defaults={'title': size_title.strip()}
#     )
#     return size, created

# def get_or_create_category(category_name):
#     if not category_name or not category_name.strip():
#         # Дефолтная категория
#         category, created = Category.objects.get_or_create(
#             name='Без категории',
#             defaults={'slug': slugify('Без категории')}
#         )
#         return category, created
#     category_slug = slugify(category_name.strip())
#     return Category.objects.get_or_create(name=category_name.strip(), slug=category_slug)

# def get_or_create_product(article_number):
#     try:
#         return Product.objects.filter(article_number=int(article_number)).first()
#     except (ValueError, TypeError):
#         # Если article_number не число, возвращаем None
#         return None

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

# def save_product(product):
#     product.save()
#     return product

# def get_or_create_product_price(product, size, defaults):
#     return ProductPrice.objects.get_or_create(product=product, size=size, defaults=defaults)

# def update_product_price(product_price, row):
#     product_price.price = row['Цена продажи, без учёта скидок']
#     product_price.old_price = row.get('Старая цена', '')
#     product_price.zacup_price = row['Закупочная цена']
#     product_price.save()

# def import_products_from_csv(file_path):
#     """Синхронная главная функция импорта из CSV."""
#     if not os.path.exists(file_path):
#         print(f"Файл не найден: {file_path}")
#         return
    
#     successful_imports = 0
#     errors = []  # Список словарей: {'row_num': int, 'row': dict, 'error': str}
    
#     with open(file_path, 'r', encoding='windows-1251') as csvfile:
#         reader = csv.DictReader(csvfile, delimiter=';')
#         for row_num, row in enumerate(reader, start=2):  # Нумерация строк, начиная с 2 (1 - заголовки)
#             try:
#                 def parse_price(price_str):
#                     if not price_str:
#                         return 0.0
#                     cleaned = str(price_str).replace(' ', '').replace(',', '.').strip()
#                     try:
#                         return float(cleaned)
#                     except ValueError:
#                         return 0.0  # Возврат 0, если формат некорректный (для безопасности)
#                 # Получаем или создаём размер
#                 size, _ = get_or_create_size(row.get('Значение св-ва для модификации товара №1', ''))
#                 if not size:
#                     size = None  # Если пустой размер, используем None

#                 # Получаем или создаём категорию
#                 # category_name = row.get('Категория', '')
#                 # category_name = ''
#                 # category, _ = get_or_create_category(category_name)
#                 category, _ = get_or_create_category('')

#                 title = row.get('Название товара', '').strip()
#                 if not title:
#                     raise ValueError("Пропуск строки: нет названия товара.")

#                 article_number_str = row.get('Артикул', '').strip()
#                 try:
#                     article_number = int(article_number_str)
#                 except (ValueError, TypeError):
#                     raise ValueError(f"Пропуск строки: неверный артикул {article_number_str}.")

#                 slug = generate_slug(title, article_number)
#                 print(f"Генерируем slug для продукта: {slug}")

#                 product = get_or_create_product(article_number)
#                 stock = 100
                
#                 if product:
#                     # Обновляем существующий продукт
#                     product.slug = slug
#                     product.title = title
#                     product.description = row.get('Полное описание товара', '')
#                     product.is_hidden = row.get('Скрыт ли товар на сайте?', '0').strip() == '1'
#                     product.unit = row.get('Ед. измерения', '')
#                     # product.stock = row.get('Остаток', 0)
#                     product.stock = stock
#                     product.category = category
#                     save_product(product)

#                     # Обновляем или создаем цену для продукта
#                     product_price, price_created = get_or_create_product_price(
#                         product,
#                         size,
#                         defaults={
#                             'price': parse_price(row.get('Цена продажи, без учёта скидок', 0)),
#                             'old_price': parse_price(row.get('Старая цена', '')),
#                             'zacup_price': parse_price(row.get('Закупочная цена', 0)),
#                         }
#                     )

#                     if not price_created:
#                         # Если цена уже существует, обновляем её
#                         update_product_price(product_price, row)
#                 else:
#                     # Если продукт не существует, создаем новый
#                     product = create_product(
#                         slug,
#                         title,
#                         row.get('Полное описание товара', ''),
#                         row.get('Скрыт ли товар на сайте?', '0').strip() == '1',
#                         article_number,
#                         row.get('Ед. измерения', ''),
#                         # row.get('Остаток', 0),
#                         stock,
#                         category
#                     )

#                     # Создание цены для нового продукта
#                     get_or_create_product_price(
#                         product,
#                         size,
#                         defaults={
#                             'price': parse_price(row.get('Цена продажи, без учёта скидок', 0)),
#                             'old_price': parse_price(row.get('Старая цена', '')),
#                             'zacup_price': parse_price(row.get('Закупочная цена', 0)),
#                         }
#                     )

#                 # Если есть URL для изображений, загружаем их
#                 image_urls = row.get('Изображения товара', '').strip()
#                 if image_urls:
#                     import_images(image_urls, product)  # Загрузка изображений только один раз для продукта

#                 successful_imports += 1
#                 print(f"Продукт {title} успешно импортирован из строки {row_num}.")

#             except KeyError as e:
#                 error_msg = f"Ошибка: отсутствует ключ в CSV строке {row_num} (артикул: {row.get('Артикул', '?')}): {e}"
#                 errors.append({'row_num': row_num, 'row': dict(row), 'error': error_msg})
#                 print(error_msg)
#             except Exception as e:
#                 error_msg = f"Ошибка при обработке строки {row_num} (артикул: {row.get('Артикул', '?')}): {e}"
#                 errors.append({'row_num': row_num, 'row': dict(row), 'error': error_msg})
#                 print(error_msg)
    
#     total_processed = successful_imports + len(errors)
#     failed_count = len(errors)
    
#     print("\nИмпорт завершён.")
#     print(f"Всего обработано строк (товаров): {total_processed}")
#     print(f"Успешно импортировано: {successful_imports}")
#     print(f"Не импортировано (с ошибками): {failed_count}")
    
#     if errors:
#         print("\nПодробности ошибок:")
#         for err in errors:
#             print(f"- Строка {err['row_num']}: {err['error']} (Название: {err['row'].get('Название товара', 'N/A')}, Артикул: {err['row'].get('Артикул', 'N/A')})")









import csv
import os
import time
import requests
from django.core.files.base import ContentFile
from django.db import connection
from .models import Product, Size, ProductPrice, Category, ProductImage
from slugify import slugify

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
        title__iexact=normalized_title,  
        defaults={'title': size_title.strip()}
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
    product_price.price = row['Цена продажи, без учёта скидок']
    product_price.old_price = row.get('Старая цена', '')
    product_price.zacup_price = row['Закупочная цена']
    product_price.save()

def parse_price(price_str):
    if not price_str:
        return 0.0
    cleaned = str(price_str).replace(' ', '').replace(',', '.').strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0  # Возврат 0, если формат некорректный (для безопасности)

def process_single_row(row, row_num):
    """Обработка одной строки CSV с контролем нагрузки"""
    try:
        # Получаем или создаём размер
        size, _ = get_or_create_size(row.get('Значение св-ва для модификации товара №1', ''))
        if not size:
            size = None  # Если пустой размер, используем None

        # Получаем или создаём категорию
        category, _ = get_or_create_category('')

        title = row.get('Название товара', '').strip()
        if not title:
            raise ValueError("Пропуск строки: нет названия товара.")

        article_number_str = row.get('Артикул', '').strip()
        try:
            article_number = int(article_number_str)
        except (ValueError, TypeError):
            raise ValueError(f"Пропуск строки: неверный артикул {article_number_str}.")

        slug = generate_slug(title, article_number)
        print(f"Генерируем slug для продукта: {slug}")

        product = get_or_create_product(article_number)
        stock = 100
        
        if product:
            # Обновляем существующий продукт
            product.slug = slug
            product.title = title
            product.description = row.get('Полное описание товара', '')
            product.is_hidden = row.get('Скрыт ли товар на сайте?', '0').strip() == '1'
            product.unit = row.get('Ед. измерения', '')
            product.stock = stock
            product.category = category
            save_product(product)

            # Обновляем или создаем цену для продукта
            product_price, price_created = get_or_create_product_price(
                product,
                size,
                defaults={
                    'price': parse_price(row.get('Цена продажи, без учёта скидок', 0)),
                    'old_price': parse_price(row.get('Старая цена', '')),
                    'zacup_price': parse_price(row.get('Закупочная цена', 0)),
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
                row.get('Полное описание товара', ''),
                row.get('Скрыт ли товар на сайте?', '0').strip() == '1',
                article_number,
                row.get('Ед. измерения', ''),
                stock,
                category
            )

            # Создание цены для нового продукта
            get_or_create_product_price(
                product,
                size,
                defaults={
                    'price': parse_price(row.get('Цена продажи, без учёта скидок', 0)),
                    'old_price': parse_price(row.get('Старая цена', '')),
                    'zacup_price': parse_price(row.get('Закупочная цена', 0)),
                }
            )

        # Если есть URL для изображений, загружаем их
        image_urls = row.get('Изображения товара', '').strip()
        if image_urls:
            import_images(image_urls, product)  # Загрузка изображений только один раз для продукта

        return True, f"Продукт {title} успешно импортирован из строки {row_num}."

    except KeyError as e:
        error_msg = f"Ошибка: отсутствует ключ в CSV строке {row_num} (артикул: {row.get('Артикул', '?')}): {e}"
        return False, error_msg
    except Exception as e:
        error_msg = f"Ошибка при обработке строки {row_num} (артикул: {row.get('Артикул', '?')}): {e}"
        return False, error_msg

def import_products_from_csv(file_path):
    """Оптимизированная главная функция импорта из CSV с контролем нагрузки CPU."""
    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
        return
    
    # Настройки для контроля нагрузки
    BATCH_SIZE = 50  # Обрабатываем по 50 строк за раз
    DELAY_BETWEEN_BATCHES = 0.5  # Пауза 0.5 секунды между пачками
    DELAY_BETWEEN_ROWS = 0.01  # Минимальная пауза между строками
    
    successful_imports = 0
    errors = []  # Список словарей: {'row_num': int, 'row': dict, 'error': str}
    
    # Читаем весь файл в память для более эффективной обработки
    with open(file_path, 'r', encoding='windows-1251') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        rows = list(reader)
    
    total_rows = len(rows)
    print(f"Найдено строк для обработки: {total_rows}")
    start_time = time.time()
    
    # Обрабатываем файл пачками для снижения нагрузки
    for i in range(0, total_rows, BATCH_SIZE):
        batch_start_time = time.time()
        batch = rows[i:i + BATCH_SIZE]
        
        for j, row in enumerate(batch):
            row_num = i + j + 2  # Нумерация строк, начиная с 2 (1 - заголовки)
            
            # Добавляем небольшую задержку между строками
            time.sleep(DELAY_BETWEEN_ROWS)
            
            success, result = process_single_row(row, row_num)
            
            if success:
                successful_imports += 1
                print(result)
            else:
                errors.append({'row_num': row_num, 'row': dict(row), 'error': result})
                print(result)
        
        # Закрываем соединение с БД для очистки ресурсов
        connection.close()
        
        batch_time = time.time() - batch_start_time
        progress = min(i + BATCH_SIZE, total_rows)
        elapsed_total = time.time() - start_time
        
        print(f"Обработано {progress}/{total_rows} строк. "
              f"Время пачки: {batch_time:.2f}сек, "
              f"Общее время: {elapsed_total:.2f}сек")
        
        # Пауза между пачками для снижения нагрузки CPU
        if i + BATCH_SIZE < total_rows:
            time.sleep(DELAY_BETWEEN_BATCHES)
    
    total_processed = successful_imports + len(errors)
    failed_count = len(errors)
    
    total_time = time.time() - start_time
    print(f"\nИмпорт завершён за {total_time:.2f} секунд.")
    print(f"Всего обработано строк (товаров): {total_processed}")
    print(f"Успешно импортировано: {successful_imports}")
    print(f"Не импортировано (с ошибками): {failed_count}")
    
    if errors:
        print("\nПодробности ошибок:")
        for err in errors[:10]:  # Показываем только первые 10 ошибок
            print(f"- Строка {err['row_num']}: {err['error']} (Название: {err['row'].get('Название товара', 'N/A')}, Артикул: {err['row'].get('Артикул', 'N/A')})")
        if len(errors) > 10:
            print(f"... и еще {len(errors) - 10} ошибок")

    return successful_imports, errors



























# # рабочий парсер товаров очень, быстрый но не устанавливает первую фотографию товара а рандомна.
# import csv
# import os
# import requests
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from django.core.files.base import ContentFile
# from .models import Product, Size, ProductPrice, Category, ProductImage
# from slugify import slugify
# import time
# import random  # Для случайной задержки

# def generate_slug(title, article_number):
#     slug = slugify(f"{title}-{article_number}")
#     return slug

# def get_existing_images(product):
#     return ProductImage.objects.filter(product=product).exists()

# def import_images_parallel(image_urls, product, max_workers=5, delay=0.5):
#     """
#     Параллельная загрузка изображений с лимитом потоков и задержками,
#     чтобы избежать блокировки удалённого сервера.
#     """
#     image_urls = [url.strip() for url in image_urls.splitlines() if url.strip()]
    
#     # Проверяем, есть ли уже изображения для данного продукта
#     if get_existing_images(product):
#         print(f"Изображения уже загружены для продукта {product.title}. Пропускаем загрузку.")
#         return  # Если изображения уже существуют, пропускаем загрузку
    
#     # Параллельная загрузка с ограниченным числом потоков
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         futures = [
#             executor.submit(download_image_with_delay, url, product, delay) 
#             for url in image_urls
#         ]
#         for future in as_completed(futures):
#             future.result()  # Ждём завершения каждой

# def download_image_with_delay(image_url, product, delay):
#     """
#     Загрузка одного изображения с задержкой (чтобы не перегружать сервер).
#     """
#     time.sleep(delay + random.uniform(0, 0.5))  # Случайная задержка 0.5-1 сек между запросами
#     try:
#         print(f"Попытка загрузки изображения: {image_url.strip()}")
#         response = requests.get(image_url.strip(), timeout=10)
#         print(f"Статус ответа для {image_url.strip()}: {response.status_code}")
#         if response.status_code == 200:
#             image_data = response.content
#             image_file = ContentFile(image_data)

#             # Извлечение имени файла из URL
#             image_name = os.path.basename(image_url.strip())
#             if not image_name:
#                 image_name = 'image.jpg'  # Дефолтное имя, если не извлекли

#             product_image = ProductImage(product=product)
#             product_image.image.save(image_name, image_file, save=False)
#             product_image.save()
#             print(f"Изображение {image_name} успешно загружено для продукта {product.title}.")
#         else:
#             print(f"Ошибка при загрузке изображения {image_url.strip()}: статус {response.status_code}")
#     except Exception as img_e:
#         print(f"Ошибка при загрузке изображения {image_url.strip()}: {img_e}")

# def get_or_create_size(size_title):
#     if not size_title or not size_title.strip():
#         return None, False
#     normalized_title = size_title.strip().upper()
#     size, created = Size.objects.get_or_create(
#         title__iexact=normalized_title,  # Используйте фильтр с iexact
#         defaults={'title': size_title.strip()}  # Сохраняйте оригинальный title
#     )
#     return size, created

# def get_or_create_category(category_name):
#     if not category_name or not category_name.strip():
#         # Дефолтная категория
#         category, created = Category.objects.get_or_create(
#             name='Без категории',
#             defaults={'slug': slugify('Без категории')}
#         )
#         return category, created
#     category_slug = slugify(category_name.strip())
#     return Category.objects.get_or_create(name=category_name.strip(), slug=category_slug)

# def get_or_create_product(article_number):
#     try:
#         return Product.objects.filter(article_number=int(article_number)).first()
#     except (ValueError, TypeError):
#         # Если article_number не число, возвращаем None
#         return None

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

# def save_product(product):
#     product.save()
#     return product

# def get_or_create_product_price(product, size, defaults):
#     return ProductPrice.objects.get_or_create(product=product, size=size, defaults=defaults)

# def update_product_price(product_price, row):
#     product_price.price = parse_price(row.get('Цена продажи, без учёта скидок', 0))
#     product_price.old_price = parse_price(row.get('Старая цена', ''))
#     product_price.zacup_price = parse_price(row.get('Закупочная цена', 0))
#     product_price.save()

# def parse_price(price_str):
#     """Функция парсинга цены, перенесена сюда для доступности."""
#     if not price_str:
#         return 0.0
#     cleaned = str(price_str).replace(' ', '').replace(',', '.').strip()
#     try:
#         return float(cleaned)
#     except ValueError:
#         return 0.0  # Возврат 0, если формат некорректный (для безопасности)
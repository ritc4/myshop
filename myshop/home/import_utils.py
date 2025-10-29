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

# # Запуск асинхронной функции импорта
# # asyncio.run(import_products_from_csv('path_to_your_csv_file.csv'))




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






import csv
import aiohttp
import asyncio
import aiofiles
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async
from .models import Product, Size, ProductPrice, Category, ProductImage
from slugify import slugify

def generate_slug(title, article_number):
    slug = slugify(f"{title}-{article_number}")
    return slug

async def import_images(image_urls, product):
    # Разделяем URL по переносам строк
    image_urls = [url.strip() for url in image_urls.splitlines() if url.strip()]

    # Проверяем, есть ли уже изображения для данного продукта
    existing_images = await get_existing_images(product)

    if existing_images:
        print(f"Изображения уже загружены для продукта {product.title}. Пропускаем загрузку.")
        return  # Если изображения уже существуют, пропускаем загрузку

    async with aiohttp.ClientSession() as session:
        for url in image_urls:  # Загружаем изображения последовательно
            await download_image(session, url, product)

async def download_image(session, image_url, product):
    try:
        print(f"Попытка загрузки изображения: {image_url.strip()}")
        async with session.get(image_url.strip(), timeout=aiohttp.ClientTimeout(total=10)) as response:
            print(f"Статус ответа для {image_url.strip()}: {response.status}")
            if response.status == 200:
                image_data = await response.read()
                image_file = ContentFile(image_data)

                # Извлечение имени файла из URL
                image_name = image_url.split("/")[-1]
                product_image = ProductImage(product=product)

                # Сохранение изображения
                await sync_to_async(product_image.image.save)(
                    image_name, image_file
                )
                await sync_to_async(product_image.save)()  # Сохранение в асинхронном контексте
                print(f"Изображение {image_name} успешно загружено для продукта {product.title}.")
            else:
                print(f"Ошибка при загрузке изображения {image_url.strip()}: статус {response.status}")
    except Exception as img_e:
        print(f"Ошибка при загрузке изображения {image_url.strip()}: {img_e}")

@sync_to_async
def get_existing_images(product):
    return ProductImage.objects.filter(product=product).exists()

@sync_to_async
def get_or_create_size(size_title):
    return Size.objects.get_or_create(title=size_title)

@sync_to_async
def get_or_create_category(category_name):
    category_slug = slugify(category_name)
    return Category.objects.get_or_create(name=category_name, slug=category_slug)

@sync_to_async
def get_or_create_product(article_number):
    return Product.objects.filter(article_number=article_number).first()

@sync_to_async
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

@sync_to_async
def save_product(product):
    product.save()
    return product

@sync_to_async
def get_or_create_product_price(product, size, defaults):
    return ProductPrice.objects.get_or_create(product=product, size=size, defaults=defaults)

@sync_to_async
def update_product_price(product_price, row):
    product_price.price = row['Цена продажи']
    product_price.old_price = row.get('Старая цена')
    product_price.zacup_price = row['Закупочная цена']
    product_price.save()

async def import_products_from_csv(file_path):
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(await csvfile.readlines())
        for row in reader:
            try:
                size, _ = await get_or_create_size(row['Размер'])
                
                # Изменение: Парсим название товара для извлечения категории
                full_title = row['Название товара'].strip()
                if ' - ' in full_title:
                    category_name, title = full_title.split(' - ', 1)
                    category_name = category_name.strip()
                    title = title.strip()
                else:
                    category_name = None  # Нет категории в названии
                    title = full_title
                
                if category_name:
                    category, _ = await get_or_create_category(category_name)
                else:
                    default_category, _ = await get_or_create_category('Без категории')
                    category = default_category

                article_number = row['Артикул']
                slug = generate_slug(title, article_number)  # Slug теперь на основе очищенного title

                print(f"Генерируем slug для продукта: {slug}")

                product = await get_or_create_product(article_number)
                
                if product:
                    product.slug = slug
                    product.title = title  # Используем очищенное title
                    product.description = row['Описание товара']
                    product.is_hidden = row['Скрыт ли товар'].strip() == '1'
                    product.unit = row['Ед. измерения']
                    product.stock = row['Остаток']
                    product.category = category
                    await save_product(product)

                    # Обновляем или создаем цену для продукта
                    product_price, price_created = await get_or_create_product_price(
                        product,
                        size,
                        defaults={
                            'price': row['Цена продажи'],
                            'old_price': row.get('Старая цена'),
                            'zacup_price': row['Закупочная цена'],
                        }
                    )

                    if not price_created:
                        # Если цена уже существует, обновляем её
                        await update_product_price(product_price, row)
                else:
                    # Если продукт не существует, создаем новый
                    product = await create_product(
                        slug,
                        title,  # Используем очищенное title
                        row['Описание товара'],
                        row['Скрыт ли товар'].strip() == '1',
                        article_number,
                        row['Ед. измерения'],
                        row['Остаток'],
                        category
                    )

                    # Создание цены для нового продукта
                    await get_or_create_product_price(
                        product,
                        size,
                        defaults={
                            'price': row['Цена продажи'],
                            'old_price': row.get('Старая цена'),
                            'zacup_price': row['Закупочная цена'],
                        }
                    )

                # Если есть URL для изображений, загружаем их
                if 'Изображения' in row and row['Изображения']:
                    image_urls = row['Изображения'].strip()
                    await import_images(image_urls, product)  # Загрузка изображений только один раз для продукта

                print(f"Продукт {title} успешно импортирован.")

            except Exception as e:
                print(f"Ошибка при обработке строки {row}: {e}")

# Запуск асинхронной функции импорта
# asyncio.run(import_products_from_csv('path_to_your_csv_file.csv'))

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




import csv
import aiohttp
import asyncio
import aiofiles
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async
from urllib.parse import urlparse
from .models import Product, Size, ProductPrice, Category, ProductImage
from slugify import slugify
import signal

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
        return

    async with aiohttp.ClientSession() as session:
        for url in image_urls:
            try:
                await download_image(session, url, product)
            except asyncio.CancelledError:
                print(f"Импорт изображений прерван для {product.title}.")
                raise

async def download_image(session, image_url, product):
    parsed_url = urlparse(image_url.strip())
    if not parsed_url.scheme or not parsed_url.netloc:
        print(f"Некорректный URL для изображения: {image_url.strip()}. Пропускаем.")
        return
    
    try:
        print(f"Попытка загрузки изображения: {image_url.strip()}")
        async with session.get(image_url.strip(), timeout=aiohttp.ClientTimeout(total=10)) as response:
            print(f"Статус ответа для {image_url.strip()}: {response.status}")
            if response.status == 200:
                image_data = await response.read()
                image_file = ContentFile(image_data)

                image_name = image_url.split("/")[-1]
                product_image = ProductImage(product=product)

                await sync_to_async(product_image.image.save)(
                    image_name, image_file
                )
                await sync_to_async(product_image.save)()
                print(f"Изображение {image_name} успешно загружено для продукта {product.title}.")
            else:
                print(f"Ошибка при загрузке изображения {image_url.strip()}: статус {response.status}")
    except asyncio.CancelledError:
        raise
    except Exception as img_e:
        print(f"Ошибка при загрузке изображения {image_url.strip()}: {img_e}")

@sync_to_async
def get_existing_images(product):
    return ProductImage.objects.filter(product=product).exists()

@sync_to_async
def get_or_create_size(size_title):
    return Size.objects.get_or_create(title=size_title)

@sync_to_async
def get_or_create_category(name, parent=None):
    slug = slugify(name)
    return Category.objects.get_or_create(name=name, slug=slug, defaults={'parent': parent})

def parse_category_from_title(full_title):
    """
    Парсим название товара для определения категории и подкатегории.
    Возвращает кортеж: (parent_category_name, subcategory_name, cleaned_title)
    Если не найдено, возвращает (None, "Без категории", full_title)
    """
    title_lower = full_title.lower().strip()
    print(f"Парсинг title: '{full_title}' (lower: '{title_lower}')")  # Для отладки
    
    # Специальные категории (расширены, проверяем первыми для приоритета; убрали 'тройк', убрали 'Товары для дома', перенесли ключи в 'НОВЫЙ ГОД')
    special_categories = {
        # Новый год / праздники (расширено: добавлены 'ветка', 'ветв', перенесли ключи из 'Товары для дома' — постельное, лампы, ночники и т.д.)
        'новый год': 'НОВЫЙ ГОД', 'новогодний': 'НОВЫЙ ГОД', 'новогодняя': 'НОВЫЙ ГОД', 'новогодние': 'НОВЫЙ ГОД',
        'новогоднего': 'НОВЫЙ ГОД', 'новогодней': 'НОВЫЙ ГОД', 'новогодних': 'НОВЫЙ ГОД', 'рождество': 'НОВЫЙ ГОД',
        'рождественский': 'НОВЫЙ ГОД', 'рождественская': 'НОВЫЙ ГОД', 'рождественские': 'НОВЫЙ ГОД', 'праздник': 'НОВЫЙ ГОД',
        'праздники': 'НОВЫЙ ГОД', 'праздничный': 'НОВЫЙ ГОД', 'праздничная': 'НОВЫЙ ГОД', 'новогодние аксессуары': 'НОВЫЙ ГОД',
        'гирлянд': 'НОВЫЙ ГОД', 'гирлянда': 'НОВЫЙ ГОД', 'гирлянды': 'НОВЫЙ ГОД', 'коврик': 'НОВЫЙ ГОД', 'фейерверк': 'НОВЫЙ ГОД',
        'ветк': 'НОВЫЙ ГОД', 'ветка': 'НОВЫЙ ГОД', 'ветв': 'НОВЫЙ ГОД', 'елочн': 'НОВЫЙ ГОД', 'елочка': 'НОВЫЙ ГОД', 'снежинк': 'НОВЫЙ ГОД',
        'снежинка': 'НОВЫЙ ГОД', 'игрушк': 'НОВЫЙ ГОД', 'игрушка': 'НОВЫЙ ГОД', 'украшени': 'НОВЫЙ ГОД', 'украшение': 'НОВЫЙ ГОД',
        # Перенесено из 'Товары для дома' (постельное бельё, лампы и т.д.)
        'постельное': 'НОВЫЙ ГОД', 'постельные': 'НОВЫЙ ГОД', 'постельной': 'НОВЫЙ ГОД', 'постель': 'НОВЫЙ ГОД',
        'постели': 'НОВЫЙ ГОД', 'белье': 'НОВЫЙ ГОД', 'белья': 'НОВЫЙ ГОД', 'белью': 'НОВЫЙ ГОД',
        'бельем': 'НОВЫЙ ГОД', 'бель': 'НОВЫЙ ГОД', 'домашний': 'НОВЫЙ ГОД', 'домашняя': 'НОВЫЙ ГОД',
        'домашние': 'НОВЫЙ ГОД', 'полотенц': 'НОВЫЙ ГОД', 'полотенце': 'НОВЫЙ ГОД', 'салфетк': 'НОВЫЙ ГОД',
        'салфетки': 'НОВЫЙ ГОД', 'настольн': 'НОВЫЙ ГОД', 'кухонн': 'НОВЫЙ ГОД', 'ночной': 'НОВЫЙ ГОД',
        'ночник': 'НОВЫЙ ГОД', 'ламп': 'НОВЫЙ ГОД', 'лампа': 'НОВЫЙ ГОД', 'светильник': 'НОВЫЙ ГОД',
        'настольный': 'НОВЫЙ ГОД', 'ванн': 'НОВЫЙ ГОД', 'ванная': 'НОВЫЙ ГОД', 'туалет': 'НОВЫЙ ГОД',
        # Сад, огород (расширено: добавлены 'дерев', 'кустарник', 'овощ', 'фрукт', 'ягод')
        'сад': 'Сад, огород', 'сада': 'Сад, огород', 'огород': 'Сад, огород', 'огорода': 'Сад, огород', 'семена': 'Сад, огород',
        'семен': 'Сад, огород', 'растения': 'Сад, огород', 'растений': 'Сад, огород', 'цветы': 'Сад, огород', 'цветов': 'Сад, огород',
        'инструмент': 'Сад, огород', 'инструменты': 'Сад, огород', 'удобрени': 'Сад, огород', 'удобрения': 'Сад, огород',
        'горшок': 'Сад, огород', 'горшки': 'Сад, огород', 'кашпо': 'Сад, огород', 'теплиц': 'Сад, огород', 'теплица': 'Сад, огород',
        'саженц': 'Сад, огород', 'саженцы': 'Сад, огород', 'рассад': 'Сад, огород', 'рассада': 'Сад, огород', 'газон': 'Сад, огород',
        'клумб': 'Сад, огород', 'клумба': 'Сад, огород', 'мебель садовая': 'Сад, огород', 'полив': 'Сад, огород', 'поливные системы': 'Сад, огород',
        'пестицид': 'Сад, огород', 'пестициды': 'Сад, огород', 'гербицид': 'Сад, огород', 'гербициды': 'Сад, огород',
        'компост': 'Сад, огород', 'грунт': 'Сад, огород', 'дерев': 'Сад, огород', 'дерево': 'Сад, огород', 'кустарник': 'Сад, огород',
        'овощ': 'Сад, огород', 'фрукт': 'Сад, огород', 'ягод': 'Сад, огород',
        # Искусственные цветы (расширено: 'декоративн', 'украшени', 'растени')
        'искусственн': 'Искусственные цветы', 'искусственные цветы': 'Искусственные цветы', 'искусственный цветок': 'Искусственные цветы',
        'декоративные цветы': 'Искусственные цветы', 'декоративный цветок': 'Искусственные цветы', 'декоративн': 'Искусственные цветы',
        'украшени': 'Искусственные цветы', 'украшение': 'Искусственные цветы', 'растени': 'Искусственные цветы', 'растение': 'Искусственные цветы',
        # Косметика (расширено: 'парфюм', 'крем', 'маска', 'лосьон')
        'косметик': 'Косметика', 'косметика': 'Косметика', 'уход за лицом': 'Косметика', 'уход за телом': 'Косметика',
        'уход за волосами': 'Косметика', 'макияж': 'Косметика', 'парфюмери': 'Косметика', 'парфюмерия': 'Косметика',
        'дух': 'Косметика', 'духи': 'Косметика', 'парфюм': 'Косметика', 'крем': 'Косметика', 'маска': 'Косметика', 'лосьон': 'Косметика',
        # Игрушки (расширено: 'кукл', 'машинк', 'конструктор')
        'игрушк': 'Игрушки', 'игрушка': 'Игрушки', 'игрушки': 'Игрушки', 'детские игрушки': 'Игрушки', 'развивающие игрушки': 'Игрушки',
        'кукл': 'Игрушки', 'кукла': 'Игрушки', 'машинк': 'Игрушки', 'машинка': 'Игрушки', 'конструктор': 'Игрушки',
        # Сумки и рюкзаки (расширено: 'портфел', 'чехол')
        'сумк': 'Сумки и рюкзаки', 'сумка': 'Сумки и рюкзаки', 'сумки': 'Сумки и рюкзаки', 'рюкзак': 'Сумки и рюкзаки',
        'рюкзаки': 'Сумки и рюкзаки', 'портфел': 'Сумки и рюкзаки', 'портфель': 'Сумки и рюкзаки', 'чехол': 'Сумки и рюкзаки',
        # Подарки и текстиль (убрали 'тройк', расширили: 'комплект', 'ткан')
        'подарочн': 'Подарки и текстиль', 'подарок': 'Подарки и текстиль', 'набор': 'Подарки и текстиль', 'набора': 'Подарки и текстиль',
        'плед': 'Подарки и текстиль', 'пледа': 'Подарки и текстиль', 'комплект': 'Подарки и текстиль',
        'ткан': 'Подарки и текстиль', 'ткань': 'Подарки и текстиль',
    }
    
    # Шаг 1: Ищем специальные категории (приоритет)
    for special_key, cat_name in special_categories.items():
        if special_key in title_lower:
            print(f"Найдена специальная категория: '{special_key}' -> {cat_name}")
            return None, cat_name, full_title
    
    # Расширенные словари для гендеров
    gender_keywords = {
        # Женский (расширено: 'lady', 'girl', 'woman')
        'для женщин': 'ЖЕНСКАЯ ОДЕЖДА', 'для женщины': 'ЖЕНСКАЯ ОДЕЖДА', 'женщина': 'ЖЕНСКАЯ ОДЕЖДА', 'женские': 'ЖЕНСКАЯ ОДЕЖДА',
        'женских': 'ЖЕНСКАЯ ОДЕЖДА', 'женщинам': 'ЖЕНСКАЯ ОДЕЖДА', 'женщинами': 'ЖЕНСКАЯ ОДЕЖДА', 'женщинах': 'ЖЕНСКАЯ ОДЕЖДА',
        'женская': 'ЖЕНСКАЯ ОДЕЖДА', 'женской': 'ЖЕНСКАЯ ОДЕЖДА', 'женскую': 'ЖЕНСКАЯ ОДЕЖДА', 'женский': 'ЖЕНСКАЯ ОДЕЖДА',
        'женским': 'ЖЕНСКАЯ ОДЕЖДА', 'женское': 'ЖЕНСКАЯ ОДЕЖДА', 'жен.': 'ЖЕНСКАЯ ОДЕЖДА', 'жен': 'ЖЕНСКАЯ ОДЕЖДА', 'женск': 'ЖЕНСКАЯ ОДЕЖДА',
        'lady': 'ЖЕНСКАЯ ОДЕЖДА', 'girl': 'ЖЕНСКАЯ ОДЕЖДА', 'woman': 'ЖЕНСКАЯ ОДЕЖДА',
        # Мужской (расширено: 'man', 'boy', 'gentleman')
        'для мужчин': 'МУЖСКАЯ ОДЕЖДА', 'для мужчины': 'МУЖСКАЯ ОДЕЖДА', 'мужчина': 'МУЖСКАЯ ОДЕЖДА', 'мужские': 'МУЖСКАЯ ОДЕЖДА',
        'мужских': 'МУЖСКАЯ ОДЕЖДА', 'мужчинам': 'МУЖСКАЯ ОДЕЖДА', 'мужчинами': 'МУЖСКАЯ ОДЕЖДА', 'мужчинах': 'МУЖСКАЯ ОДЕЖДА',
        'мужская': 'МУЖСКАЯ ОДЕЖДА', 'мужской': 'МУЖСКАЯ ОДЕЖДА', 'мужскую': 'МУЖСКАЯ ОДЕЖДА', 'муж.': 'МУЖСКАЯ ОДЕЖДА',
        'муж': 'МУЖСКАЯ ОДЕЖДА', 'мужск': 'МУЖСКАЯ ОДЕЖДА', 'man': 'МУЖСКАЯ ОДЕЖДА', 'boy': 'МУЖСКАЯ ОДЕЖДА', 'gentleman': 'МУЖСКАЯ ОДЕЖДА',
        # Детский (расширено: 'kid', 'child', 'baby')
        'для детей': 'ДЕТСКАЯ ОДЕЖДА', 'для ребенка': 'ДЕТСКАЯ ОДЕЖДА', 'ребенок': 'ДЕТСКАЯ ОДЕЖДА', 'ребенка': 'ДЕТСКАЯ ОДЕЖДА',
        'дети': 'ДЕТСКАЯ ОДЕЖДА', 'детская': 'ДЕТСКАЯ ОДЕЖДА', 'детской': 'ДЕТСКАЯ ОДЕЖДА', 'детскую': 'ДЕТСКАЯ ОДЕЖДА',
        'детские': 'ДЕТСКАЯ ОДЕЖДА', 'детских': 'ДЕТСКАЯ ОДЕЖДА', 'дет': 'ДЕТСКАЯ ОДЕЖДА', 'детск': 'ДЕТСКАЯ ОДЕЖДА',
        'kid': 'ДЕТСКАЯ ОДЕЖДА', 'child': 'ДЕТСКАЯ ОДЕЖДА', 'baby': 'ДЕТСКАЯ ОДЕЖДА',
        # Подростковый (расширено: 'teen', 'youth')
        'для подростков': 'ДЕТСКАЯ ОДЕЖДА', 'подросток': 'ДЕТСКАЯ ОДЕЖДА', 'подростки': 'ДЕТСКАЯ ОДЕЖДА', 'подростков': 'ДЕТСКАЯ ОДЕЖДА',
        'подростковая': 'ДЕТСКАЯ ОДЕЖДА', 'подростковой': 'ДЕТСКАЯ ОДЕЖДА', 'подрос': 'ДЕТСКАЯ ОДЕЖДА', 'teen': 'ДЕТСКАЯ ОДЕЖДА', 'youth': 'ДЕТСКАЯ ОДЕЖДА',
    }
    
    # Словари для подкатегорий по гендерам (разделены, расширены: добавлены дублёнки, гендер к общим категориям)
    subcategory_mappings = {
        'ЖЕНСКАЯ ОДЕЖДА': {
            # Рубашки, блузки
            'рубашк': 'Рубашки, блузки', 'рубашка': 'Рубашки, блузки', 'рубашки': 'Рубашки, блузки', 'рубашек': 'Рубашки, блузки',
            'блузк': 'Рубашки, блузки', 'блузка': 'Рубашки, блузки', 'блузки': 'Рубашки, блузки', 'блузок': 'Рубашки, блузки',
            # Обувь (расширено: 'балетк', 'сапог', 'ботильон')
            'обув': 'Обувь женская', 'обувь': 'Обувь женская', 'ботинк': 'Обувь женская', 'ботинки': 'Обувь женская', 'туфл': 'Обувь женская',
            'тапочк': 'Обувь женская', 'тапочки': 'Обувь женская', 'сандал': 'Обувь женская', 'кроссовк': 'Обувь женская', 'балетк': 'Обувь женская',
            'балетки': 'Обувь женская', 'сапог': 'Обувь женская', 'ботильон': 'Обувь женская',
            # Свитеры, джемперы (гендер-специфично)
            'свитер': 'Джемпер, свитер женский', 'свитера': 'Джемпер, свитер женский', 'джемпер': 'Джемпер, свитер женский', 'джемпера': 'Джемпер, свитер женский',
            'кофт': 'Джемпер, свитер женский', 'кофта': 'Джемпер, свитер женский', 'кардиган': 'Джемпер, свитер женский',
            # Верхняя одежда (добавлен бомбер, дублёнка)
            'куртк': 'Верхняя одежда женская', 'куртка': 'Верхняя одежда женская', 'куртки': 'Верхняя одежда женская',
            'пальт': 'Верхняя одежда женская', 'пальто': 'Верхняя одежда женская', 'плащ': 'Верхняя одежда женская',
            'бомбер': 'Верхняя одежда женская', 'дублёнк': 'Верхняя одежда женская', 'дублёнка': 'Верхняя одежда женская',
            # Платья, туники
            'плат': 'Платья', 'платье': 'Платья', 'платья': 'Платья', 'туник': 'Платья', 'туника': 'Платья',
            # Юбки
            'юбк': 'Юбки', 'юбка': 'Юбки', 'юбки': 'Юбки',
            # Джинсы, брюки, шорты (разделены)
            'джинс': 'Джинсы женские', 'джинсы': 'Джинсы женские',
            'брюк': 'Брюки женские', 'брюки': 'Брюки женские',
            'шорт': 'Шорты женские', 'шорты': 'Шорты женские',
            'леггин': 'Леггинсы женские', 'леггинсы': 'Леггинсы женские',
            # Толстовки, свитшоты (гендер-специфично)
            'толстовк': 'Толстовки, свитшоты женские', 'толстовка': 'Толстовки, свитшоты женские',
            # Футболки, майки, топы
            'футболк': 'Футболки, майки', 'футболка': 'Футболки, майки', 'майк': 'Футболки, майки', 'майка': 'Футболки, майки',
            'топ': 'Футболки, майки', 'топа': 'Футболки, майки',
            # Костюмы (добавлена тройка)
            'костюм': 'Костюмы женские', 'костюма': 'Костюмы женские', 'костюмы': 'Костюмы женские', 'тройк': 'Костюмы женские',
            # Пижамы (отдельная подкатегория)
            'пижам': 'Пижамы женские', 'пижама': 'Пижамы женские',
            # Халаты (отдельная подкатегория)
            'халат': 'Халаты женские',
            # Купальники, нижнее белье
            'купальник': 'Купальники, нижнее белье', 'купальники': 'Купальники, нижнее белье', 'бель': 'Купальники, нижнее белье',
            'белье': 'Купальники, нижнее белье', 'лифчик': 'Купальники, нижнее белье', 'трусики': 'Купальники, нижнее белье',
            # Колготки, носки (гендер-специфично)
            'колготк': 'Колготки женские', 'колготки': 'Колготки женские', 'носок': 'Колготки женские', 'носки': 'Колготки женские',
            # Аксессуары (расширено: 'бижутери', 'ювелирк', 'браслет', 'серьги')
            'шарф': 'Аксессуары женские', 'шарфы': 'Аксессуары женские', 'перчатк': 'Аксессуары женские', 'перчатки': 'Аксессуары женские',
            'шляп': 'Аксессуары женские', 'шляпа': 'Аксессуары женские', 'очки': 'Аксессуары женские', 'очки солнцезащитные': 'Аксессуары женские',
            'ремень': 'Аксессуары женские', 'ремни': 'Аксессуары женские', 'сумк': 'Аксессуары женские', 'сумка': 'Аксессуары женские',
            'рюкзак': 'Аксессуары женские', 'рюкзаки': 'Аксессуары женские', 'бижутери': 'Аксессуары женские', 'бижутерия': 'Аксессуары женские',
            'ювелирк': 'Аксессуары женские', 'ювелирка': 'Аксессуары женские', 'браслет': 'Аксессуары женские', 'серьги': 'Аксессуары женские',
            # Другие
            'боди': 'Боди, комбинезоны', 'боди': 'Боди, комбинезоны', 'комбинезон': 'Боди, комбинезоны', 'комбинезоны': 'Боди, комбинезоны',
            'лосин': 'Лосины, леггинсы', 'лосины': 'Лосины, леггинсы', 'леггинс': 'Лосины, леггинсы', 'леггинсы': 'Лосины, леггинсы',
        },
        'МУЖСКАЯ ОДЕЖДА': {
            # Аналогично расширено: рубахи, обувь, свитеры (гендер-специфично), верхняя одежда (дублёнка), брюки/джинсы/шорты, футболки, костюмы, пижамы, халаты, белье, носки, аксессуары
            'рубашк': 'Рубашки', 'рубашка': 'Рубашки', 'рубашки': 'Рубашки', 'рубашек': 'Рубашки',
            'обув': 'Обувь мужская', 'обувь': 'Обувь мужская', 'ботинк': 'Обувь мужская', 'ботинки': 'Обувь мужская',
            'тапочк': 'Обувь мужская', 'тапочки': 'Обувь мужская', 'кроссовк': 'Обувь мужская', 'кроссовки': 'Обувь мужская',
            'кед': 'Обувь мужская', 'кеды': 'Обувь мужская',
            'свитер': 'Джемпер, свитер мужской', 'свитера': 'Джемпер, свитер мужской', 'джемпер': 'Джемпер, свитер мужской', 'джемпера': 'Джемпер, свитер мужской',
            'кофт': 'Джемпер, свитер мужской', 'кофта': 'Джемпер, свитер мужской',
            'куртк': 'Верхняя одежда мужская', 'куртка': 'Верхняя одежда мужская', 'куртки': 'Верхняя одежда мужская',
            'пальт': 'Верхняя одежда мужская', 'пальто': 'Верхняя одежда мужская', 'плащ': 'Верхняя одежда мужская',
            'дублёнк': 'Верхняя одежда мужская', 'дублёнка': 'Верхняя одежда мужская',
            'джинс': 'Джинсы мужские', 'джинсы': 'Джинсы мужские',
            'брюк': 'Брюки мужские', 'брюки': 'Брюки мужские',
            'шорт': 'Шорты мужские', 'шорты': 'Шорты мужские',
            'леггин': 'Леггинсы мужские', 'леггинсы': 'Леггинсы мужские',
            'толстовк': 'Толстовки, свитшоты мужские', 'толстовка': 'Толстовки, свитшоты мужские',
            'футболк': 'Футболки, майки', 'футболка': 'Футболки, майки', 'майк': 'Футболки, майки', 'майка': 'Футболки, майки',
            'топ': 'Футболки, майки', 'топа': 'Футболки, майки',
            'костюм': 'Костюмы мужские', 'костюма': 'Костюмы мужские', 'костюмы': 'Костюмы мужские', 'смокинг': 'Костюмы мужские',
            'фрак': 'Костюмы мужские', 'тройк': 'Костюмы мужские',
            'пижам': 'Пижамы мужские', 'пижама': 'Пижамы мужские',
            'халат': 'Халаты мужские',
            'плавк': 'Купальники, нижнее белье', 'плавки': 'Купальники, нижнее белье', 'бель': 'Купальники, нижнее белье',
            'белье': 'Купальники, нижнее белье', 'трусы': 'Купальники, нижнее белье',
            'носок': 'Носки мужские', 'носки': 'Носки мужские',
            'галстук': 'Аксессуары мужские', 'галстуки': 'Аксессуары мужские', 'ремень': 'Аксессуары мужские', 'ремни': 'Аксессуары мужские',
            'очки': 'Аксессуары мужские', 'очки солнцезащитные': 'Аксессуары мужские', 'шарф': 'Аксессуары мужские', 'шарфы': 'Аксессуары мужские',
            'перчатк': 'Аксессуары мужские', 'перчатки': 'Аксессуары мужские', 'шляп': 'Аксессуары мужские', 'шляпа': 'Аксессуары мужские',
            'сумк': 'Аксессуары мужские', 'сумка': 'Аксессуары мужские', 'рюкзак': 'Аксессуары мужские', 'рюкзаки': 'Аксессуары мужские',
            'боди': 'Боди, комбинезоны', 'боди': 'Боди, комбинезоны', 'комбинезон': 'Боди, комбинезоны', 'комбинезоны': 'Боди, комбинезоны',
        },
        'ДЕТСКАЯ ОДЕЖДА': {
            # Аналогично: рубахи, обувь, свитеры (гендер-специфично), верхняя одежда (дублёнка), платья/юбки, джинсы/брюки/шорты, футболки, костюмы, пижамы, халаты, колготки, аксессуары, боди
            'рубашк': 'Рубашки, блузки', 'рубашка': 'Рубашки, блузки', 'рубашки': 'Рубашки, блузки', 'блузк': 'Рубашки, блузки',
            'блузка': 'Рубашки, блузки', 'блузки': 'Рубашки, блузки',
            'обув': 'Обувь детская', 'обувь': 'Обувь детская', 'ботинк': 'Обувь детская', 'ботинки': 'Обувь детская', 'тапочк': 'Обувь детская',
            'тапочки': 'Обувь детская', 'кроссовк': 'Обувь детская', 'сандал': 'Обувь детская', 'кед': 'Обувь детская', 'кеды': 'Обувь детская',
            'свитер': 'Джемпер, свитер детский', 'свитера': 'Джемпер, свитер детский', 'джемпер': 'Джемпер, свитер детский', 'джемпера': 'Джемпер, свитер детский',
            'кофт': 'Джемпер, свитер детский', 'кофта': 'Джемпер, свитер детский',
            'куртк': 'Верхняя одежда детская', 'куртка': 'Верхняя одежда детская', 'куртки': 'Верхняя одежда детская',
            'пальт': 'Верхняя одежда детская', 'пальто': 'Верхняя одежда детская', 'плащ': 'Верхняя одежда детская',
            'дублёнк': 'Верхняя одежда детская', 'дублёнка': 'Верхняя одежда детская',
            'плат': 'Платья', 'платье': 'Платья', 'платья': 'Платья', 'туник': 'Платья', 'туника': 'Платья',
            'юбк': 'Юбки', 'юбка': 'Юбки', 'юбки': 'Юбки',
            'джинс': 'Джинсы детские', 'джинсы': 'Джинсы детские',
            'брюк': 'Брюки детские', 'брюки': 'Брюки детские',
            'шорт': 'Шорты детские', 'шорты': 'Шорты детские',
            'толстовк': 'Толстовки, свитшоты детские', 'толстовка': 'Толстовки, свитшоты детские',
            'футболк': 'Футболки, майки', 'футболка': 'Футболки, майки', 'майк': 'Футболки, майки', 'майка': 'Футболки, майки',
            'топ': 'Футболки, майки', 'топа': 'Футболки, майки',
            'костюм': 'Костюмы детские', 'костюма': 'Костюмы детские', 'костюмы': 'Костюмы детские', 'тройк': 'Костюмы детские',
            'пижам': 'Пижамы детские', 'пижама': 'Пижамы детские',
            'халат': 'Халаты детские',
            'колготк': 'Колготки детские', 'колготки': 'Колготки детские', 'носок': 'Колготки детские', 'носки': 'Колготки детские',
            'шарф': 'Аксессуары детские', 'шарфы': 'Аксессуары детские', 'перчатк': 'Аксессуары детские', 'перчатки': 'Аксессуары детские',
            'шапка': 'Аксессуары детские', 'шапки': 'Аксессуары детские', 'сумк': 'Аксессуары детские', 'сумка': 'Аксессуары детские',
            'рюкзак': 'Аксессуары детские', 'рюкзаки': 'Аксессуары детские', 'очки': 'Аксессуары детские', 'очки солнцезащитные': 'Аксессуары детские',
            'боди': 'Боди, комбинезоны', 'боди': 'Боди, комбинезоны', 'комбинезон': 'Боди, комбинезоны', 'комбинезоны': 'Боди, комбинезоны',
        }
    }
    
    parent_name = None
    found_gender_key = None
    # Шаг 2: Ищем гендер
    for gender_key, p_name in gender_keywords.items():
        if gender_key in title_lower:
            parent_name = p_name
            found_gender_key = gender_key
            print(f"Найден гендер: '{gender_key}' -> {parent_name}")
            break
    
    subcategory_name = None
    cleaned_title = full_title
    
    if parent_name:
        # Ищем подкатегорию
        subs = subcategory_mappings.get(parent_name, {})
        for sub_key, sub_name in subs.items():
            if sub_key in title_lower:
                subcategory_name = sub_name
                print(f"Найдена подкатегория: '{sub_key}' -> {sub_name}")
                break
        
        if not subcategory_name:
            subcategory_name = parent_name
            print(f"Подкатегория не найдена, fallback на {parent_name}")
        
        # Очистка title (улучшена)
        if found_gender_key:
            cleaned_title = full_title.replace(f" {found_gender_key} ", " ").strip()
            if cleaned_title == full_title:
                if title_lower.startswith(found_gender_key + " "):
                    cleaned_title = full_title[len(found_gender_key) + 1:].strip()
                elif title_lower.endswith(" " + found_gender_key):
                    cleaned_title = full_title[:-len(found_gender_key) - 1].strip()
            print(f"Очищенный title: '{cleaned_title}' (удален гендер: '{found_gender_key}')")
        return parent_name, subcategory_name, cleaned_title
    
    # Шаг 3: Fallback
    print("Ничего не найдено, fallback на 'Без категории'")
    return None, "Без категории", full_title


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
    # Функция для чтения CSV в отдельном потоке (синхронно)
    def read_csv():
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)  # Возвращаем список всех строк для асинхронной обработки

    # Читаем CSV в фоне
    rows = await asyncio.to_thread(read_csv)
    total_rows = len(rows)
    print(f"Начинаем импорт {total_rows} продуктов из {file_path}.")

    processed = 0
    for row in rows:
        try:
            size, _ = await get_or_create_size(row['Размер'])
            
            full_title = row['Название товара'].strip()
            parent_name, subcategory_name, cleaned_title = parse_category_from_title(full_title)
            
            try:
                if parent_name:
                    parent_category, _ = await get_or_create_category(parent_name)
                    category, _ = await get_or_create_category(subcategory_name, parent=parent_category)
                    print(f"Создана иерархия: {parent_name} > {subcategory_name}")
                else:
                    category, _ = await get_or_create_category(subcategory_name)
                    print(f"Создана категория: {subcategory_name}")
            except Exception as cat_e:
                print(f"Ошибка создания категории для '{full_title}': {cat_e}. Fallback на 'Без категории'.")
                category, _ = await get_or_create_category("Без категории")
            
            article_number = row['Артикул']
            slug = generate_slug(cleaned_title, article_number)

            print(f"Генерируем slug для продукта: {slug}")

            product = await get_or_create_product(article_number)
            
            if product:
                product.slug = slug
                product.title = cleaned_title
                product.description = row['Описание товара']
                product.is_hidden = row['Скрыт ли товар'].strip() == '1'
                product.unit = row['Ед. измерения']
                product.stock = row['Остаток']
                product.category = category
                await save_product(product)

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
                    await update_product_price(product_price, row)
            else:
                product = await create_product(
                    slug,
                    cleaned_title,
                    row['Описание товара'],
                    row['Скрыт ли товар'].strip() == '1',
                    article_number,
                    row['Ед. измерения'],
                    row['Остаток'],
                    category
                )

                await get_or_create_product_price(
                    product,
                    size,
                    defaults={
                        'price': row['Цена продажи'],
                        'old_price': row.get('Старая цена'),
                        'zacup_price': row['Закупочная цена'],
                    }
                )

            if 'Изображения' in row and row['Изображения']:
                image_urls = row['Изображения'].strip()
                try:
                    await import_images(image_urls, product)
                except asyncio.CancelledError:
                    print(f"Прерывание загрузки изображений для {product.title}.")
                    break

            print(f"Продукт {cleaned_title} успешно импортирован в категорию '{subcategory_name}'.")
            
            processed += 1
            if processed % 100 == 0:  # Логируем прогресс каждые 100 строк
                print(f"Обработано {processed}/{total_rows} продуктов.")

        except KeyboardInterrupt:
            print(f"\nИмпорт прерван пользователем на строке {processed + 1}. Завершаем gracefully.")
            break
        except Exception as e:
            print(f"Ошибка при обработке строки {processed + 1} ({row.get('Название товара', 'N/A')}): {e}")
            continue

    print(f"Импорт завершён. Обработано {processed} из {total_rows} продуктов.")

def run_import(file_path):
    try:
        asyncio.run(import_products_from_csv(file_path))
    except KeyboardInterrupt:
        print("Импорт завершён пользователем.")
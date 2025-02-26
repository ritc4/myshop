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
                category_name = row.get('Категория', None)
                if category_name:
                    category, _ = await get_or_create_category(category_name)
                else:
                    default_category, _ = await get_or_create_category('Без категории')
                    category = default_category

                title = row['Название товара']
                article_number = row['Артикул']
                slug = generate_slug(title, article_number)

                print(f"Генерируем slug для продукта: {slug}")

                product = await get_or_create_product(article_number)
                
                if product:
                    product.slug = slug
                    product.title = title
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
                        title,
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
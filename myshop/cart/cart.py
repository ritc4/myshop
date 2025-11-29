# from decimal import Decimal
# from django.conf import settings
# from home.models import Product, ProductPrice, Size

# MAX_QUANTITY = 100  # Глобальный максимум для одного товара/размера (можно вынести в settings)

# class Cart:
#     def __init__(self, request):
#         """
#         Инициализировать корзину. 
#         """
#         self.session = request.session
#         cart = self.session.get(settings.CART_SESSION_ID)
#         if not cart:
#             # сохранить пустую корзину в сеансе
#             cart = self.session[settings.CART_SESSION_ID] = {} 
#         self.cart = cart

#     def add(self, product, quantity=1, override_quantity=False, size=None):
#         """Добавить товар в корзину либо обновить его количество."""
#         product_id = str(product.id)
#         unique_key = f"{product_id}_{size}"

#         # Получаем объект Size
#         try:
#             size_object = Size.objects.get(title=size)  # Получаем объект Size по title
#             product_price = product.product_prices.get(size=size_object)  # Используем size
#         except Size.DoesNotExist:
#             print(f"Размер {size} не найден.")  # Удалите print для prod
#             return
#         except ProductPrice.DoesNotExist:
#             print(f"Цена для размера {size} не найдена.")
#             return

#         if unique_key not in self.cart:
#             # Получаем первое изображение
#             first_image = product.images.first()  # Получаем первое изображение
#             image_url = first_image.image.url if first_image else None  # Сохраняем URL изображения

#             self.cart[unique_key] = {
#                 'product_id': product_id,  # Сохраняем id продукта
#                 'article_number': product.article_number,
#                 'title': product.title,  # Сохраняем название продукта
#                 'size': size,
#                 'quantity': 0,
#                 'price': str(product_price.price),  # Сохраняем как строку (для JSON-сериализации)
#                 'image': image_url,  # Сохраняем изображение
#                 'url': product.get_absolute_url()  # Сохраняем URL продукта
#             }

#         # Обновление количества товара в корзине
#         current_quantity = self.cart[unique_key]['quantity']
#         if override_quantity:
#             new_quantity = quantity
#         else:
#             new_quantity = current_quantity + quantity

#         # Жёсткая проверка максимума: обрезаем до 100
#         new_quantity = min(new_quantity, MAX_QUANTITY)
#         self.cart[unique_key]['quantity'] = new_quantity

#         # Удаляем print для production
#         # print(f"{unique_key}: Добавление товара: {product_id}, размер: {size}, количество: {quantity}, переопределить: {override_quantity}")
#         # print("Текущая корзина:", self.cart)
        
#         self.save()
        
#     # Остальные методы без изменений (save, remove, __iter__, __len__, get_total_price, clear, get_item, get_all_items_json)
#     def save(self):
#         # пометить сеанс как "измененный",
#         # чтобы обеспечить его сохранение
#         self.session.modified = True
    
#     def remove(self, product, size=None):
#         """
#         Удалить товар из корзине.
#         """
#         product_id = str(product.id)
#         size_id = str(size)
#         unique_key = f"{product_id}_{size_id}"

#         if unique_key in self.cart:
#             del self.cart[unique_key]
#             self.save()
    
#     def __iter__(self):
#         for size_key, item in self.cart.items():
#             # Создаём копию, чтобы не изменять оригинальный словарь в сессии
#             item_copy = item.copy()
#             item_copy['price'] = Decimal(item_copy['price'])  # Преобразуем из строки в Decimal
#             item_copy['total_price'] = item_copy['price'] * item_copy['quantity']  # Decimal * int = Decimal
#             item_copy['size'] = size_key.split('_')[1]  # Получаем размер из ключа
#             # Добавляем max_quantity для шаблонов (опционально, если нужно динамически)
#             item_copy['max_quantity'] = MAX_QUANTITY
            
#             yield item_copy
    
#     def __len__(self):
#         """
#         Подсчитать все товарные позиции в корзине.
#         """
#         return sum(item['quantity'] for item in self.cart.values())
    
#     def get_total_price(self):
#         return sum(
#             Decimal(item['price']) * item['quantity']  # Преобразуем из строки в Decimal
#             for item in self.cart.values())
    
#     def clear(self):
#         # удалить корзину из сеанса
#         del self.session[settings.CART_SESSION_ID]
#         self.save()
    
#     def get_cart_items(self):
#         return self.cart
    
#     # Добавленный метод для получения данных конкретного товара
#     def get_item(self, product_id, size):
#         """
#         Возвращает данные товара в корзине по product_id и size.
#         Преобразует типы для совместимости с JSON.
#         Возвращает словарь или None, если товар не найден.
#         """
#         unique_key = f"{product_id}_{size}"
#         if unique_key in self.cart:
#             item = self.cart[unique_key].copy()
#             item['price'] = Decimal(item['price'])  # Преобразуем в Decimal
#             item['total_price'] = item['price'] * item['quantity']  # Decimal
#             # Преобразование в строки для JSON
#             item['price'] = str(item['price'])
#             item['total_price'] = str(item['total_price'])
#             item['quantity'] = str(item['quantity'])
#             return item
#         return None

#     # Новый метод: Получить все items в JSON-готовом формате (для будущего использования)
#     def get_all_items_json(self):
#         items = []
#         for unique_key, item in self.cart.items():
#             item_data = item.copy()
#             item_data['price'] = str(Decimal(item['price']))  # Преобразуем в Decimal, затем в строку
#             item_data['total_price'] = str(Decimal(item['price']) * item['quantity'])  # Decimal расчёт, затем строка
#             item_data['quantity'] = str(item['quantity'])
#             item_data['product_id'] = item['product_id']
#             item_data['size'] = unique_key.split('_')[1]  # Размер из ключа
#             items.append(item_data)
#         return items







from decimal import Decimal
from django.conf import settings
from home.models import Product, ProductPrice, Size

MAX_QUANTITY = 100  # Глобальный максимум для одного товара/размера (можно вынести в settings)

class Cart:
    def __init__(self, request):
        """
        Инициализировать корзину. 
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # сохранить пустую корзину в сеансе
            cart = self.session[settings.CART_SESSION_ID] = {} 
        self.cart = cart
        self.removed_items = []  # Список удалённых товаров для уведомлений

    def add(self, product, quantity=1, override_quantity=False, size=None):
        """Добавить товар в корзину либо обновить его количество."""
        product_id = str(product.id)
        unique_key = f"{product_id}_{size}"

        # Получаем объект Size
        try:
            size_object = Size.objects.get(title=size)  # Получаем объект Size по title
            product_price = product.product_prices.get(size=size_object)  # Используем size
        except Size.DoesNotExist:
            print(f"Размер {size} не найден.")  # Удалите print для prod
            return
        except ProductPrice.DoesNotExist:
            print(f"Цена для размера {size} не найдена.")
            return

        if unique_key not in self.cart:
            # Получаем первое изображение
            first_image = product.images.first()  # Получаем первое изображение
            image_url = first_image.image.url if first_image else None  # Сохраняем URL изображения

            self.cart[unique_key] = {
                'product_id': product_id,  # Сохраняем id продукта
                'article_number': product.article_number,
                'title': product.title,  # Сохраняем название продукта
                'size': size,
                'quantity': 0,
                'price': str(product_price.price),  # Сохраняем как строку (для JSON-сериализации)
                'image': image_url,  # Сохраняем изображение
                'url': product.get_absolute_url()  # Сохраняем URL продукта
            }

        # Обновление количества товара в корзине
        current_quantity = self.cart[unique_key]['quantity']
        if override_quantity:
            new_quantity = quantity
        else:
            new_quantity = current_quantity + quantity

        # Жёсткая проверка максимума: обрезаем до 100
        new_quantity = min(new_quantity, MAX_QUANTITY)
        self.cart[unique_key]['quantity'] = new_quantity

        # Удаляем print для production
        # print(f"{unique_key}: Добавление товара: {product_id}, размер: {size}, количество: {quantity}, переопределить: {override_quantity}")
        # print("Текущая корзина:", self.cart)
        
        self.save()
        
    # Остальные методы без изменений (save, remove, __iter__, __len__, get_total_price, clear, get_item, get_all_items_json)
    def save(self):
        # пометить сеанс как "измененный",
        # чтобы обеспечить его сохранение
        self.session.modified = True
    
    def remove(self, product, size=None):
        """
        Удалить товар из корзине.
        """
        product_id = str(product.id)
        size_id = str(size)
        unique_key = f"{product_id}_{size_id}"

        if unique_key in self.cart:
            del self.cart[unique_key]
            self.save()
    
    def __iter__(self):
        """
        Перебирает товары в корзине, проверяя их существование в базе.
        Если товар/размер удалён, удаляет из сессии и добавляет в removed_items для уведомления.
        """
        items_to_remove = []  # Список ключей для удаления
        for unique_key, item in list(self.cart.items()):  # Используем list(), чтобы избежать изменений во время итерации
            try:
                product_id = item['product_id']
                size_title = item['size']
                
                # Проверяем существование продукта
                product = Product.objects.get(id=product_id)
                
                # Проверяем существование размера
                size_obj = Size.objects.get(title=size_title)
                
                # Проверяем существование ProductPrice (цена для размера) — только для валидации
                ProductPrice.objects.get(product=product, size=size_obj)  # Убираем присваивание, просто проверяем существование
                
                # Если всё ок, продолжаем как обычно
                item_copy = item.copy()
                item_copy['price'] = Decimal(item_copy['price'])
                item_copy['total_price'] = item_copy['price'] * item_copy['quantity']
                item_copy['size'] = size_title
                item_copy['max_quantity'] = MAX_QUANTITY
                yield item_copy
            
            except (Product.DoesNotExist, Size.DoesNotExist, ProductPrice.DoesNotExist):
                # Товар/размер удалён — добавляем в список для удаления и уведомления
                self.removed_items.append({
                    'title': item['title'],
                    'article_number': item['article_number'],
                    'size': item['size']
                })
                items_to_remove.append(unique_key)
                continue  # Пропускаем этот товар
        
        # Удаляем несуществующие товары из сессии
        for key in items_to_remove:
            del self.cart[key]
        self.save()  # Сохраняем сессию после изменений

    
    def __len__(self):
        """
        Подсчитать все товарные позиции в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']  # Преобразуем из строки в Decimal
            for item in self.cart.values())
    
    def clear(self):
        # удалить корзину из сеанса
        del self.session[settings.CART_SESSION_ID]
        self.save()
    
    def get_cart_items(self):
        return self.cart
    
    # Добавленный метод для получения данных конкретного товара
    def get_item(self, product_id, size):
        """
        Возвращает данные товара в корзине по product_id и size.
        Преобразует типы для совместимости с JSON.
        Возвращает словарь или None, если товар не найден.
        """
        unique_key = f"{product_id}_{size}"
        if unique_key in self.cart:
            item = self.cart[unique_key].copy()
            item['price'] = Decimal(item['price'])  # Преобразуем в Decimal
            item['total_price'] = item['price'] * item['quantity']  # Decimal
            # Преобразование в строки для JSON
            item['price'] = str(item['price'])
            item['total_price'] = str(item['total_price'])
            item['quantity'] = str(item['quantity'])
            return item
        return None

    # Новый метод: Получить все items в JSON-готовом формате (для будущего использования)
    def get_all_items_json(self):
        items = []
        for unique_key, item in self.cart.items():
            item_data = item.copy()
            item_data['price'] = str(Decimal(item['price']))  # Преобразуем в Decimal, затем в строку
            item_data['total_price'] = str(Decimal(item['price']) * item['quantity'])  # Decimal расчёт, затем строка
            item_data['quantity'] = str(item['quantity'])
            item_data['product_id'] = item['product_id']
            item_data['size'] = unique_key.split('_')[1]  # Размер из ключа
            items.append(item_data)
        return items


    def get_removed_items(self):
        """
        Возвращает список удалённых товаров и очищает его (чтобы уведомления показывались только один раз).
        """
        removed = self.removed_items[:]
        self.removed_items = []
        return removed
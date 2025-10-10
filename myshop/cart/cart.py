# from decimal import Decimal
# from django.conf import settings
# from home.models import Product, ProductPrice, Size




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


#         print(f"{unique_key}: Добавление товара: {product_id}, размер: {size}, количество: {quantity}, переопределить: {override_quantity}")

#         # Получаем объект Size
#         try:
#             size_object = Size.objects.get(title=size)  # Получаем объект Size по title
#             product_price = product.product_prices.get(size=size_object)  # Используем size
#         except Size.DoesNotExist:
#             print(f"Размер {size} не найден.")
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
#                 'price': str(product_price.price),
#                 'image': image_url,  # Сохраняем изображение
#                 'url': product.get_absolute_url()  # Сохраняем URL продукта
#             }

#         # Обновление количества товара в корзине
#         if override_quantity:
#             self.cart[unique_key]['quantity'] = quantity
#         else:
#             self.cart[unique_key]['quantity'] += quantity

#         print("Текущая корзина:", self.cart)
#         self.save()
        
        
    
    
#     def save(self):
#         # пометить сеанс как "измененный",
#         # чтобы обеспечить его сохранение
#         self.session.modified = True
    


#     def remove(self, product, size=None):
#         """
#         Удалить товар из корзины.
#         """
#         product_id = str(product.id)
#         size_id = str(size)
#         unique_key = f"{product_id}_{size_id}"

#         if unique_key in self.cart:
#             del self.cart[unique_key]
#             self.save()
    


#     def __iter__(self):
#         for size_key, item in self.cart.items():
#             item['price'] = Decimal(item['price'])
#             item['total_price'] = item['price'] * item['quantity']
#             item['size'] = size_key.split('_')[1]  # Получаем размер из ключа
            
#             yield item

    
#     def __len__(self):
#         """
#         Подсчитать все товарные позиции в корзине.
#         """
#         return sum(item['quantity'] for item in self.cart.values())
    

#     def get_total_price(self):
#         return sum(
#             Decimal(item['price']) * item['quantity']
#             for item in self.cart.values())
    
    
#     def clear(self):
#         # удалить корзину из сеанса
#         del self.session[settings.CART_SESSION_ID]
#         self.save()

    
#     def get_cart_items(self):
#         return self.cart




from decimal import Decimal
from django.conf import settings
from home.models import Product, ProductPrice, Size

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

    def add(self, product, quantity=1, override_quantity=False, size=None):
        """Добавить товар в корзину либо обновить его количество."""
        product_id = str(product.id)
        unique_key = f"{product_id}_{size}"

        print(f"{unique_key}: Добавление товара: {product_id}, размер: {size}, количество: {quantity}, переопределить: {override_quantity}")

        # Получаем объект Size
        try:
            size_object = Size.objects.get(title=size)  # Получаем объект Size по title
            product_price = product.product_prices.get(size=size_object)  # Используем size
        except Size.DoesNotExist:
            print(f"Размер {size} не найден.")
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
                'price': str(product_price.price),
                'image': image_url,  # Сохраняем изображение
                'url': product.get_absolute_url()  # Сохраняем URL продукта
            }

        # Обновление количества товара в корзине
        if override_quantity:
            self.cart[unique_key]['quantity'] = quantity
        else:
            self.cart[unique_key]['quantity'] += quantity

        print("Текущая корзина:", self.cart)
        self.save()
        
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
        for size_key, item in self.cart.items():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            item['size'] = size_key.split('_')[1]  # Получаем размер из ключа
            
            yield item
    
    def __len__(self):
        """
        Подсчитать все товарные позиции в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
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
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            # Преобразование в строки для JSON (как предлагалось ранее)
            item['price'] = str(item['price'])
            item['total_price'] = str(item['total_price'])
            item['quantity'] = str(item['quantity'])
            return item
        return None

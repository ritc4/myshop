from django import forms 
from .models import Order,DeliveryMethod



class OrderCreateForm(forms.ModelForm):

    DELIVERY_CHOICES = [
        (0, 'Выбирите способ доставки'),
        (1, 'Почта России (russianpost.ru)'),
        (2, 'EMS Почта России'),
        (4, 'Байкал сервис'),
        (5, 'Деловые линии'),
        (6, 'ЖелДор Экспедиция'),
        (7, 'ПЭК'),
        (8, 'Кит - транспортная компания'),
        (9, 'Энергия'),
        (10, 'СДЭК'),
    ]

    delivery_method = forms.ChoiceField(
        choices=DELIVERY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'aria-label': 'Default select example',
            'id': 'shipmethod',
            'onchange': 'toggleAdditionalCol()',
        }),
        initial=0  # Установите значение по умолчанию
    )
 
    class Meta: 
        model = Order
        fields = [
            'delivery',
            'first_name_last_name', 
            'email',
            'phone',
            'region',
            'city',
            'address',
            'passport_number',
            'comment',
            'zamena_product',
            'strahovat_gruz'
        ]
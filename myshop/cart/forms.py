from django import forms
from home.models import ProductPrice  # Импортируем модель ProductPrice для получения размеров


PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 101)]

class CartAddProductForm(forms.Form):
    
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES, 
        coerce=int
    )

    override = forms.BooleanField(
        required=False, 
        initial=False,
        widget=forms.HiddenInput
    )
    
    size = forms.ChoiceField(
        choices=[],  # Изначально пустой список
        required=True,  # По умолчанию обязательное поле
        label="Выберите размер",
    )

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)  # Получаем продукт из аргументов
        sizes = kwargs.pop('sizes', [])  # Получаем размеры из аргументов
        super().__init__(*args, **kwargs)
        self.fields['size'].choices = sizes  # Устанавливаем доступные размеры
        

        if sizes:
            self.fields['size'].choices = sizes  # Устанавливаем размеры и цены

            # Устанавливаем начальное значение для размера с минимальной ценой
            if self.fields['size'].choices:
                min_price_size = min(sizes, key=lambda x: x[1])  # Находим размер с минимальной ценой
                self.fields['size'].initial = min_price_size[0]  # Устанавливаем начальное значение
            else:
                # Если размеров нет, можно оставить поле обязательным или выдать ошибку
                self.fields['size'].required = True  # Оставляем обязательным, если размеры отсутствуют

    def clean_size(self):
        size = self.cleaned_data.get('size')
        print(f"Полученное значение размера: {size}")
        print(f"Допустимые значения: {dict(self.fields['size'].choices)}")
        if size not in dict(self.fields['size'].choices):
            raise forms.ValidationError("Выберите корректный вариант.")
        return size


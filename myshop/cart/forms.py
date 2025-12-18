from django import forms
from home.models import ProductPrice  # Импортируем модель ProductPrice для получения размеров

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 101)]

class CartAddProductForm(forms.Form):
    
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES, 
        coerce=int,
        widget=forms.NumberInput(attrs={'min': 1, 'max': 100})  # Добавлено: клиентская валидация min/max
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
        
        # Устанавливаем доступные размеры (убрал дублирование)
        self.fields['size'].choices = sizes

        if sizes:
            # Устанавливаем начальное значение для размера с минимальной ценой (исправлено: float для min)
            if self.fields['size'].choices:
                min_price_size = min(sizes, key=lambda x: float(x[1]))  # float(x[1]) для корректного min по цене
                self.fields['size'].initial = min_price_size[0]  # Устанавливаем начальное значение
            else:
                # Если размеров нет, оставляем поле обязательным
                self.fields['size'].required = True
                self.fields['size'].initial = None  # Явно None, если пусто

    def clean_size(self):
        size = self.cleaned_data.get('size')
        # Убрал print для production
        # print(f"Полученное значение размера: {size}")
        # print(f"Допустимые значения: {[choice[0] for choice in self.fields['size'].choices]}")
        
        if size not in [choice[0] for choice in self.fields['size'].choices]:
            raise forms.ValidationError("Выберите корректный вариант.")
        return size

    def clean_quantity(self):
        """Серверная проверка максимума для quantity."""
        quantity = self.cleaned_data.get('quantity') 
        if quantity > 100:
            raise forms.ValidationError("Максимум 100 единиц за раз.")
        return min(quantity, 100)  # Обрезаем до 100 на всякий случай

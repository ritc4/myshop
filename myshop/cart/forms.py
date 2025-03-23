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
        super().__init__(*args, **kwargs)
        
        if product:
            try:
                sizes = ProductPrice.objects.filter(product=product).select_related('size')
                self.fields['size'].choices = [(size.size.title, size.price) for size in sizes]

                if self.fields['size'].choices:
                    min_price_size = min(sizes, key=lambda x: x.price)  # Находим размер с минимальной ценой
                    self.fields['size'].initial = min_price_size.size.title
                else:
                    # Если размеров нет, можно оставить поле обязательным или выдать ошибку
                    self.fields['size'].required = True  # Оставляем обязательным, если размеры отсутствуют

            except Exception as e:
                # Логируем ошибку
                print(f"Ошибка при загрузке размеров: {e}")

    def clean_size(self):
        size = self.cleaned_data.get('size')
        # Здесь можно добавить дополнительную логику валидации, если нужно
        return size



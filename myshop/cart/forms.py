from django import forms
from home.models import Size  # Предполагаем, что у вас есть модель Size

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
            # Получаем размеры для данного продукта
            sizes = product.size.all()
            # Создаем список кортежей (имя, имя) для выбора
            self.fields['size'].choices = [(size.title, size.title) for size in sizes]
            
            # Устанавливаем required=False, если размеров нет
            if not self.fields['size'].choices:
                self.fields['size'].required = False  # Делаем поле необязательным
        print(self.fields['size'].choices)
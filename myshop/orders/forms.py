from django import forms 
from .models import Order,DeliveryMethod



class OrderCreateForm(forms.ModelForm):

    delivery_method = forms.ModelChoiceField(
        queryset=DeliveryMethod.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'aria-label': 'Default select example',
            'id': 'shipmethod',
            'onchange': 'toggleAdditionalCol()',
        }),
        empty_label="Выберите способ доставки"
    )
 
    class Meta: 
        model = Order
        fields = [
            'delivery_method',
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
    

        # def __init__(self, *args, **kwargs):
        #     super().__init__(*args, **kwargs)
        #     self.fields['size'].widget = forms.HiddenInput()  # Скрываем поле
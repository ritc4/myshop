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
        empty_label="Выберите способ доставки",
        label="Выберите способ доставки",  # Устанавливаем нужную метку
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
            'postal_code',
            'passport_number',
            'comment',
            'zamena_product',
            'strahovat_gruz',
            'soglasie_na_obrabotku_danyh',
            'soglasie_na_uslovie_sotrudnichestva',
        ]

        labels = {
            'delivery_method':'Доставка',
            'first_name_last_name': 'Фамилия Имя Отчество',
            'email': 'Электронный адрес',
            'phone': 'Телефон',
            'region': 'Регион',
            'city': 'Город',
            'address': 'Адрес',
            'postal_code': 'Почтовый индекс',
            'passport_number':'Паспортные данные',
            'comment':'Комментарии к заказу',
            'zamena_product':'Не предлагать замену товаров',
            'strahovat_gruz':'Cтраховать груз',
            'soglasie_na_obrabotku_danyh':"Согласие на обработку персональных данных",
            'soglasie_na_uslovie_sotrudnichestva':"Согласие с условиями сотрудничества",  
        }


        widgets = {
            'delivery_method': forms.Select(attrs={'class': 'form-control', 'id': 'delivery_method', 'name': 'delivery_method'}),
            'first_name_last_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'first_name_last_name', 'name': 'first_name_last_name', 'autocomplete': 'name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'email', 'name': 'email', 'autocomplete': 'email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'id': 'phone', 'name': 'phone', 'autocomplete': 'tel'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'id': 'region', 'name': 'region', 'autocomplete': 'address-level1'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'id': 'city', 'name': 'city', 'autocomplete': 'address-level2'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'id': 'address', 'name': 'address', 'autocomplete': 'street-address'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'id': 'postal_code', 'name': 'postal_code', 'autocomplete': 'postal-code'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control', 'id': 'passport_number', 'name': 'passport_number', 'autocomplete': 'off'}),  # Отключаем автозаполнение для паспортных данных
            'comment': forms.Textarea(attrs={'class': 'form-control', 'id': 'comment', 'name': 'comment', 'rows': 4}),
            'zamena_product': forms.CheckboxInput(attrs={'class': 'form-input-row checkbox', 'id': 'zamena_product', 'name': 'zamena_product'}),
            'soglasie_na_obrabotku_danyh': forms.CheckboxInput(attrs={'class': 'form-input-row checkbox', 'id': 'soglasie_na_obrabotku_danyh', 'name': 'soglasie_na_obrabotku_danyh'}),
            'soglasie_na_uslovie_sotrudnichestva': forms.CheckboxInput(attrs={'class': 'form-input-row checkbox', 'id': 'soglasie_na_uslovie_sotrudnichestva', 'name': 'soglasie_na_uslovie_sotrudnichestva'}),
        }


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(OrderCreateForm, self).__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['delivery_method'].initial = user.delivery_method
            self.fields['first_name_last_name'].initial = getattr(user, 'first_name', '')  # Или используйте нужное поле
            self.fields['email'].initial = user.email
            self.fields['phone'].initial = getattr(user, 'phone', '')  # Предполагается, что поле phone есть в модели пользователя
            self.fields['region'].initial = getattr(user, 'region', '')
            self.fields['city'].initial = getattr(user, 'city', '')
            self.fields['address'].initial = getattr(user, 'address', '')
            self.fields['postal_code'].initial = getattr(user, 'postal_code', '')
            
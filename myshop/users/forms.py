from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm, PasswordChangeForm
from captcha.fields import CaptchaField

class LoginUserForm(AuthenticationForm):
    username = forms.CharField( 
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'username',  # Добавляем id
            'name': 'username',  # Добавляем name
            'autocomplete': 'username'  # Добавляем autocomplete
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password',  # Добавляем id
            'name': 'password',  # Добавляем name
            'autocomplete': 'current-password'  # Добавляем autocomplete
        })
    )

    # Добавляем CAPTCHA поле
    captcha = CaptchaField(
        label='Введите текст с картинки'  # Метка для поля
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']

class RegisterUserForm(UserCreationForm):  
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'username',  # Добавляем id
            'name': 'username',  # Добавляем name
            'autocomplete': 'username'  # Добавляем autocomplete
        })
    )
    first_name = forms.CharField(
        label='ФИО',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'first_name',  # Добавляем id
            'name': 'first_name',  # Добавляем name
            'autocomplete': 'given-name'  # Добавляем autocomplete
        })
    )
    email = forms.EmailField(
        label='Электронная почта',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'email',  # Добавляем id
            'name': 'email',  # Добавляем name
            'autocomplete': 'email'  # Добавляем autocomplete
        })
    )
    phone = forms.CharField(
        label='Телефон для связи',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'phone',  # Добавляем id
            'name': 'phone',  # Добавляем name
            'autocomplete': 'tel'  # Добавляем autocomplete
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password1',  # Добавляем id
            'name': 'password1',  # Добавляем name
            'autocomplete': 'new-password'  # Добавляем autocomplete
        })
    )
    password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password2',  # Добавляем id
            'name': 'password2',  # Добавляем name
            'autocomplete': 'new-password'  # Добавляем autocomplete
        })
    )

    # Добавляем CAPTCHA поле
    captcha = CaptchaField(
        label='Введите текст с картинки'  # Метка для поля
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name','email', 'phone', 'password1', 'password2']

        
    def clean_email (self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Такой E-mail уже существует!')
        return email
    

class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(
        disabled=True,
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'username',  # Добавляем id
            'name': 'username',  # Добавляем name
            'autocomplete': 'username'  # Добавляем autocomplete
        })
    )
    email = forms.EmailField( 
        disabled=True,
        label='E-mail',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'email',  # Добавляем id
            'name': 'email',  # Добавляем name
            'autocomplete': 'email'  # Добавляем autocomplete
        })
    )

    class Meta:
        model = get_user_model()
        fields = ['photo', 'username', 'email', 'first_name', 'phone', 'region', 'city', 'address', 'postal_code', 'delivery_method']
        labels = {
            'first_name': 'ФИО',
            'region': 'Регион',
            'city': 'Город',
            'address': 'Адрес',
            'postal_code': 'Почтовый индекс',
            'delivery_method': 'Доставка',
            'photo': 'Фотография',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'first_name',  # Добавляем id
                'name': 'first_name',  # Добавляем name
                'autocomplete': 'given-name'  # Добавляем autocomplete
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'phone',  # Добавляем id
                'name': 'phone',  # Добавляем name
                'autocomplete': 'tel'  # Добавляем autocomplete
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'region',  # Добавляем id
                'name': 'region',  # Добавляем name
                'autocomplete': 'address-level1'  # Добавляем autocomplete
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'city',  # Добавляем id
                'name': 'city',  # Добавляем name
                'autocomplete': 'address-level2'  # Добавляем autocomplete
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'address',  # Добавляем id
                'name': 'address',  # Добавляем name
                'autocomplete': 'street-address'  # Добавляем autocomplete
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'postal_code',  # Добавляем id
                'name': 'postal_code',  # Добавляем name
                'autocomplete': 'postal-code'  # Добавляем autocomplete
            }),
            'delivery_method': forms.Select(attrs={
                'class': 'form-control',
                'id': 'delivery_method',  # Добавляем id
                'name': 'delivery_method',  # Добавляем name
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем нужные поля обязательными на форме
        required_fields = [
            'first_name',
            'phone',
            'region',
            'city',
            'address',
            'postal_code',
            'delivery_method',
        ]
        for field_name in required_fields:
            self.fields[field_name].required = True


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
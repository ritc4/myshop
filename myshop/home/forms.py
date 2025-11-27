# from django import forms  # Импортируем модуль forms
# from .models import Review



# class MultipleFileInput(forms.ClearableFileInput):
#     allow_multiple_selected = True


# class MultipleFileField(forms.FileField):
#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault("widget", MultipleFileInput())
#         super().__init__(*args, **kwargs)

#     def clean(self, data, initial=None):
#         single_file_clean = super().clean
#         if isinstance(data, (list, tuple)):
#             result = [single_file_clean(d, initial) for d in data]
#         else:
#             result = [single_file_clean(data, initial)]
#         return result




# class ReviewForm(forms.ModelForm):

#     images = MultipleFileField(required=False,label='Загрузите изображение:',)  # Добавляем поле для загрузки нескольких файлов

#     kachestvo_rating = forms.ChoiceField(
#         choices=[(i, str(i)) for i in range(1, 6)],
#         widget=forms.Select(attrs={'class': 'star-rating'}),
#         label='Качество товара:'
#     )

#     obsluga_rating = forms.ChoiceField(
#         choices=[(i, str(i)) for i in range(1, 6)],
#         widget=forms.Select(attrs={'class': 'star-rating'}),
#         label='Качество обслуживания:'
#     )

#     sroki_rating = forms.ChoiceField(
#         choices=[(i, str(i)) for i in range(1, 6)],
#         widget=forms.Select(attrs={'class': 'star-rating'}),
#         label='Соблюдение сроков:'
#     )

#     class Meta:
#         model = Review
#         fields = ['content', 'kachestvo_rating', 'obsluga_rating', 'sroki_rating', 'images']
#         labels = {
#             'kachestvo_rating': 'Качество товара',
#             'obsluga_rating': 'Качество обслуживания',
#             'sroki_rating': 'Соблюдение сроков',
#             'images': 'Загрузите фото',
#         }
        
#         widgets = {
#             'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Напишите ваш отзыв...'}),
#         }


# from django import forms
# from django.core.exceptions import ValidationError
# from .models import Review
# from captcha.fields import CaptchaField 

# def validate_file_size(value):
#     """Валидатор размера файла (макс. 20 МБ)"""
#     max_size = 20 * 1024 * 1024  # 20 MB
#     if hasattr(value, 'size') and value.size > max_size:
#         raise ValidationError(f'Размер файла превышает {max_size / (1024 * 1024)} МБ.')
#     return value

# class MultipleFileInput(forms.ClearableFileInput):
#     allow_multiple_selected = True

# class MultipleFileField(forms.FileField):
#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault("widget", MultipleFileInput())
#         super().__init__(*args, **kwargs)

#     def clean(self, data, initial=None):
#         single_file_clean = super().clean
#         if isinstance(data, (list, tuple)):
#             result = [single_file_clean(d, initial) for d in data]
#         else:
#             result = [single_file_clean(data, initial)]
#         return result

# class ReviewForm(forms.ModelForm):
#     images = MultipleFileField(
#         required=False,
#         label='Загрузите изображение:',
#         validators=[validate_file_size],  # Валидация размера каждого файла
#         widget=MultipleFileInput(attrs={'accept': 'image/*', 'style': 'display: none;'})
#     )

#     kachestvo_rating = forms.ChoiceField(
#         choices=[(i, str(i)) for i in range(1, 6)],
#         widget=forms.Select(attrs={'class': 'star-rating', 'required': False}),
#         label='Качество товара:'
#     )

#     obsluga_rating = forms.ChoiceField(
#         choices=[(i, str(i)) for i in range(1, 6)],
#         widget=forms.Select(attrs={'class': 'star-rating', 'required': False}),
#         label='Качество обслуживания:'
#     )

#     sroki_rating = forms.ChoiceField(
#         choices=[(i, str(i)) for i in range(1, 6)],
#         widget=forms.Select(attrs={'class': 'star-rating', 'required': False}),
#         label='Соблюдение сроков:'
#     )

#     class Meta:
#         model = Review
#         fields = ['content', 'kachestvo_rating', 'obsluga_rating', 'sroki_rating', 'images']
#         labels = {
#             'kachestvo_rating': 'Качество товара',
#             'obsluga_rating': 'Качество обслуживания',
#             'sroki_rating': 'Соблюдение сроков',
#             'images': 'Загрузите фото',
#         }
        
#         widgets = {
#             'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Напишите ваш отзыв...', 'required': False}),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         images = self.files.getlist('images') if self.files else []
#         content = cleaned_data.get('content', '').strip()
        
#         # Валидация текста отзыва (обязательно)
#         if not content:
#             raise forms.ValidationError('Пожалуйста, напишите текст отзыва.')
        
#         # Валидация изображений: максимум 5 файлов
#         max_files = 5
#         if len(images) > max_files:
#             raise forms.ValidationError(f'Максимум {max_files} изображений.')
        
#         # Валидация общего размера изображений (не более 100 MB)
#         max_total_size = 100 * 1024 * 1024  # 100 MB
#         total_size = sum(file.size for file in images)
#         if total_size > max_total_size:
#             raise forms.ValidationError(f'Общий размер изображений не должен превышать {max_total_size / (1024 * 1024)} МБ.')
        
#         # Валидация рейтингов (все обязательны)
#         required_ratings = ['kachestvo_rating', 'obsluga_rating', 'sroki_rating']
#         for rating in required_ratings:
#             if not cleaned_data.get(rating):
#                 raise forms.ValidationError(f'Пожалуйста, установите рейтинг для "{self.fields[rating].label}".')
        
#         return cleaned_data


# class ContactForm(forms.Form):
#     first_name = forms.CharField(
#         label='Представьтесь',
#         required=True,  # Сделаем поле необязательным
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'id': 'first_name',  
#             'name': 'first_name',  
#             'autocomplete': 'given-name'  
#         })
#     )
#     email = forms.EmailField(
#         required=True, 
#         label='E-mail',
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'id': 'email',  
#             'name': 'email',  
#             'autocomplete': 'email'  
#         })
#     )
#     phone = forms.CharField(
#         required=False,  # Сделаем поле необязательным
#         label='Телефон для связи',
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'id': 'phone',  
#             'name': 'phone',  
#             'autocomplete': 'tel'  
#         })
#     )
#     content = forms.CharField(
#         required=True,
#         label='Сообщение',
#         widget=forms.Textarea(attrs={
#             'class': 'form-control',
#             'rows': 4,
#             'placeholder': 'Напишите нам...'
#         })
#     )
    
#     # Добавляем CAPTCHA поле
#     captcha = CaptchaField(
#         label='Введите текст с картинки'  # Метка для поля
#     )

#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)
#         super(ContactForm, self).__init__(*args, **kwargs)
#         if user and user.is_authenticated:
#             self.fields['first_name'].initial = getattr(user, 'first_name', '')
#             self.fields['email'].initial = user.email
#             self.fields['phone'].initial = getattr(user, 'phone', '')  # Убедитесь, что поле phone есть в модели пользователя
    

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if not email:
#             raise forms.ValidationError('Это поле обязательно для заполнения.')
#         return email
    







from django import forms
from django.core.exceptions import ValidationError
from .models import Review
from captcha.fields import CaptchaField

def validate_file_size(value):
    """Валидатор размера файла (макс. 20 МБ)"""
    max_size = 20 * 1024 * 1024  # 20 MB
    if hasattr(value, 'size') and value.size > max_size:
        raise ValidationError(f'Размер файла превышает {max_size / (1024 * 1024)} МБ.')
    return value

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class ReviewForm(forms.ModelForm):
    images = MultipleFileField(
        required=False,
        label='Загрузите изображение:',
        validators=[validate_file_size],  # Валидация размера каждого файла
        widget=MultipleFileInput(attrs={'accept': 'image/*', 'style': 'display: none;'})
    )

    kachestvo_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'star-rating', 'required': True}),
        required=True,
        label='Качество товара:'
    )

    obsluga_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'star-rating', 'required': True}),
        required=True,
        label='Качество обслуживания:'
    )

    sroki_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'star-rating', 'required': True}),
        required=True,
        label='Соблюдение сроков:'
    )

    class Meta:
        model = Review
        fields = ['content', 'kachestvo_rating', 'obsluga_rating', 'sroki_rating', 'images']
        labels = {
            'kachestvo_rating': 'Качество товара',
            'obsluga_rating': 'Качество обслуживания',
            'sroki_rating': 'Соблюдение сроков',
            'images': 'Загрузите фото',
        }
        
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Напишите ваш отзыв...', 'required': False}),
        }

    def clean(self):
        cleaned_data = super().clean()
        images = self.files.getlist('images') if self.files else []
        content = cleaned_data.get('content', '').strip()
        
        # Валидация текста отзыва (обязательно)
        if not content:
            raise forms.ValidationError('Пожалуйста, напишите текст отзыва.')
        
        # Валидация рейтингов (обязательно: должны быть от 1 до 5 для каждого поля)
        required_ratings = ['kachestvo_rating', 'obsluga_rating', 'sroki_rating']
        for rating_field in required_ratings:
            rating_value = cleaned_data.get(rating_field)
            if not rating_value or not (1 <= int(rating_value) <= 5):
                raise forms.ValidationError('Все рейтинги обязательны и должны быть от 1 до 5.')
        
        # Валидация изображений: максимум 5 файлов
        max_files = 5
        if len(images) > max_files:
            raise forms.ValidationError(f'Максимум {max_files} изображений.')
        
        # Валидация общего размера изображений (не более 100 MB)
        max_total_size = 100 * 1024 * 1024  # 100 MB
        total_size = sum(file.size for file in images)
        if total_size > max_total_size:
            raise forms.ValidationError(f'Общий размер изображений не должен превышать {max_total_size / (1024 * 1024)} МБ.')
        
        return cleaned_data

class ContactForm(forms.Form):
    first_name = forms.CharField(
        label='Представьтесь',
        required=True,  # Сделаем поле необязательным
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'first_name',  
            'name': 'first_name',  
            'autocomplete': 'given-name'  
        })
    )
    email = forms.EmailField(
        required=True, 
        label='E-mail',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'email',  
            'name': 'email',  
            'autocomplete': 'email'  
        })
    )
    phone = forms.CharField(
        required=False,  # Сделаем поле необязательным
        label='Телефон для связи',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'phone',  
            'name': 'phone',  
            'autocomplete': 'tel'  
        })
    )
    content = forms.CharField(
        required=True,
        label='Сообщение',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Напишите нам...'
        })
    )
    
    # Добавляем CAPTCHA поле
    captcha = CaptchaField(
        label='Введите текст с картинки'  # Метка для поля
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ContactForm, self).__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['first_name'].initial = getattr(user, 'first_name', '')
            self.fields['email'].initial = user.email
            self.fields['phone'].initial = getattr(user, 'phone', '')  # Убедитесь, что поле phone есть в модели пользователя
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Это поле обязательно для заполнения.')
        return email

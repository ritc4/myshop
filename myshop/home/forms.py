from django import forms  # Импортируем модуль forms
from .models import Review



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

    images = MultipleFileField(required=False,label='Загрузите изображение:',)  # Добавляем поле для загрузки нескольких файлов

    kachestvo_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'star-rating'}),
        label='Качество товара:'
    )

    obsluga_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'star-rating'}),
        label='Качество обслуживания:'
    )

    sroki_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'star-rating'}),
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
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Напишите ваш отзыв...'}),
        }


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
        required=False,
        label='Сообщение',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Напишите нам...'
        })
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
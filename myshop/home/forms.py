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

    images = MultipleFileField(required=False)  # Добавляем поле для загрузки нескольких файлов

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


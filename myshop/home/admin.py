from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from mptt.admin import DraggableMPTTAdmin
from .models import Category,Size,Product

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('title',)  # Отображение названия размера в админке
    search_fields = ['title']  # Определяем поле для поиска


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'article_number', 'stock', 'unit', 'image', 'is_hidden', 'get_sizes_display','price','category','created','updated','mesto')  # Отображение полей продукта в админке
    list_filter = ('is_hidden','category','created','updated','mesto')
    prepopulated_fields = {'slug':('title','article_number',)}
    filter_horizontal = ('size',)  # Используем горизонтальный фильтр для выбора 
    search_fields = ['title']  # Позволяет искать продукты по названию
    list_editable = ['price', 'is_hidden','mesto']

    # Определяем действия для скрытия и показа товаров
    actions = ['hide_products', 'show_products']

    def hide_products(self, request, queryset):
        queryset.update(is_hidden=True)  # Скрываем выбранные товары
        self.message_user(request, f"{queryset.count()} товаров успешно скрыто.")

    hide_products.short_description = "Скрыть выбранные товары"  # Описание действия

    def show_products(self, request, queryset):
        queryset.update(is_hidden=False)  # Показываем выбранные товары
        self.message_user(request, f"{queryset.count()} товаров успешно показано.")

    show_products.short_description = "Показать выбранные товары"  # Описание действия

    def get_sizes_display(self, obj):
        return ", ".join([size.title for size in obj.size.all()])
    
    get_sizes_display.short_description = 'size'  # Название колонки в админке



admin.site.register(Category,DraggableMPTTAdmin,
    list_display=('tree_actions','indented_title','image'),
    list_display_links=('indented_title',),
    prepopulated_fields = {'slug':('name',)})
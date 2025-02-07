from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from mptt.admin import DraggableMPTTAdmin
from .models import Category


# class CategoryAdmin(MPTTModelAdmin):
#     Category,
#     DraggableMPTTAdmin,
#     list_display=(
#         'tree_actions',
#         'indented_title',),
#     list_display_links=(
#         'indented_title',),
#     prepopulated_fields = {slug:("name")}

admin.site.register(
    Category,
    DraggableMPTTAdmin,
    list_display=(
        'tree_actions',
        'indented_title',),
    list_display_links=(
        'indented_title',),
    prepopulated_fields = {'slug':('name',)})
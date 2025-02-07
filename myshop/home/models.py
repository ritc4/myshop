from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse

class Category(MPTTModel):
    name = models.CharField(max_length=255, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    slug = models.SlugField(max_length=255,verbose_name='Url',unique=True)

    def get_absolute_url(self):
        return reverse("home:category", kwargs={"slug": self.slug})
    
    def __str__(self):
        return self.name
    

    class MPTTMeta:
        order_insertion_by = ['name']
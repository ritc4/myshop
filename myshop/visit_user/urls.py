from django.urls import path
from .views import visit_view

app_name = 'visit_user'

urlpatterns = [
    path('visits/', visit_view, name='visit_view'),
]
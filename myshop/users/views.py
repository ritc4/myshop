from .forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.contrib.auth import get_user_model
from orders.models import Order
from home.models import ProductPrice
from django.core.paginator import Paginator
from .models import User
import os


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title':'Авторизация'}


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title':'Регистрация'}
    success_url = reverse_lazy ('users:login')


class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': "Профиль пользователя"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Настройка хлебных крошек
        context['breadcrumbs'] = [
            {'name': 'Профиль пользователя', 'slug': '/profile/'},
        ]

        # Изменено: Если добавлено поле user в Order, используйте filter(user=self.request.user) вместо email
        # Комментирую оба варианта для ясности; уберите, что не нужно
        # Если Order имеет user field:
        # orders = Order.objects.filter(user=self.request.user) \
        #     .select_related('delivery_method') \
        #     .prefetch_related('items__product_price', 'items__product_price__product')  # Если product_price вместо/к product
        # Если остался фильтр по email:
        orders = Order.objects.filter(email=self.request.user.email) \
            .select_related('delivery_method') \
            .prefetch_related('items__product_price', 'items__product_price__product')

        # Пагинация (без изменений)
        paginator = Paginator(orders, 20)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['orders'] = page_obj
        context['paginator'] = paginator
        context['show_pagination'] = page_obj.has_other_pages

        if page_obj.has_other_pages:
            pages_to_show = 5
            half = pages_to_show // 2
            start_page = max(1, page_obj.number - half)
            end_page = min(paginator.num_pages, page_obj.number + half)

            if end_page - start_page < pages_to_show - 1:
                if start_page == 1:
                    end_page = min(paginator.num_pages, start_page + pages_to_show - 1)
                elif end_page == paginator.num_pages:
                    start_page = max(1, end_page - pages_to_show + 1)

            context["page_range"] = range(start_page, end_page + 1)
        else:
            context['page_range'] = []

        return context

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        # Логика перезаписи файла (без изменений)
        instance = form.instance
        if instance.pk:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.photo and instance.photo != old_instance.photo:
                if os.path.isfile(old_instance.photo.path):
                    os.remove(old_instance.photo.path)
        return super().form_valid(form)


# class OrderDetailView(LoginRequiredMixin, DetailView):
#     model = Order
#     template_name = 'orders/order/order_detail.html'
#     context_object_name = 'order'

#     def get_queryset(self):
#         # Изменено: Обновите prefetch_related, если добавлен product_price
#         return Order.objects.select_related('delivery_method').prefetch_related('items__product_price', 'items__product_price__product')  # Если product_price вместо product

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         order = self.object
#         items = order.items.all()

#         # Пагинация (без изменений)
#         if items.count() > 20:
#             paginator = Paginator(items, 10)
#             page_number = self.request.GET.get('page')
#             page_obj = paginator.get_page(page_number)
#             context['page_obj'] = page_obj
#             context['paginator'] = paginator
#             context['show_pagination'] = True

#             pages_to_show = 5
#             half = pages_to_show // 2
#             start_page = max(1, page_obj.number - half)
#             end_page = min(paginator.num_pages, page_obj.number + half)

#             if end_page - start_page < pages_to_show - 1:
#                 if start_page == 1:
#                     end_page = min(paginator.num_pages, start_page + pages_to_show - 1)
#                 elif end_page == paginator.num_pages:
#                     start_page = max(1, end_page - pages_to_show + 1)

#             context["page_range"] = range(start_page, end_page + 1)
#         else:
#             context['page_obj'] = items
#             context['show_pagination'] = False
#             context['page_range'] = []

#         context['breadcrumbs'] = [
#             {'name': 'Детали заказа', 'slug': f'/order_detail/{order.id}/'},
#         ]
#         return context




class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        # Оптимизировано: Добавлен prefetch для size (batch-загрузка всех размеров без N+1)
        return Order.objects.select_related('delivery_method', 'discount').prefetch_related(  # Добавлен discount, если используется
            'items__product_price__product',      # Для title, article_number
            'items__product_price__size'          # Для size.title (один запрос для всех)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object
        items = order.items.all()

        if items.count() > 20:
            paginator = Paginator(items, 10)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['page_obj'] = page_obj
            context['paginator'] = paginator
            context['show_pagination'] = True

            pages_to_show = 5
            half = pages_to_show // 2
            start_page = max(1, page_obj.number - half)
            end_page = min(paginator.num_pages, page_obj.number + half)

            if end_page - start_page < pages_to_show - 1:
                if start_page == 1:
                    end_page = min(paginator.num_pages, start_page + pages_to_show - 1)
                elif end_page == paginator.num_pages:
                    start_page = max(1, end_page - pages_to_show + 1)

            context["page_range"] = range(start_page, end_page + 1)
        else:
            context['page_obj'] = items
            context['show_pagination'] = False
            context['page_range'] = []

        # Дополнительно: total_cost (если не в модели)
        context['total_cost'] = order.get_total_cost() if hasattr(order, 'get_total_cost') else sum(item.get_cost() for item in items)

        context['breadcrumbs'] = [
            {'name': 'Детали заказа', 'slug': f'/order_detail/{order.id}/'},
        ]
        return context

class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password_change_form.html"

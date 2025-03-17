from .forms import LoginUserForm,RegisterUserForm,ProfileUserForm,UserPasswordChangeForm
from django.contrib.auth.views import LoginView,PasswordChangeView
from django.views.generic import CreateView,UpdateView,DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.contrib.auth import get_user_model
from orders.models import Order  # Импортируйте вашу модель заказов
from django.core.paginator import Paginator





class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title':'Авторизация'}

    # def get_success_url(self):
    #     return reverse_lazy('home:home')



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
        
        # Получаем заказы пользователя с использованием select_related и prefetch_related
        orders = Order.objects.filter(email=self.request.user.email) \
            .select_related('delivery_method') \
            .prefetch_related('items', 'items__product')
        
        # Пагинация
        paginator = Paginator(orders, 20)  # Разбиваем на страницы по 5 заказов
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['orders'] = page_obj  # Передаем только текущую страницу заказов
        
        return context

    def get_success_url(self):
        return reverse_lazy ('users:profile')

    def get_object(self, queryset=None):
        return self.request.user
    




class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order/order_detail.html'  # Укажите ваш шаблон для деталей заказа
    context_object_name = 'order'

    def get_queryset(self):
        # Используем select_related для оптимизации запросов
        return Order.objects.select_related('delivery_method').prefetch_related('items__product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем конкретный заказ
        order = self.object

        # Настройка хлебных крошек
        context['breadcrumbs'] = [
            {'name': 'Детали заказа', 'slug': f'/order_detail/{order.id}/'},
        ]

        return context





class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password_change_form.html"
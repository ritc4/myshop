from .forms import LoginUserForm,RegisterUserForm,ProfileUserForm,UserPasswordChangeForm
from django.contrib.auth.views import LoginView,PasswordChangeView
from django.views.generic import CreateView,UpdateView
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
        
        # Получаем заказы пользователя
        orders = Order.objects.filter(email=self.request.user.email)  # Измените на правильное поле, если нужно
        
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
    

class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password_change_form.html"
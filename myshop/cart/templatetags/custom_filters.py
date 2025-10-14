from django import template

register = template.Library()

@register.filter
def russian_pluralize(value, arg):
    """
    Аргумент arg должен быть строкой вида 'товар,товара,товаров'
    """
    args = arg.split(',')
    if len(args) != 3:
        return value  # Если аргумент неправильный, возвращаем как есть
    
    n = abs(int(value))
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} {args[0]}"  # 1 товар
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return f"{n} {args[1]}"  # 2-4 товара
    else:
        return f"{n} {args[2]}"  # 5+ товаров
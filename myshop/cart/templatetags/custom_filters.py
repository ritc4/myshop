from django import template

register = template.Library()

@register.filter
def pluralize(value, arg):
    value = int(value)
    forms = arg.split(',')
    if len(forms) != 3:
        return arg
    if value % 10 == 1 and value % 100 != 11:
        return f"{value} {forms[0].strip()}"
    elif 2 <= value % 10 <= 4 and not (12 <= value % 100 <= 14):
        return f"{value} {forms[1].strip()}"
    else:
        return f"{value} {forms[2].strip()}"
from django.core.management.base import BaseCommand
from home.tasks import import_csv_task  # Импорт задачи

class Command(BaseCommand):
    help = 'Отправка импорта продуктов из CSV в Celery'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        try:
            # Отправляем задачу в очередь Celery
            result = import_csv_task.delay(file_path)
            self.stdout.write(self.style.SUCCESS(f'Задача импорта отправлена в Celery. Task ID: {result.id}'))
            # Опционально: жди результата (но для больших импортов лучше не ждать)
            # self.stdout.write(self.style.SUCCESS(f'Результат: {result.get(timeout=300)}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка отправки задачи: {e}'))




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




# # рабочий парсер товаров очень, быстрый но не устанавливает первую фотографию товара а рандомна.
# from django.core.management.base import BaseCommand
# import csv
# from home.tasks import import_csv_batch_task  # Импорт задачи

# class Command(BaseCommand):
#     help = 'Импорт продуктов из CSV в Celery батчами с итоговыми результатами.'

#     def add_arguments(self, parser):
#         parser.add_argument('file_path', type=str)
#         parser.add_argument('--batch-size', type=int, default=100, help='Размер батча (по умолчанию 100)')

#     def handle(self, *args, **kwargs):
#         file_path = kwargs['file_path']
#         batch_size = kwargs.get('batch_size', 100)

#         try:
#             with open(file_path, 'r', encoding='windows-1251') as csvfile:
#                 reader = csv.DictReader(csvfile, delimiter=';')
#                 rows = list(reader)  # Для больших файлов замените ниже на потоковую обработку

#             total_rows = len(rows)
#             self.stdout.write(f"Всего строк: {total_rows}. Разделяем на батчи по {batch_size}.")

#             task_results = []

#             for i in range(0, total_rows, batch_size):
#                 batch_number = i // batch_size + 1
#                 start_num = i + 1  # Глобальный индекс старта
#                 batch = rows[i:i + batch_size]
#                 result = import_csv_batch_task.delay(batch, start_num)  # Теперь верно передаём
#                 task_results.append((batch_number, result.id, start_num, len(batch), result))
#                 self.stdout.write(f'Батч {batch_number} (строки {start_num}-{start_num + len(batch) - 1}) отправлен в Celery. Task ID: {result.id}')

#             self.stdout.write('Ожидание завершения всех задач...')

#             total_successful = 0
#             total_failed = 0
#             all_errors = []

#             for batch_number, task_id, start_num, batch_len, task_result in task_results:
#                 try:
#                     res = task_result.get(timeout=3600)
#                     total_successful += res['successful_imports']
#                     total_failed += res['failed_count']
#                     all_errors.extend(res['errors'])
#                 except Exception as task_e:
#                     self.stderr.write(f'Ошибка в задаче (батч {batch_number}, ID {task_id}): {task_e}')
#                     total_failed += batch_len  # Предполагаем, что весь батч неудачен

#             self.stdout.write(self.style.SUCCESS(
#                 f'\nИтоги импорта:\n'
#                 f'Всего обработано товаров: {total_successful + total_failed}\n'
#                 f'Успешно загружено: {total_successful}\n'
#                 f'Не загружено (ошибки): {total_failed}'
#             ))

#             if all_errors:
#                 self.stdout.write('\nСписок ошибок (с глобальными номерами строк):')
#                 for error in all_errors:
#                     self.stdout.write(f"Строка {error['row_num']}: {error['error']}")
#             else:
#                 self.stdout.write('\nОшибок не обнаружено.')

#         except Exception as e:
#             self.stderr.write(self.style.ERROR(f'Ошибка: {e}'))




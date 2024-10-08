from django.shortcuts import render
from .models import (TempTable, DictSecChapter, TempTableUNC, TempTableССКUNC, ExpensesToEpcMap, ExpensesToEpcMap, 
                     ObjectAnalog, InvestProject, Object, EpcCalculation, EpcCosts, SummaryEstimateCalculation,
                     ObjectCostEstimate, LocalCostEstimate, Expenses, ExpensesByEpc, TempTableLocal, LocalEstimateData, LocalEstimateDataSort
                    )
import pandas as pd
import re
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from collections import defaultdict
from collections import defaultdict, OrderedDict
from django.db import transaction
from django.db.models import Count, Q
from .forms import ObjectAnalogForm
import logging
import csv
import numpy as np
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
import difflib
import asyncio



logging.basicConfig(
    filename='debug.log',  # Имя файла, куда будут записываться логи
    level=logging.DEBUG,    # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s'  # Формат сообщений
)

# СТРАНИЦЫ HTML
# Стартовая страница
def start_page(request):

    all_records = TempTable.objects.all().order_by('chapter_id')
    all_record_unc = TempTableUNC.objects.all()
    # Группируем записи по главам
    grouped_records = {}
    for record in all_records:
        chapter_id = record.chapter_id.dict_sec_chapter_id
        if chapter_id not in grouped_records:
            grouped_records[chapter_id] = []
        grouped_records[chapter_id].append(record)

    context = {
        'grouped_records': grouped_records,
        'all_record_unc': all_record_unc,
    }
    return render(request, 'start.html', context)

# Страница связывания
def CCP_UNC_page(request):
    all_CCP_UNC = TempTableССКUNC.objects.all()

    # Получаем все записи из TempTable и TempTableUNC
    all_temp_records = TempTable.objects.all()
    all_temp_UNC_records = TempTableUNC.objects.all()

    # Группируем записи из TempTableССКUNC по главам
    grouped_records = defaultdict(list)
    for record in all_CCP_UNC:
        grouped_records[record.temp_table_id.chapter_id.dict_sec_chapter_id].append(
            record)

    # Сортировка по главам
    sorted_grouped_records = OrderedDict(sorted(grouped_records.items()))

    # Получаем все записи из TempTableССКUNC, чтобы исключить связанные позиции
    linked_temp_records_ids = TempTableССКUNC.objects.values_list(
        'temp_table_id', flat=True)
    linked_temp_UNC_records_ids = TempTableССКUNC.objects.values_list(
        'temp_table_unc_id', flat=True)

    # Фильтруем TempTable и TempTableUNC, чтобы оставить только несвязанные позиции
    unlinked_temp_records = all_temp_records.exclude(
        id__in=linked_temp_records_ids)
    unlinked_temp_UNC_records = all_temp_UNC_records.exclude(
        id__in=linked_temp_UNC_records_ids)

    # Группируем несвязанные TempTable записи по главам
    unlinked_grouped_records = defaultdict(list)
    for record in unlinked_temp_records:
        unlinked_grouped_records[record.chapter_id.dict_sec_chapter_id].append(
            record)

    # Сортировка по главам для несвязанных записей
    sorted_unlinked_grouped_records = OrderedDict(
        sorted(unlinked_grouped_records.items()))

    context = {
        'grouped_records': sorted_grouped_records,
        'unlinked_grouped_records': sorted_unlinked_grouped_records,
        'unlinked_temp_UNC_records': unlinked_temp_UNC_records,
    }

    return render(request, 'CCP_UNC.html', context)

# Страница ключевых слов
def dict_word_page(request):

    dict_word = ExpensesToEpcMap.objects.all().order_by('expenses_to_epc_map_id')
    # Группируем записи по главам
    context = {
        'dict_word': dict_word,
    }
    return render(request, 'dict_word_page.html', context)

# Объектs аналог
def object_analog(request):
    # Получаем список уникальных проектов с подсчетом количества строк для каждого проекта
    project_list = (
        ObjectAnalog.objects
        .values('project_id', 'project_name')
        .annotate(total_records=Count('id'))
        .annotate(num_records=Count('id'))
        .annotate(num_records_TX=Count('TX', filter=Q(TX__isnull=False) & ~Q(TX='')))
        .annotate(num_checked=Count('is_check', filter=Q(is_check=True)))
        .order_by('project_id')
    )

    context = {
        'project_list': project_list,
    }

    return render(request, 'object_anlog.html', context)

# Объектs аналог_2
def object_analog_2(request):
    # Получаем все проекты
    projects = InvestProject.objects.all()

    # Словарь для хранения данных о проектах
    project_data = []

    for project in projects:
        # Подсчитываем количество позиций в сметах для текущего проекта
        total_expenses = Expenses.objects.filter(summary_estimate_calculation__invest_project=project).count()

        # Подсчитываем количество связанных позиций
        related_positions = ExpensesByEpc.objects.filter(expense_id__summary_estimate_calculation__invest_project=project).distinct().count()

        # Подсчитываем количество проверенных позиций
        checked_positions_expenses = Expenses.objects.filter(summary_estimate_calculation__invest_project=project, is_check=True).distinct().count()

        # Подсчитываем количество проверенных позиций
        checked_positions_expensesbyepc = ExpensesByEpc.objects.filter(expense_id__summary_estimate_calculation__invest_project=project, is_check=True).distinct().count()

        # Подсчитываем количество отсортированых позиций
        checked_positions_sort = LocalEstimateDataSort.objects.filter(local_cost_estimate__summary_estimate_calculation__invest_project=project).distinct().count()

        # Добавляем данные в список
        project_data.append({
            'project': project,
            'num_records': total_expenses,
            'num_records_TX': related_positions,
            'num_checked': checked_positions_expenses,
            'num_checked_byepc': checked_positions_expensesbyepc,
            'num_checked_sort': checked_positions_sort,
        })

    context = {
        'projects': project_data,
    }

    return render(request, 'object_anlog_2.html', context)

# Содержание Объекта аналога
def object_analog_content(request, project_id):
    # Фильтрация строк по идентификатору проекта и сортировка по идентификатору главы
    all_object_analog = ObjectAnalog.objects.filter(project_id=project_id).order_by('chapter_id')
    
    context = {
        'all_object_analog': all_object_analog,
        'project_id': project_id
    }
    print(f' id {project_id}')

    return render(request, 'object_anlog_content.html', context)

# Содержание Объекта аналога
def object_analog_content_2(request, project_id):
    # Получаем объект проекта по project_id
    invest_project = get_object_or_404(InvestProject, pk=project_id)

    # Получаем все объекты, связанные с этим проектом
    objects = Object.objects.filter(invest_project=invest_project)

    # Получаем все сводные сметы расчета, связанные с объектами этого проекта
    summary_estimates = SummaryEstimateCalculation.objects.get(invest_project=invest_project)

    expense_ids_in_epc = ExpensesByEpc.objects.filter(epc_costs_id__object__in=objects
                    ).values_list('expense_id', flat=True).distinct()  

    filtered_expenses = Expenses.objects.filter(summary_estimate_calculation=summary_estimates).exclude(expense_id__in=expense_ids_in_epc
                    ).order_by('chapter_id__dict_sec_chapter_id').distinct()

    # Получаем ID всех EpcCosts, которые связаны с ExpensesByEpc
    epc_cost_ids_in_expenses = ExpensesByEpc.objects.values_list('epc_costs_id', flat=True)

    # Исключаем те EpcCosts, которые уже присутствуют в ExpensesByEpc
    epccosts_expenses = EpcCosts.objects.filter(object__in=objects).exclude(epc_costs_id__in=epc_cost_ids_in_expenses)

    # Получаем все затраты по EPC, связанные с этими сводными сметами расчета
    expenses_by_epc_items = ExpensesByEpc.objects.filter(epc_costs_id__object__in=objects
                                ).select_related('expense_id', 'epc_costs_id').order_by(
                                'expense_id__chapter_id__dict_sec_chapter_id', 
                                'expense_id__local_cost_estimate__local_cost_estimate_code'
                            )

    context = {
        'project_id': project_id,
        'invest_project': invest_project,
        'all_object_analog': expenses_by_epc_items,
        'filtered_expenses': filtered_expenses,
        'epccosts_expenses': epccosts_expenses,
    }
    
    return render(request, 'object_anlog_content_2.html', context)

# Содержание локальных смет Объекта аналога
def local_content_2(request, project_id):
    # Получаем объект проекта по project_id
    invest_project = get_object_or_404(InvestProject, pk=project_id)

    # Получаем все сводные сметы расчета, связанные с объектами этого проекта
    summary_estimates = SummaryEstimateCalculation.objects.get(invest_project=invest_project)  

    # Получаем все локальные сметы расчета, связанные с ССР
    local_estimates = LocalCostEstimate.objects.filter(summary_estimate_calculation=summary_estimates) 

    local_estimates_data = LocalEstimateData.objects.filter(local_cost_estimate__in=local_estimates)

    # Список идентификаторов локальных смет для передачи в шаблон
    local_estimate_ids = list(local_estimates_data.values_list('parsed_local_estimate_id', flat=True))

    context = {
        'project_id': project_id,
        'local_estimates_data': local_estimates_data,
        'local_estimate_ids': local_estimate_ids,
    }
    
    return render(request, 'local.html', context)

# Фильтрация смет
def async_filter_data(request):
    if request.method == 'POST':
        column_name = request.POST.get('column_name', None)  # Столбец
        keyword = request.POST.get('keyword', '')  # Ключевое слово
        estimate_ids = request.POST.getlist('estimate_ids[]', [])  # Идентификаторы локальных смет

        # Фильтруем данные только по переданным идентификаторам локальных смет
        local_estimates_data = LocalEstimateData.objects.filter(parsed_local_estimate_id__in=estimate_ids)
        
        filtered_data = []
        column_key = f"Unnamed: {column_name}"

        if keyword:
            # Пройдемся по всем данным
            for data in local_estimates_data:
                if column_name:
                    # Если указан столбец, ищем только в этом столбце
                    if column_key in data.row_data:
                        cell_value = str(data.row_data[column_key])                        
                        if re.search(keyword.lower(), cell_value.lower()):
                            print('Условие сработало с столбцом')
                            filtered_data.append({
                                'local_cost_estimate_code': data.local_cost_estimate.local_cost_estimate_code,
                                'row_number': data.row_number,
                                'row_data': data.row_data
                            })
                else:
                    # Если столбец не указан, ищем по всем столбцам (всему JSON)
                    for key, value in data.row_data.items():
                        cell_value = str(value)                        
                        if re.search(keyword.lower(), cell_value.lower()):
                            filtered_data.append({
                                'local_cost_estimate_code': data.local_cost_estimate.local_cost_estimate_code,
                                'row_number': data.row_number,
                                'row_data': data.row_data
                            })
                            break

        return JsonResponse({'data': filtered_data})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)



# ВСПОМОГАТЕЛЬНЫЕ УНКЦИИ
# Валидация кварталов
def format_quarter_info(quarter_str):
    # Паттерн для извлечения квартала и года с пересчетом
    pattern_with_base_year = r'\b(\d{4})\s*г(?:од|года)?\s*с\s*пересчетом\s*на\s*(\d+|IV|I|II|III|IV)\s*квартал\s*(\d{4})\s*г(?:од|года)?\b'
    match_with_base_year = re.search(
        pattern_with_base_year, quarter_str, re.IGNORECASE)

    if match_with_base_year:
        quarter = match_with_base_year.group(2)
        year = match_with_base_year.group(3)
        # Приведение к формату 'IV квартал 2018 г.'
        return f'{quarter} квартал {year} г.)'

    # Паттерн для извлечения квартала и года без пересчета
    pattern_without_base_year = r'(\d+|IV|I|II|III|IV)\s*квартал\s*(\d{4})\s*г(?:од|года)?'
    match_without_base_year = re.search(
        pattern_without_base_year, quarter_str, re.IGNORECASE)

    if match_without_base_year:
        quarter = match_without_base_year.group(1)
        year = match_without_base_year.group(2)
        # Приведение к формату 'IV квартал 2018 г.'
        return f'{quarter} квартал {year} г.'

    # Паттерн для извлечения квартала и года без пересчета
    pattern_without_base_year = r'(\d+|IV|I|II|III|IV)\s*кв.\s*(\d{4})\s*г(?:од|года)?'
    match_without_base_year = re.search(
        pattern_without_base_year, quarter_str, re.IGNORECASE)

    if match_without_base_year:
        quarter = match_without_base_year.group(1)
        year = match_without_base_year.group(2)
        # Приведение к формату 'IV квартал 2018 г.'
        return f'{quarter} квартал {year} г.'

    # Новый паттерн для строки: "1 кв 2019 года с НДС"
    pattern_simple_quarter = r'(\d+|IV|I|II|III|IV)\s*кв(?:квартал)?\s*(\d{4})\s*г(?:од|года)?'
    match_simple_quarter = re.search(
        pattern_simple_quarter, quarter_str, re.IGNORECASE)

    if match_simple_quarter:
        quarter = match_simple_quarter.group(1)
        year = match_simple_quarter.group(2)
        # Приведение к формату 'I квартал 2019 г.'
        return f'{quarter} квартал {year} г.'

    pattern = r'(\d{1,2})\s*(кв\w*|квартал)\s*(\d{4})\s*г(?:од|года)?|\b(\d{4})\s*г(?:од|года)?\s*с\s*пересчетом\s*в\s*текущие\s*цены\s*(\d{1,2}|IV|I|II|III|IV)\s*(квартал)\s*(\d{4})\s*г(?:од|года)?'
    match = re.search(pattern, quarter_str, re.IGNORECASE)

    if match:
        if match.group(1) and match.group(3):
            quarter = match.group(1)
            year = match.group(3)
            return f'{quarter} квартал {year} г.'
        elif match.group(5) and match.group(7):
            quarter = match.group(5)
            year = match.group(7)
            return f'{quarter} квартал {year} г.'

    return None

# Удаляем пробелы и заменяем запятую на точку
def clean_decimal_value(value):
    if isinstance(value, str):
        value = value.replace(' ', '').replace(',', '.')
    return value

# Убирает пробелы и приводит строку к нижнему регистру
def clean_string(s):
    return re.sub(r'\s+', '', s).lower()

# Очищаем имя объекта
def clean_object_name(name_object):
    return name_object.replace(" ", "").lower()

# Очищаем напряжение
def clean_voltage_string(voltage):
    # Удаляем все лишние символы, кроме цифр
    cleaned_voltage = ''.join(filter(str.isdigit, voltage))
    
    # Добавляем 'кВ', если это необходимо
    if cleaned_voltage:
        return f"{cleaned_voltage}кВ"
    else:
        return None  # Если строка оказалась пустой

# Функция для очистки строки ЛСР от лишних символов
def clean_and_normalize_string(value):
    # Удаляем переводы строки и лишние пробелы
    value = re.sub(r'\s+', '', value)
    # Приводим к нижнему регистру для корректного сравнения
    return value.lower()



# СПРАВОЧНИК КЛЮЧЕВЫХ СЛОВ
# Ввод нового ключевого слова
def add_expense_to_epc(request):
    if request.method == 'POST':
        expense_name = request.POST.get('expense_name')
        expense_epc = request.POST.get('expense_epc')
        expense_number = request.POST.get('expense_number')
        expense_voltage = request.POST.get('expense_voltage')
        expense_type = request.POST.get('expense_type')

        # Создаем и сохраняем новый объект
        new_expense = ExpensesToEpcMap(
            expenses_to_epc_map_name=expense_name, 
            expenses_to_epc_map_epc=expense_epc, 
            expenses_to_epc_number = expense_number,
            expenses_to_epc_voltage_marker = expense_voltage,
            expenses_to_epc_type = expense_type)
        new_expense.save()

        # Перенаправляем на ту же страницу или другую по вашему выбору
        return redirect('myapp:dict_word_page')

    return render(request, 'dict_word_page.html')  # Укажите ваш шаблон

# Редактирование ключевого слова
def edit_expense_to_epc(request, expense_id):
    try:
        expense_full = ExpensesToEpcMap.objects.all
        # Получаем ключевое слово по ID
        expense = ExpensesToEpcMap.objects.get(pk=expense_id)

    except ExpensesToEpcMap.DoesNotExist:
        # Если ключевое слово не найдено, возвращаем ошибку
        messages.error(request, "Ключевое слово не найдено.")
        return redirect('myapp:dict_word_page')    

    if request.method == 'POST':
        # Получаем данные из формы        
        expense_name = request.POST.get('expense_name')
        expense_epc = request.POST.get('expense_epc')
        expense_number = int(request.POST.get('expense_number'))
        expense_voltage = int(request.POST.get('expense_voltage'))
        expense_type = int(request.POST.get('expense_type'))

        # Обновляем объект ключевого слова
        expense.expenses_to_epc_map_name = expense_name
        expense.expenses_to_epc_map_epc = expense_epc
        expense.expenses_to_epc_number = expense_number
        expense.expenses_to_epc_voltage_marker = expense_voltage
        expense.expenses_to_epc_type = expense_type

        print(f"Полученные данные: {expense_name}, {expense_epc}, {expense_number}, {expense_voltage}, {expense_type}")
        print(f"Типы данных: {type(expense_name)}, {type(expense_epc)}, {type(expense_number)}, {type(expense_voltage)}, {type(expense_type)}")

        try:
            expense.save()
            messages.success(request, "Ключевое слово успешно обновлено.")

        except Exception as e:
            messages.error(request, f"Ошибка при сохранении ключевого слова: {e}")

        # Перенаправляем пользователя обратно на страницу списка ключевых слов или другую по вашему выбору
        return redirect('myapp:dict_word_page')

    # Передаем существующие данные ключевого слова в шаблон для отображения в форме
    context = {
        'expense': expense_full,
    }
    return render(request, 'dict_word_page.html', context)

# Удаление ключевого слова
def delete_expense_to_epc(request):
    if request.method == 'POST':
        expense_id = request.POST.get('expense_id')

        try:
            # Находим объект и удаляем его
            expense = ExpensesToEpcMap.objects.get(
                expenses_to_epc_map_id=expense_id)
            expense.delete()
        except ExpensesToEpcMap.DoesNotExist:
            return HttpResponse("Ключевое слово с таким ID не найдено", status=404)

        # Перенаправляем на ту же страницу или другую по вашему выбору
        return redirect('myapp:dict_word_page')

    return render(request, 'dict_word_page.html')  # Укажите ваш шаблон



# ПАРСИНГ
# Парсинг локалных смет
def parse_local_estimate_sheet(request, match_code, uploaded_file, temp_table_record):
    try:
        # Открываем файл Excel, получаем имена всех листов
        xls = pd.ExcelFile(uploaded_file)

        # Ищем вкладку, которая содержит идентификатор сметы match_code
        target_sheet_name = None
        for sheet_name in xls.sheet_names:
            if match_code in sheet_name:
                target_sheet_name = sheet_name
                break

        if not target_sheet_name:
            messages.error(request, f"Ошибка при парсинге локальной сметы. Вкладка с кодом {match_code} не найдена.")
            return

        # Чтение данных из найденной вкладки
        df = pd.read_excel(xls, sheet_name=target_sheet_name)

        # Заменяем NaN на None (null в JSON)
        df = df.replace({np.nan: None})

        # Проходим по строкам этой вкладки и сохраняем данные в TempTableLocal
        for index, row in df.iterrows():
            row_values = row.to_dict()  # Преобразуем строку в словарь

            # Записываем данные в TempTableLocal
            TempTableLocal.objects.create(
                temp_table=temp_table_record,
                row_number=index + 1,  # Номер строки
                row_data=row_values  # Данные строки в формате JSON
            )
        messages.success(request, f"Данные из вкладки '{target_sheet_name}' успешно сохранены в TempTableLocal.")
    
    except Exception as e:
        messages.error(request, f"Ошибка при парсинге локальной сметы {match_code}: {e}")

# Импорт CCR
def add_CCR(request):
    if request.method == 'POST' and request.FILES.get('CCR'):
        uploaded_file = request.FILES['CCR']

        try:
            # Шаг 1: Чтение Excel-файла в DataFrame
            df = pd.read_excel(uploaded_file, sheet_name=0, engine='openpyxl')
            rows_data = []  

            # Шаг 2: Проход по строкам DataFrame и запись данных в список
            for index, row in df.iterrows():
                row_values = row.tolist()
                rows_data.append({
                    'index': index,
                    'row_values': row_values
                })
                
            # Шаг 3: Обработка данных из списка
            current_chapter = None
            previous_chapter_instance = None
            quarter_row = None
            rows_to_insert = []
            additional_rows = []  # Новый список для строк между "Итого по главе" и новой главой
            target_column = None

            for data in rows_data:
                row_values = data['row_values']
                index = data['index']

                # Проверка на наличие главы
                for i in range(0, len(row_values)):
                    if isinstance(row_values[i], str):
                        match = re.search(r'\bГлава\s+(\d+)', row_values[i])
                        if match:
                            # Если найдена новая глава, сначала сохраняем строки предыдущей главы
                            if rows_to_insert:
                                for r in rows_to_insert:
                                    TempTable.objects.create(
                                        chapter_id=previous_chapter_instance,
                                        quarter=quarter_row,
                                        object_costEstimate_id=r['object_costEstimate_id'],
                                        local_costEstimate_id=r['local_costEstimate_id'],
                                        expenses_name=r['expenses_name'],
                                        construction_cost=clean_decimal_value(r['construction_cost']),
                                        installation_cost=clean_decimal_value(r['installation_cost']),
                                        equipment_cost=clean_decimal_value(r['equipment_cost']),
                                        other_cost=clean_decimal_value(r['other_cost']),
                                        total_cost=clean_decimal_value(r['total_cost'])
                                    )
                                rows_to_insert = []

                            # Сохраняем строки, которые были между "Итого по главе" и новой главой
                            if additional_rows:
                                for r in additional_rows:
                                    TempTable.objects.create(
                                        chapter_id=previous_chapter_instance,
                                        quarter=quarter_row,
                                        object_costEstimate_id=r['object_costEstimate_id'],
                                        local_costEstimate_id=r['local_costEstimate_id'],
                                        expenses_name=r['expenses_name'],
                                        construction_cost=clean_decimal_value(r['construction_cost']),
                                        installation_cost=clean_decimal_value(r['installation_cost']),
                                        equipment_cost=clean_decimal_value(r['equipment_cost']),
                                        other_cost=clean_decimal_value(r['other_cost']),
                                        total_cost=clean_decimal_value(r['total_cost'])
                                    )
                                additional_rows = []  # Очищаем список после сохранения

                            # Теперь обновляем текущую главу и chapter_instance
                            current_chapter = match.group(1)
                            try:
                                chapter_instance = DictSecChapter.objects.get(dict_sec_chapter_id=current_chapter)
                                previous_chapter_instance = chapter_instance  # Сохраняем для последующей записи
                                messages.success(request, f"Найден номер главы {current_chapter}")
                            except DictSecChapter.DoesNotExist:
                                messages.error(request, f"Глава с ID {current_chapter} не найдена в базе данных.")
                        continue

                # Проверка на квартал
                if quarter_row is None:  # Проверка, если quarter_row еще не найден
                    key_phrases_quarter = ["Составлен"]

                    # Пробуем найти квартал в каждой строке по отдельности
                    for i in range(0, len(row_values)):
                        if isinstance(row_values[i], str):
                            cleaned_value = re.sub(r'\s+', ' ', str(row_values[i]).strip().lower())
                            if any(re.search(phrase.lower(), cleaned_value) for phrase in key_phrases_quarter):
                                quarter_row = format_quarter_info(cleaned_value)
                                if quarter_row:
                                    messages.success(request, f"Найден квартал: {quarter_row}")
                                    break  # Если нашли квартал, выходим из цикла

                    # Если не нашли, объединяем все строки и ищем в объединенной строке
                    if quarter_row is None:
                        combined_str = " ".join([str(rv) for rv in row_values if isinstance(rv, str)]).strip()
                        quarter_row = format_quarter_info(combined_str)

                        if quarter_row is None:
                            messages.error(request, f"Не найден квартал!")
                        else:
                            messages.success(request, f"Найден квартал: {quarter_row}")

                # Проверка на финальную строку
                key_phrases = ["Итого по"]
                for i in range(0, len(row_values)):
                    if isinstance(row_values[i], str):
                        cleaned_value = re.sub(r'\s+', ' ', str(row_values[i]).strip().lower())
                        if any(re.search(phrase.lower(), cleaned_value) for phrase in key_phrases) and "главе" in cleaned_value:
                            target_column = cleaned_value
                            messages.success(request, f"Финальная строка найдена: {target_column}")
                            break

                if current_chapter is not None:   
                    try:
                        cost_estimate_id = row_values[1].replace(' ', '')                       
                                                
                        if re.search(r'\bОСР\b', cost_estimate_id) or re.search(r'^\d{2}-\d{2}$', cost_estimate_id) or re.search(r'^ОСР\d{2}-\d{2}$', cost_estimate_id):  
                            match = re.search(r'\b\d{2}-\d{2}\b', cost_estimate_id)                          
                            row_data = {
                                'chapter_id': current_chapter,
                                'object_costEstimate_id': match.group(0),
                                'local_costEstimate_id': None,
                                'expenses_name': row_values[2] if row_values[2] else None,
                                'construction_cost': row_values[3] if row_values[3] else None,
                                'installation_cost': row_values[4] if row_values[4] else None,
                                'equipment_cost': row_values[5] if row_values[5] else None,
                                'other_cost': row_values[6] if row_values[6] else None,
                                'total_cost': row_values[7] if row_values[7] else None,
                            }

                        elif re.search(r'\bЛСР\b', cost_estimate_id) or re.search(r'\bЛС\b', cost_estimate_id) or re.search(r'^\d{2}-\d{2}-\d{2}$', cost_estimate_id) or re.search(r'^ЛСР\d{2}-\d{2}-\d{2}$', cost_estimate_id):
                            match = re.search(r'\d{2}-\d{2}-\d{2}$', cost_estimate_id)     
                            row_data = {
                                'chapter_id': current_chapter,
                                'object_costEstimate_id': None,
                                'local_costEstimate_id': match.group(0),
                                'expenses_name': row_values[2] if row_values[2] else None,
                                'construction_cost': row_values[3] if row_values[3] else None,
                                'installation_cost': row_values[4] if row_values[4] else None,
                                'equipment_cost': row_values[5] if row_values[5] else None,
                                'other_cost': row_values[6] if row_values[6] else None,
                                'total_cost': row_values[7] if row_values[7] else None,
                            }

                            
                        else:
                            row_data = {
                                'chapter_id': current_chapter,
                                'object_costEstimate_id': None,  
                                'local_costEstimate_id': None,
                                'expenses_name': row_values[2] if row_values[2] else None,
                                'construction_cost': row_values[3] if row_values[3] else None,
                                'installation_cost': row_values[4] if row_values[4] else None,
                                'equipment_cost': row_values[5] if row_values[5] else None,
                                'other_cost': row_values[6] if row_values[6] else None,
                                'total_cost': row_values[7] if row_values[7] else None,
                            }

                        # Если строка найдена после "Итого по главе", добавляем ее в additional_rows
                        if target_column:
                            additional_rows.append(row_data)
                        else:
                            rows_to_insert.append(row_data)
                    except Exception as e:
                        messages.error(
                            request, f"Ошибка в строке {index}: {row} : {e}  ")

            # Сохранение данных после последней главы
            if rows_to_insert:
                for r in rows_to_insert:
                    temp_table_record = TempTable.objects.create(
                        chapter_id=previous_chapter_instance,
                        quarter=quarter_row,
                        object_costEstimate_id=r['object_costEstimate_id'],
                        local_costEstimate_id=r['local_costEstimate_id'],
                        expenses_name=r['expenses_name'],
                        construction_cost=clean_decimal_value(r['construction_cost']),
                        installation_cost=clean_decimal_value(r['installation_cost']),
                        equipment_cost=clean_decimal_value(r['equipment_cost']),
                        other_cost=clean_decimal_value(r['other_cost']),
                        total_cost=clean_decimal_value(r['total_cost'])
                    )

            # Сохранение строк, следующих после "Итого по главе" для последней главы
            if additional_rows:
                for r in additional_rows:
                    TempTable.objects.create(
                        chapter_id=previous_chapter_instance,
                        quarter=quarter_row,
                        object_costEstimate_id=r['object_costEstimate_id'],
                        local_costEstimate_id=r['local_costEstimate_id'],
                        expenses_name=r['expenses_name'],
                        construction_cost=clean_decimal_value(r['construction_cost']),
                        installation_cost=clean_decimal_value(r['installation_cost']),
                        equipment_cost=clean_decimal_value(r['equipment_cost']),
                        other_cost=clean_decimal_value(r['other_cost']),
                        total_cost=clean_decimal_value(r['total_cost'])
                    )

            # Второй этап: Проход по всем записям с локальными сметами и вызов парсинга
            local_estimates = TempTable.objects.filter(local_costEstimate_id__isnull=False)

            # Канал для отправки сообщений
            channel_layer = get_channel_layer()

            for estimate in local_estimates:
                try:
                    LCR = estimate.local_costEstimate_id
                    if channel_layer is None:
                        print(f"Ошибка: channel_layer не инициализирован {channel_layer}")

                    # Отправляем уведомление через WebSocket
                    async_to_sync(channel_layer.group_send)(
                        "notifications_group",  # имя группы
                        {
                            "type": "send_notification",
                            "message": f"Смета {LCR} распознается",
                        },
                    )
                    parse_local_estimate_sheet(request, LCR, uploaded_file, estimate)

                except Exception as e:
                    print(f'Ошибка при парсинге локальной сметы {LCR}: {e}')


            return redirect('myapp:start')

        except Exception as e:
            messages.error(request, f"Ошибка при обработке файла: в строке {index}  {e}")
            return redirect('myapp:start')
    else:
        messages.error(request, "Файл не загружен.")
        return redirect('myapp:start')

# Импорт UNC
def add_UNC(request):
    if request.method == 'POST' and request.FILES.get('UNC'):
        uploaded_file = request.FILES['UNC']

        # Чтение Excel-файла в DataFrame
        try:
            df = pd.read_excel(uploaded_file, sheet_name=0, engine='openpyxl')
        except Exception as e:
            messages.error(request, f"Ошибка при чтении файла: {e}")
            return redirect('myapp:start')

        rows_to_insert = []
        recording = False  # Переменная для начала записи
        row_type = None

        try:
            # Проход по строкам DataFrame и сохранение данных в базу
            for index, row in df.iterrows():

                if row_type is None:
                    if "Наименование УНЦ" in str(row.iloc[4]):
                        row_type = 1  # Тип №1
                    elif "Наименование УНЦ" in str(row.iloc[5]):
                        row_type = 2  # Тип №2
                    else:
                        messages.warning(request, f"Не удалось определить тип строки на строке {index + 1}")

                # Ожидаемая последовательность от 1 до 16
                expected_sequence = list(map(str, range(1, 8)))

                # Проверка на строку с нумерацией столбцов от 1 до 16
                if not recording:
                    if row.isnull().all():
                        continue  # Пропускаем пустые строки

                    actual_sequence = [str(cell).strip() for cell in row[:8] if pd.notna(cell)]
                    if actual_sequence == expected_sequence:
                        recording = True
                        messages.info(request, f"Начало записи данных с индекса строки: {index + 1}")
                        continue
                if row_type == 1:
                    if isinstance(row.iloc[4], str) and re.search(r'Итого', str(row.iloc[4]).strip(), re.IGNORECASE):
                        messages.info(request, f"Условие срабатывает для записи в базу на строке {index + 1}")

                        if rows_to_insert:
                            try:
                                for r in rows_to_insert:
                                    TempTableUNC.objects.create(
                                        project_id=r['project_id'],
                                        project_name=r['project_name'],
                                        name_unc=r['name_unc'],
                                        name_object=r['name_object'],
                                        voltage=r['voltage'],
                                        TX=r['TX'],
                                        count=r['count'],
                                        unit=r['unit'],
                                        unc_code=r['unc_code']
                                    )
                                messages.success(request, f"Данные успешно записаны в БД для {len(rows_to_insert)} строк.")
                                rows_to_insert = []  # Очищаем список после записи
                            except Exception as e:
                                messages.error(request, f"Ошибка при сохранении данных в БД на строке {index + 1}: {e}")
                        continue  # Переходим к следующей строке

                elif row_type == 2:
                    if isinstance(row.iloc[5], str) and re.search(r'Итого', str(row.iloc[5]).strip(), re.IGNORECASE):
                        messages.info(request, f"Условие срабатывает для записи в базу на строке {index + 1}")

                        if rows_to_insert:
                            try:
                                for r in rows_to_insert:
                                    TempTableUNC.objects.create(
                                        project_id=r['project_id'],
                                        project_name=r['project_name'],
                                        name_unc=r['name_unc'],
                                        name_object=r['name_object'],
                                        voltage=r['voltage'],
                                        TX=r['TX'],
                                        count=r['count'],
                                        unit=r['unit'],
                                        unc_code=r['unc_code']
                                    )
                                messages.success(request, f"Данные успешно записаны в БД для {len(rows_to_insert)} строк.")
                                rows_to_insert = []  # Очищаем список после записи
                            except Exception as e:
                                messages.error(request, f"Ошибка при сохранении данных в БД на строке {index + 1}: {e}")
                        continue  # Переходим к следующей строке

                if recording:
                    try:
                        if row_type == 1:
                            row_data = {
                                'project_id': row.iloc[3],  # id проекта
                                'project_name': row.iloc[2],  # имя проекта
                                'name_unc': row.iloc[4],  # Имя УНЦ
                                'name_object': row.iloc[5],  # Имя объекта
                                'voltage': row.iloc[9],  # Напряжение
                                # Техническая характеристика
                                'TX': row.iloc[10],
                                'count': row.iloc[15],  # количевство
                                'unit': row.iloc[16],  # еденица измерени
                                'unc_code': row.iloc[17],  # номер расценки
                            }
                        elif row_type == 2:
                            row_data = {
                                'project_id': row.iloc[3],  # id проекта
                                'project_name': row.iloc[2],  # имя проекта
                                'name_unc': row.iloc[5],  # Имя УНЦ
                                'name_object': row.iloc[6],  # Имя объекта
                                'voltage': row.iloc[10],  # Напряжение
                                # Техническая характеристика
                                'TX': row.iloc[11],
                                'count': row.iloc[18],  # количевство
                                'unit': row.iloc[19],  # еденица измерени
                                'unc_code': row.iloc[20],  # номер расценки
                            }

                        rows_to_insert.append(row_data)
                    except Exception as e:
                        messages.error(request, f"Ошибка при обработке строки {index + 1}: {e}")

        except Exception as e:
            messages.error(request, f"Общая ошибка на строке {index + 1}: {e}")
            return redirect('myapp:start')

        messages.success(request, "Данные успешно загружены в базу данных.")
        return redirect('myapp:start')
    else:
        messages.error(request, 'Файла нет или метод запроса не POST')
        return redirect('myapp:start')

# Очистка списка парсинга
def delete_temp(request):
    if request.method == 'POST':
        # Удаляем все записи из TempTable
        TempTable.objects.all().delete()

        # Удаляем все записи из TempTableUNC
        TempTableUNC.objects.all().delete()

        # Перенаправляем пользователя после удаления
        # Замените 'some_page' на нужный URL или название маршрута
        return redirect('myapp:start')
    else:
        # Замените 'some_page' на нужный URL или название маршрута
        return redirect('myapp:start')



# МИГРАЦИЯ
# Формирование проекта с ОА
@transaction.atomic
def migrate_data_to_main_tables(request):
    try:
        # Группировка данных по проектам из TempTable
        projects = TempTableUNC.objects.values('project_id', 'project_name').distinct()

        # Группировка объектов по полю name_object из TempTableUNC
        objects_data = TempTableUNC.objects.values('name_object').distinct()

        for project in projects:
            project_id = project['project_id']
            project_code = project['project_id']
            project_name = project['project_name']

            # Проверка, существует ли проект с таким project_code
            if InvestProject.objects.filter(invest_project_mrid=project_code).exists():
                # Если проект с таким кодом уже существует, выдаем уведомление и пропускаем его создание
                messages.error(request, f"Проект с кодом {project_code} уже существует. Создание дубликата невозможно.")
                return redirect('myapp:start')

            # Создание или обновление инвестиционного проекта
            invest_project, created = InvestProject.objects.get_or_create(
                invest_project_mrid=project_code,
                defaults={
                    'dict_project_type_id': None,
                    'dict_project_status_id': None,
                    'invest_project_type': None,
                    'invest_project_version': None,
                    'invest_project_unc_forecast': None,
                    'invest_project_create_dttm': None,
                    'invest_project_update_dttm': None,
                    'project_name': project_name,  # Устанавливаем имя проекта
                    'project_code': project_code,
                }
            )

            for obj_data in objects_data:
                name_object = obj_data['name_object']

                # Создание объекта
                obj, created = Object.objects.get_or_create(
                    invest_project=invest_project,
                    object_name=name_object,
                    defaults={
                        'object_type_id': None,
                        'dict_region_id': None,
                        'dict_work_type_id': None,
                        'dict_substaion_type_id': None,
                        'start_up_complex_id': None,
                        'dict_regions_economic_zone_id': None,
                        'object_mrid': None,
                        'object_is_analogue': None,
                        'object_create_dttm': None,
                        'object_update_dttm': None,
                    }
                )
                if created:
                    print(f"Создан новый объект: {obj}")
                else:
                    print(f"Объект уже существует: {obj}")

                # Создание записи в EpcCalculation
                epc_calculation = EpcCalculation.objects.create(
                    object=obj
                )

                # Создание записей в EpcCosts
                epc_costs_data = TempTableUNC.objects.filter(name_object=name_object)
                for epc_cost_data in epc_costs_data:
                    epc_cost = EpcCosts.objects.create(
                    object=obj,
                    epc_calculation=epc_calculation,
                    dict_cost_epc_id=epc_cost_data.unc_code,  # Обращаемся к полю через точку
                    dict_cost_epc_table_id=None,
                    name_unc=epc_cost_data.name_unc,  # Обращаемся к полю через точку
                    name_object=epc_cost_data.name_object,  # Обращаемся к полю через точку
                    voltage=epc_cost_data.voltage,  # Обращаемся к полю через точку
                    TX=epc_cost_data.TX,  # Обращаемся к полю через точку
                    count=epc_cost_data.count,  # Обращаемся к полю через точку
                    unit=epc_cost_data.unit  # Обращаемся к полю через точку
                    )

            # Обработка данных из TempTable
            temp_data = TempTable.objects.all()

            for data in temp_data:
                summary_estimate_calculation, created = SummaryEstimateCalculation.objects.get_or_create(
                    invest_project=invest_project,
                    defaults={
                        'sum_est_calc_mrid': None,
                        'sum_est_calc_before_ded': None,
                    }
                )

                # Создание записи в ObjectCostEstimate, если есть object_costEstimate_id
                object_cost_estimate = None
                if data.object_costEstimate_id:
                    object_cost_estimate = ObjectCostEstimate.objects.create(
                        summary_estimate_calculation=summary_estimate_calculation if summary_estimate_calculation else None,
                        object_cost_estimate_code=data.object_costEstimate_id
                    )

                # Создание записи в LocalCostEstimate, если есть local_costEstimate_id
                local_cost_estimate = None
                if data.local_costEstimate_id:

                    object_cost_estimate_prefix = '-'.join(data.local_costEstimate_id.split('-')[:2])

                    # Пытаемся найти соответствующую объектную смету по этому префиксу
                    linked_object_cost_estimate = ObjectCostEstimate.objects.filter(
                        object_cost_estimate_code=object_cost_estimate_prefix
                    ).first()

                    local_cost_estimate, created = LocalCostEstimate.objects.get_or_create(
                        object_cost_estimate=linked_object_cost_estimate if linked_object_cost_estimate else object_cost_estimate,
                        summary_estimate_calculation=summary_estimate_calculation if summary_estimate_calculation else None,
                        local_cost_estimate_code=data.local_costEstimate_id
                    )

                    # Теперь переносим данные из TempTableLocal в LocalEstimateData
                    temp_table_locals = TempTableLocal.objects.filter(temp_table=data).order_by('row_number')

                    for temp_table_local in temp_table_locals:
                                LocalEstimateData.objects.create(
                                    local_cost_estimate=local_cost_estimate,
                                    row_number=temp_table_local.row_number,
                                    row_data=temp_table_local.row_data
                                )
                    
                if pd.notna(data.expenses_name) and data.expenses_name not in ('', '0', 'nan'):
                    # Создание записи в Expenses
                    expense = Expenses.objects.create(
                        local_cost_estimate=local_cost_estimate if local_cost_estimate else None,
                        object_cost_estimate=object_cost_estimate if object_cost_estimate else None,
                        summary_estimate_calculation= summary_estimate_calculation if summary_estimate_calculation else None,
                        dict_expenditure_id=None,
                        expense_nme=data.expenses_name,
                        quarter=data.quarter,
                        construction_cost=data.construction_cost,
                        installation_cost=data.installation_cost,
                        equipment_cost=data.equipment_cost,
                        other_cost=data.other_cost,
                        total_cost=data.total_cost,
                        chapter_id=data.chapter_id
                    )
        messages.success(request, f"Проект с кодом {project_code} успешно сохранен!")
        return redirect('myapp:start')

    except Exception as e:
        messages.error(request, f"Ошибка при переносе: {e}")
        return redirect('myapp:start')



# ОБЪЕКТЫ АНАЛОГИ
# Удаление ОА
def delete_object_analog(request, project_id):
    try:
        # Удаляем все записи, связанные с данным проектом
        deleted_count, _ = ObjectAnalog.objects.filter(
            project_id=project_id).delete()

        # Сообщаем пользователю об успешном удалении
    except Exception as e:
        # Если произошла ошибка, сообщаем об этом пользователю
        messages.error(
            request, f"Ошибка при удалении записей для проекта с ID {project_id}: {e}")

    # Перенаправляем пользователя на страницу после выполнения операции
    messages.success(
        request, f"Успешно удалено {deleted_count} записей для проекта с ID {project_id}")
    # Укажите правильный URL-имя для редиректа
    return redirect('myapp:object_analog')

# Удаление ОА_2
def delete_object_analog_2(request, project_id):
    try:
        # Удаляем все записи, связанные с данным проектом
        deleted_count, _ = InvestProject.objects.filter(invest_project_id=project_id).delete()

        # Сообщаем пользователю об успешном удалении
    except Exception as e:
        # Если произошла ошибка, сообщаем об этом пользователю
        messages.error(request, f"Ошибка при удалении записей для проекта с ID {project_id}: {e}")

    # Перенаправляем пользователя на страницу после выполнения операции
    messages.success(request, f"Успешно удалено {deleted_count} записей для проекта с ID {project_id}")
    # Укажите правильный URL-имя для редиректа
    return redirect('myapp:object_analog_2')

# Сохранение всех строк ОА в связанных ССР
def save_all_object_analogs_CCR_UNC(request, project_id):

    if request.method == 'POST':
        all_expenses_by_epc = ExpensesByEpc.objects.filter(expense_id__summary_estimate_calculation__invest_project_id=project_id)

        for record in all_expenses_by_epc:
            # Проверяем наличие флага проверки
            is_checked = f'check_{record.expenses_by_epc_id}' in request.POST
            description = request.POST.get(f'description_{record.expenses_by_epc_id}', '')

            # Обновляем данные
            record.is_check = is_checked
            record.description = description
            record.save()

        messages.success(request, "Все изменения сохранены.")
        return redirect('myapp:object_analog_content_2', project_id=project_id)

# Сохранение всех строк ОА в связанных ССР_УНЦ
def save_all_object_analogs_CCR(request, project_id):

    if request.method == 'POST':
        all_expenses_by_epc = ExpensesByEpc.objects.filter(expense_id__summary_estimate_calculation__invest_project_id=project_id)

        for record in all_expenses_by_epc:
            # Проверяем наличие флага проверки
            is_checked = f'check_{record.expenses_by_epc_id}' in request.POST
            description = request.POST.get(f'description_{record.expenses_by_epc_id}', '')

            # Обновляем данные
            record.is_check = is_checked
            record.description = description
            record.save()

        messages.success(request, "Все изменения сохранены.")
        return redirect('myapp:object_analog_content_2', project_id=project_id)

# Сохранение всех строк ОА в связанных ССР
def save_all_object_analogs_CCR(request, project_id):
    if request.method == 'POST':
        # Обработка записей ExpensesByEpc
        all_expenses_by_epc = ExpensesByEpc.objects.filter(expense_id__summary_estimate_calculation__invest_project_id=project_id)

        for record in all_expenses_by_epc:
            # Проверяем наличие флага проверки
            is_checked = f'check_{record.expenses_by_epc_id}' in request.POST
            description = request.POST.get(f'description_{record.expenses_by_epc_id}', '')

            # Обновляем данные
            record.is_check = is_checked
            record.description = description
            record.save()

        # Обработка записей Expenses
        all_expenses = Expenses.objects.filter(summary_estimate_calculation__invest_project_id=project_id)

        for record in all_expenses:
            # Проверяем наличие флага проверки
            is_checked = f'check_{record.expense_id}' in request.POST
            description = request.POST.get(f'description_{record.expense_id}', '')

            # Обновляем данные
            record.is_check = is_checked
            record.description = description
            record.save()

        messages.success(request, "Все изменения сохранены.")
        return redirect('myapp:object_analog_content_2', project_id=project_id)



# СВЯЗЫВАНИЕ
# Связывание_3
def add_UNC_CCR_3(request, project):
    try:
        # Шаг 1: Загрузка всех ключевых слов из справочника
        key_phrases = ExpensesToEpcMap.objects.all()
    except Exception as e:
        messages.error(request, f"Ошибка при загрузке ключевых слов из справочника: {e}")
        return redirect('myapp:CCP_UNC_page')

    unc_keyword_map = {}
    unc_keyword_map_local = {}

    try:
        # Шаг 2: Проход по записям EpcCosts и определение ключевых слов
        epc_costs_records = EpcCosts.objects.filter(object__invest_project=project)
        
        for epc_cost_record in epc_costs_records:
            matching_keywords = []
            matching_keywords_local = []
            cleaned_name_unc = clean_string(epc_cost_record.name_unc)            
            cleaned_voltage = clean_voltage_string(epc_cost_record.voltage)
            name_object = clean_object_name(epc_cost_record.name_object)
            # Проверка наличия ключевой фразы в поле name_unc или voltage
            for key_phrase in key_phrases:
                cleaned_key_phrase = clean_string(key_phrase.expenses_to_epc_map_epc)

                if cleaned_key_phrase in cleaned_name_unc:
                    entry = (
                        clean_string(key_phrase.expenses_to_epc_map_name),
                        cleaned_key_phrase,
                        key_phrase,
                        cleaned_voltage,
                        name_object,
                        key_phrase.expenses_to_epc_voltage_marker,
                        key_phrase.expenses_to_epc_type
                    )

                    # Разделение в зависимости от expenses_to_epc_number
                    if key_phrase.expenses_to_epc_number == 1:
                        matching_keywords.append(entry)

                    elif key_phrase.expenses_to_epc_number == 2:
                        matching_keywords_local.append(entry)   
                    
            # Добавление в словари только если есть соответствующие данные
            if matching_keywords:
                unc_keyword_map[epc_cost_record] = matching_keywords

            if matching_keywords_local:
                unc_keyword_map_local[epc_cost_record] = matching_keywords_local           

    except Exception as e:
        messages.error(request, f"Ошибка при определении ключевых слов: {e}")
        return redirect('myapp:CCP_UNC_page')

    try:
        # Шаг 3: Проход по записям Expenses и поиск соответствий
        expenses_records = Expenses.objects.filter(summary_estimate_calculation__invest_project=project) 

        # Шаг 2: Обрабатываем каждую запись по отдельности
        for expense_record in expenses_records:
            process_expense_record(request, expense_record, unc_keyword_map, unc_keyword_map_local)

    except Exception as e:
        messages.error(request, f"Ошибка при связывании затрат: {e}")
        return redirect('myapp:CCP_UNC_page')

    return redirect('myapp:CCP_UNC_page')

# Связывание_3.Анализ позиций затрат по имени
def process_expense_record(request, expense_record, unc_keyword_map, unc_keyword_map_local):
        
    try:    
        # Пропускаем записи, у которых заполнено поле object_cost_estimate
        if expense_record.object_cost_estimate is not None:
            return

        local_match_found = False
        LCR = None
        local_records = []
        channel_layer = get_channel_layer()

        # Отдельно анализируем локальные сметы
        if expense_record.local_cost_estimate is not None:
            
            try:
                # Берем одну локальную смету
                local_cost_estimate = expense_record.local_cost_estimate
     
                # Проверка на None для local_cost_estimate
                if local_cost_estimate is None:
                    messages.error(request, f"Ошибка: у записи расхода {expense_record.expense_id} отсутствует local_cost_estimate.")
                    return

                print(f"local_cost_estimate {local_cost_estimate}")
                
                # Получаем все записи из LocalEstimateData, связанные с этой сметой
                local_records = LocalEstimateData.objects.filter(local_cost_estimate=local_cost_estimate)

                # Получаем все записи из LocalEstimateData, связанные с этой сметой
                local_records_sort = LocalEstimateDataSort.objects.filter(local_cost_estimate=local_cost_estimate)

                # Дополнительная проверка на None для каждого local_record
                valid_local_records = [record for record in local_records if record.local_cost_estimate is not None]

                if not valid_local_records:
                    return

                try:
                    # Преобразуем local_records в список для безопасного использования в async_to_sync
                    local_records_list = list(local_records)

                    local_records_sort_list = list(local_records_sort)
                    # Преобразуем unc_keyword_map_local в словарь/список для синхронного доступа
                    unc_keyword_map_local_items = list(unc_keyword_map_local.items())

                    print(f"unc_keyword_map_local_items: {unc_keyword_map_local_items}")

                    local_match_found = async_to_sync(process_local_estimates)(request, local_records_list, unc_keyword_map_local_items, expense_record, local_records_sort_list)
                    print(f"local_match_found: {local_match_found}")
                except Exception as e:
                    messages.error(request, f"Ошибка при вызове async_to_sync(process_local_estimates): {e}")
                    print(f"Ошибка при вызове async_to_sync(process_local_estimates): {e}")

                print(f"local_match_found {local_match_found}")

                LCR = expense_record.local_cost_estimate.local_cost_estimate_code   

                print(f"LCR {LCR}")

                if local_match_found:
                    # Отправляем уведомление через WebSocket
                    async_to_sync(channel_layer.group_send)(
                        "notifications_group",  # имя группы
                        {
                            "type": "send_notification",
                            "message": f"Смета {LCR} сопоставлена",
                        },
                    )
                else:
                    # Отправляем уведомление через WebSocket
                    async_to_sync(channel_layer.group_send)(
                        "notifications_group",  # имя группы
                        {
                            "type": "send_notification",
                            "message": f"Смета {LCR} отправлена на распознование по имени ЛСР",
                        },
                    )
            except Exception as e:
                messages.error(request, f"Ошибка при анализе локальных смет {LCR}: {e}")
                async_to_sync(channel_layer.group_send)(
                    "notifications_group",  # имя группы
                    {
                        "type": "send_notification",
                        "message": f"Ошибка при обработке локальной сметы {LCR}: {e}",
                    },
                )

        # Переходим к проверке ключевых слов
        cleaned_expenses_name = clean_string(expense_record.expense_nme)
        match_found = False  # Флаг для определения, найдено ли совпадение
        save_record = False

        # Проверяем расход по каждому ключевому слову
        for epc_cost_record, keywords in unc_keyword_map.items():
            for keyword, keyword_2, key_phrase_obj, cleaned_voltage, name_object, voltage_marker, type  in keywords:
                try:    
                    if keyword in cleaned_expenses_name:

                        voltage_found = (voltage_marker == 1) or (voltage_marker == 2 and cleaned_voltage in cleaned_expenses_name)
                        object_name_found = name_object in cleaned_expenses_name if name_object else False                                                     
                        messages.success(request, f'Связь по имен локальной сметы: Найдено ключевое слово "{keyword}" с напряжением  "{voltage_found}" Имя объекта {name_object}  - "{object_name_found}"')
                        
                        # Если найдено хотя бы одно совпадение
                        if voltage_found or object_name_found:
                            save_record = True
                        else:
                            save_record = False

                        if save_record:
                            # Проверка на наличие дубликатов
                            existing_record = ExpensesByEpc.objects.filter(
                                epc_costs_id=epc_cost_record,
                                expense_id=expense_record.expense_id,
                            ).exists()

                            if not existing_record:
                                try:
                                    # Создаем запись с совпадениями
                                    ExpensesByEpc.objects.create(
                                        epc_costs_id=epc_cost_record,
                                        expense_id=expense_record,
                                        dict_typical_epc_work_id=None,
                                        dict_budgeting_id=None,
                                        expenses_to_epc_map_id=key_phrase_obj,
                                        expenses_by_epc_nme=keyword,
                                    )                                    
                                    match_found = True  # Указываем, что совпадение найдено
                                    async_to_sync(channel_layer.group_send)(
                                        "notifications_group",  # имя группы
                                        {
                                            "type": "send_notification",
                                            "message": f"Затрату {cleaned_expenses_name} удалось связать",
                                        },
                                    )
                                except Exception as e:      
                                    messages.error(request, f"Ошибка при сохранении: {e}")
                except Exception as e:
                    messages.error(request, f"Ошибка при обработке ключевого слова '{keyword}': {e}")
                    async_to_sync(channel_layer.group_send)(
                        "notifications_group",  # имя группы
                        {
                            "type": "send_notification",
                            "message": f"Ошибка при обработке ключевого слова {keyword} для {cleaned_expenses_name}: {e}",
                        },
                    )

        if not match_found:
            async_to_sync(channel_layer.group_send)(
                "notifications_group",  # имя группы
                {
                    "type": "send_notification",
                    "message": f"Затрату  {cleaned_expenses_name} не удалось связать",
                },
            )
    except Exception as e:
        messages.error(request, f"Общая ошибка при обработке записи расхода {expense_record.expense_id}: {e}")
        async_to_sync(channel_layer.group_send)(
            "notifications_group",  # имя группы
            {
                "type": "send_notification",
                "message": f"Ошибка при обработке записи расхода {expense_record.expense_id}: {e}",
            },
        )

# Связывание_3.Анализ локальных смет
async def process_local_estimates(request, local_estimates, unc_keyword_map_local, expense_record, local_records_sort_list):

    try:
        match_found = False
        similarity_threshold = 0.42
        object_name_found = False
        save_record = False
        keyword_found = False
        voltage_found = False
        match = None
        local_record = None

        print(f"Начало обработки локальных смет local_estimates")

        # Извлекаем все существующие записи ExpensesByEpc для текущего expense_record и кэшируем их в памяти
        existing_expenses = await sync_to_async(list)(ExpensesByEpc.objects.filter(expense_id=expense_record).values_list('epc_costs_id', flat=True))
        existing_epc_ids = set(existing_expenses)

        try:
            # Проходим по каждой записи local_estimates для проверки объекта
            for local_record in local_estimates:
                # Извлекаем данные из local_estimates
                local_record_data = local_record.row_data

                # Проверяем по каждому ключевому слову, чтобы найти объект
                for epc_cost_record, keywords_info in unc_keyword_map_local:
                    for _, _, _, _, name_object, _, _ in keywords_info:
                        for key, value in local_record_data.items():
                            value_str = clean_and_normalize_string(str(value)).lower()

                            # Проверяем наличие имени объекта с использованием порога сходства
                            similarity = difflib.SequenceMatcher(None, name_object, value_str).ratio()

                            if similarity >= similarity_threshold:
                                object_name_found = True
                                break  # Если объект найден, прекращаем дальнейший поиск

                        if object_name_found:
                            break  # Прерываем поиск, если объект уже найден

                    if object_name_found:
                        break  # Прерываем цикл по keywords_info, если объект найден

                if object_name_found:
                    break  # Прерываем цикл по local_estimates, если объект найден

        except Exception as e:
            print(f"Ошибка при проверке объекта в локальных сметах: {e}")
            await sync_to_async(messages.error)(request, f"Ошибка при проверке объекта в локальных сметах: {e}")
           
        # Перебираем локальные сметы
        for sorted_record in local_records_sort_list:


            try:
                # Извлекаем данные из отсортированной записи
                data_code = sorted_record.local_estimate_data_code
                data_part = sorted_record.local_estimate_data_part
                data_name = sorted_record.local_estimate_data_name
                data_type = sorted_record.local_estimate_data_type
                data_type_code = int(sorted_record.local_estimate_data_type_code)

                # Ищем совпадение по каждому EpcCosts и ключевым словам
                for epc_cost_record, keywords_info in unc_keyword_map_local:

                    keyword_found = False
                    save_record = False
                    voltage_found = False

                    for keyword, cleaned_key_phrase, key_phrase_obj, cleaned_voltage, name_object, voltage_marker, key_type in keywords_info:                    

                        # Определяем, где искать ключевое слово, в зависимости от `data_type`
                        print(f" Определяем место поиска key_type: {key_type}, data_type_code: {data_type_code}, key_type == data_type_code: {key_type == data_type_code}")
                        if key_type == 1 and data_type_code == 1:                            
                            search_field = data_name
                        elif key_type == 2 and data_type_code == 2:
                            search_field = data_name
                        elif key_type == 3 and data_type_code == 3:
                            search_field = data_name
                        elif key_type == 4 and data_type_code == 4:
                            search_field = data_name
                        else:
                            print(f"Условие не сработало")
                            continue

                        save_record_messages = 'Не найдено'
                        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'

                        if search_field:

                            value_str = clean_and_normalize_string(str(search_field)).lower()                                            

                            # Проверяем наличие ключевого слова
                            if re.search(pattern, value_str):
                                keyword_found = True           
                                found_value_str = value_str
                                save_record = True
                                save_record_messages = 'затрате'

                        if not keyword_found and data_part:

                            value_str = clean_and_normalize_string(str(data_part)).lower()
                            print(f"Ищем в названии раздела {value_str}")
                            # Проверяем наличие ключевого слова
                            if re.search(pattern, value_str):
                                keyword_found = True           
                                found_value_str = value_str
                                save_record = True
                                save_record_messages = 'разделу'

                        # Проверяем voltage_marker
                        if voltage_marker == 1:
                            save_record = True

                        if voltage_marker == 2:
                            voltage_match = re.search(r'\d{1,3}(,\d{1})?кв', value_str, re.IGNORECASE)
                            range_voltage_match = re.search(r'(\d{1,3})(,\d{1})?\s*-\s*(\d{1,3})(,\d{1})?\s*кв', value_str, re.IGNORECASE)
                            
                            # Проверка на наличие фразы "до" перед напряжением
                            if "до" in value_str:
                                # Проверяем, что перед напряжением идет фраза "до" (например, "Кабель до 35 кВ")

                                range_match = re.search(r'до\s*(\d{1,3})(,\d{1})?\s*кв', value_str, re.IGNORECASE)
                                if range_match:
                                    voltage_found = True

                                    # Если найдено напряжение, проверяем, попадает ли оно в диапазон
                                    if voltage_match:
                                        found_voltage = float(voltage_match.group(0).replace('кв', '').replace(',', '.').strip())
                                        cleaned_voltage_normalized = float(re.sub(r'[^\d,]', '', cleaned_voltage).replace(',', '.'))
                                        
                                        if 0 <= cleaned_voltage_normalized <= found_voltage:
                                            save_record = True
                                        else:
                                            save_record = False
                                    else: 
                                        save_record = False # Явно указываем, что не сохраняем, если не найдено соответствие напряжения                          
                            
                            if range_voltage_match:
                                # Если найден диапазон напряжений, извлекаем минимальное и максимальное значения
                                min_voltage = float(range_voltage_match.group(1).replace(',', '.'))
                                max_voltage = float(range_voltage_match.group(3).replace(',', '.'))

                                cleaned_voltage_normalized = float(re.sub(r'[^\d,]', '', cleaned_voltage).replace(',', '.'))

                                # Проверяем, входит ли наше напряжение в диапазон
                                if min_voltage <= cleaned_voltage_normalized <= max_voltage:
                                    save_record = True
                                    save_record = True
                                else:
                                    save_record = False                            
                            
                            if voltage_match:
                                match = voltage_match.group(0).strip().lower()  # Убираем пробелы и приводим к нижнему регистру
                                cleaned_voltage_normalized = cleaned_voltage.strip().lower()  # Убираем пробелы и приводим к нижнему регистру
                                voltage_found = True

                                # Сравниваем напряжение с cleaned_voltage
                                if match == cleaned_voltage_normalized:
                                    save_record = True
                                else:
                                    save_record = False
                            else:
                                voltage_found = False
                                save_record = False 

                        # Если ключевое слово найдено и (напряжение или имя объекта) также найдены, создаем запись                
                        if keyword_found and (voltage_found or object_name_found or voltage_marker == 1):

                            if save_record and epc_cost_record not in existing_epc_ids:         
                                await sync_to_async(messages.success)(request, f"Связь по ЛСР: ключевое слово '{keyword}' в поиске по {save_record_messages} найдено в строке с затратой ЛСР '{found_value_str}', напряжение '{cleaned_voltage}' найдено {voltage_found}, объект '{name_object}' найден {object_name_found}")       
                                await create_expense_by_epc(request, epc_cost_record, expense_record, key_phrase_obj, keyword)
                                match_found = True
                                existing_epc_ids.add(epc_cost_record)
                            else:
                                await sync_to_async(messages.info)(request, f"Связь по ЛСР: ключевое слово '{keyword}' {save_record_messages} строке с затратой ЛСР '{found_value_str}'")
                                match_found = False

            except Exception as e:
                    print(f"Ошибка при обработке ключевых слов локальных смет для записи: {e}")
                    await sync_to_async(messages.error)(request, f"Ошибка при обработке ключевых слов локальных смет для записи: {e}")

    except Exception as e:
        print(f"Ошибка при обработке строки: {e}")
        await sync_to_async(messages.error)(request, f"Ошибка при обработке строки: {e}")
    
    print(f"Результат обработки локальных смет: {match_found}")
    return match_found

# Связывание_3. Асинхронное создание записи
async def create_expense_by_epc(request, epc_cost_record, expense_record, key_phrase_obj, keyword):

    # Проверяем, существует ли запись с заданным epc_costs_id и expense_id
    existing_record = await sync_to_async(ExpensesByEpc.objects.filter(
        epc_costs_id=epc_cost_record,
        expense_id=expense_record
    ).exists)()

    if not existing_record:
        # Создаём новую запись, если её не существует
        await sync_to_async(ExpensesByEpc.objects.create)(
            epc_costs_id=epc_cost_record,
            expense_id=expense_record,
            dict_typical_epc_work_id=None,
            dict_budgeting_id=None,
            expenses_to_epc_map_id=key_phrase_obj,
            expenses_by_epc_nme=keyword
        )
        await sync_to_async(messages.success)(request, f"Связь по ЛСР: ключевое слово {keyword}, ")

# Пересвязывание
def re_add_UNC_CCR_2(request, project_id):

    success_flag = True

    try:
        # Получаем объект проекта по project_id
        invest_project = get_object_or_404(InvestProject, pk=project_id)

        # Получаем все сводные сметы расчета, связанные с объектами этого проекта
        try:
            summary_estimates = SummaryEstimateCalculation.objects.get(invest_project=invest_project)
        except SummaryEstimateCalculation.DoesNotExist:
            summary_estimates = None

        if summary_estimates:
            # Получаем все расходы, связанные с данной сводной сметой
            filtered_expenses = Expenses.objects.filter(summary_estimate_calculation=summary_estimates)

            # Получаем идентификаторы всех записей расходов
            expense_ids = filtered_expenses.values_list('expense_id', flat=True)
            
            # Фильтруем связанные записи в ExpensesByEpc по идентификаторам расходов
            filtered_expenses_by_epc = ExpensesByEpc.objects.filter(expense_id__in=expense_ids)

            # Удаляем записи из ExpensesByEpc, связанные с удаленными расходами
            if filtered_expenses_by_epc.exists():
                num_deleted_by_epc, _ = filtered_expenses_by_epc.delete()
                try:
                    # Вызов функции связывания после миграции данных
                    add_UNC_CCR_3(request, invest_project)
                    messages.success(request, f"Удалено {num_deleted_by_epc} записей из ExpensesByEpc.")
                except Exception as e:
                    messages.error(request, f"Ошибка при вызове add_UNC_CCR_3: {e}")
                    success_flag = False  # Если произошла ошибка, сбрасываем флаг
            else:
                try:
                    # Вызов функции связывания после миграции данных
                    add_UNC_CCR_3(request, invest_project)
                    messages.warning(request, f"Не найдены записи о связаных позициях из ExpensesByEpc.")
                except Exception as e:
                    messages.error(request, f"Ошибка при вызове add_UNC_CCR_3: {e}")
                    success_flag = False  # Если произошла ошибка, сбрасываем флаг

    except Exception as e:
        messages.error(request, f"Ошибка при пересопоставлении: {e}")
        success_flag = False  

    # Сообщение об успешном завершении выводим только если не было ошибок
    if success_flag:
        messages.success(request, "Процесс пересопоставления успешно завершен. Объект аналог изменен")

    return redirect('myapp:object_analog_2')

# Сортироака локальных смет
def local_estimates_data_sort(request, project_id):
    current_section_name = None
    success_flag = True
    total_deleted = 0

    # Шаг 1: Выбор данных локальных смет по проекту и удаление ранее отсортированных данных
    try:
        summary_estimate = SummaryEstimateCalculation.objects.filter(invest_project=project_id)
        local_records = LocalCostEstimate.objects.filter(summary_estimate_calculation__in=summary_estimate)

        for local_record_delete in local_records:
            deleted_count, _ = LocalEstimateDataSort.objects.filter(local_cost_estimate=local_record_delete).delete()
            total_deleted += deleted_count
        
        messages.success(request, f"Удалено {total_deleted} отсортированных записей")

        # Шаг 2: сортировка данныхиз словаря local_records_data
        for local_record in local_records:
            local_records_data = LocalEstimateData.objects.filter(local_cost_estimate=local_record)
            
            for data in local_records_data:

                row_data = data.row_data

                if row_data:
                    # Проверяем наличие ключевой фразы "Раздел" в данных
                    section_code_name = None
                    for key, value in row_data.items():
                        if isinstance(value, str) and "Раздел" in value:
                            section_code_name  = value
                            break

                    # Если нашли новый раздел, сохраняем его как текущий
                    if section_code_name:
                        current_section_name = section_code_name 

                    # Определяем тип по ключевым словам в названии раздела
                    if current_section_name:
                        lower_section_name = current_section_name.lower()
                        if "оборудован" in lower_section_name:
                            estimate_type = "Оборудование"
                            estimate_type_code = 1
                        elif "работ" in lower_section_name or "монтаж" in lower_section_name:
                            estimate_type = "Работы"
                            estimate_type_code = 2
                        elif "материал" in lower_section_name:
                            estimate_type = "Материалы"
                            estimate_type_code = 3
                        else:
                            estimate_type = "Прочее"
                            estimate_type_code = 4

                        try:
                            data_name = row_data.get("Unnamed: 2")
                            if data_name and isinstance(data_name, str) and all(word not in data_name for word in ("Итого", "в т.ч.", "Всего", "ВСЕГО", "Должность", "в том числе")):
                                sorted_data = LocalEstimateDataSort(
                                    local_cost_estimate=local_record,
                                    local_estimate_data_code=row_data.get("Unnamed: 1"),
                                    local_estimate_data_part=current_section_name,
                                    local_estimate_data_name=row_data.get("Unnamed: 2"),
                                    local_estimate_data_type=estimate_type,
                                    local_estimate_data_type_code=estimate_type_code,
                                )
                                sorted_data.save()

                        except Exception as e:
                            messages.error(request, f"Ошибка при сохранении данных: {e}")
                            print( f"Ошибка при сохранении данных: {e}")
                            success_flag = False


    except Exception as e:
        messages.error(request, f"Ошибка при сортировки: {e}")
        success_flag = False  

    # Сообщение об успешном завершении выводим только если не было ошибок
    if success_flag:
        messages.success(request, "Процесс сортировки ЛСР успешно завершен.")

    return redirect('myapp:object_analog_2')





























# АРХИВ
# Связывание
def add_UNC_CCR(request):
    try:
        # Шаг 1: Загрузка всех ключевых слов из справочника
        key_phrases = ExpensesToEpcMap.objects.all()
    except Exception as e:
        messages.error(request, f"Ошибка при загрузке ключевых слов из справочника: {e}")
        return redirect('myapp:CCP_UNC_page')

    unc_keyword_map = {}
    try:
        # Шаг 2: Проход по записям TempTableUNC и определение ключевых слов
        for unc_record in TempTableUNC.objects.all():
            matching_keywords = []
            cleaned_name_unc = clean_string(unc_record.name_unc)
            for key_phrase in key_phrases:
                cleaned_key_phrase = clean_string(key_phrase.expenses_to_epc_map_epc)                
                if cleaned_key_phrase in cleaned_name_unc:             
                    matching_keywords.append((clean_string(key_phrase.expenses_to_epc_map_name), clean_string(key_phrase.expenses_to_epc_map_epc), key_phrase))

            if matching_keywords:
                unc_keyword_map[unc_record] = matching_keywords            

    except Exception as e:
        messages.error(request, f"Ошибка при определении ключевых слов: {e}")
        return redirect('myapp:CCP_UNC_page')
    
    try:
        # Шаг 3: Проход по записям TempTable и поиск соответствий
        for unc_record, keywords in unc_keyword_map.items():
            for keyword, keyword_2, key_phrase_obj in keywords:
                for temp_record in TempTable.objects.all():
                    if temp_record.object_costEstimate_id != '0':
                        continue

                    cleaned_expenses_name = clean_string(temp_record.expenses_name)             

                    if keyword in cleaned_expenses_name:
                        print(f"Найдено соответствие: {temp_record}")

                        # Проверка на наличие дубликатов
                        existing_record = TempTableССКUNC.objects.filter(
                            temp_table_id=temp_record,
                            temp_table_unc_id=unc_record,
                        ).exists()

                        # Шаг 4: Сохранение результата в TempTableССКUNC
                        if not existing_record:
                            TempTableССКUNC.objects.create(
                                temp_table_id=temp_record,
                                temp_table_unc_id=unc_record,
                                matched_keyword=keyword,
                                additional_info=f"ТХ: {keyword_2}",
                                key_id=key_phrase_obj,
                            )
    except Exception as e:
        messages.error(request, f"Ошибка при сохранении результатов: {e}")
        return redirect('myapp:CCP_UNC_page')

    messages.success(request, "Процесс сопоставления успешно завершен. Сохраните объект")
    return redirect('myapp:CCP_UNC_page')

# Связывание_2
def add_UNC_CCR_2(request, project):
    try:
        # Шаг 1: Загрузка всех ключевых слов из справочника
        key_phrases = ExpensesToEpcMap.objects.all()
    except Exception as e:
        messages.error(request, f"Ошибка при загрузке ключевых слов из справочника: {e}")
        return redirect('myapp:CCP_UNC_page')

    unc_keyword_map = {}
    try:
        # Шаг 2: Проход по записям EpcCosts и определение ключевых слов
        epc_costs_records = EpcCosts.objects.filter(object__invest_project=project)
        for epc_cost_record in epc_costs_records:
            matching_keywords = []
            cleaned_name_unc = clean_string(epc_cost_record.name_unc)            
            for key_phrase in key_phrases:
                cleaned_key_phrase = clean_string(key_phrase.expenses_to_epc_map_epc)
                if cleaned_key_phrase in cleaned_name_unc:                    
                    matching_keywords.append((clean_string(key_phrase.expenses_to_epc_map_name), cleaned_key_phrase, key_phrase))

            if matching_keywords:
                unc_keyword_map[epc_cost_record] = matching_keywords                

    except Exception as e:
        messages.error(request, f"Ошибка при определении ключевых слов: {e}")
        return redirect('myapp:CCP_UNC_page')

    try:
        # Шаг 3: Проход по записям Expenses и поиск соответствий
        expenses_records = Expenses.objects.filter(summary_estimate_calculation__invest_project=project)
        for epc_cost_record, keywords in unc_keyword_map.items():
            for keyword, keyword_2, key_phrase_obj in keywords:
                for expense_record in expenses_records:

                    # Пропускаем записи, у которых заполнено поле object_cost_estimate
                    if expense_record.object_cost_estimate is not None:
                        continue

                    cleaned_expenses_name = clean_string(expense_record.expense_nme)

                    if keyword in cleaned_expenses_name:

                        # Проверка на наличие дубликатов
                        existing_record = ExpensesByEpc.objects.filter(
                            epc_costs_id=epc_cost_record,
                            expense_id=expense_record.expense_id,
                        ).exists()

                        # Шаг 4: Сохранение результата в ExpensesByEpc
                        if not existing_record:
                            try:
                                ExpensesByEpc.objects.create(
                                    epc_costs_id=epc_cost_record,
                                    expense_id=expense_record,
                                    dict_typical_epc_work_id=None,
                                    dict_budgeting_id=None,
                                    expenses_to_epc_map_id=key_phrase_obj,
                                    expenses_by_epc_nme=keyword,
                                )

                            except Exception as e:
                                messages.error(request, f"Ошибка при сохранении: {e}")                            
    except Exception as e:
        messages.error(request, f"Ошибка при сохранении результатов: {e}")
        return redirect('myapp:CCP_UNC_page')

    messages.success(request, "Процесс сопоставления успешно завершен. Объект аналог сохранен")
    return redirect('myapp:CCP_UNC_page')

# Очистка списка связывания
def delete_CCR_UNC(request):
    if request.method == 'POST':
        # Удаляем все записи из TempTableССКUNC
        TempTableССКUNC.objects.all().delete()

        # Перенаправляем пользователя после удаления
        # Замените 'some_page' на нужный URL или название маршрута
        return redirect('myapp:CCP_UNC_page')
    else:
        # Замените 'some_page' на нужный URL или название маршрута
        return redirect('myapp:CCP_UNC_page')
    
# Сохранение объекта аналога
def add_object_analog(request):
    # Получаем все записи
    all_temp_records = TempTable.objects.all()
    all_CCP_UNC = TempTableССКUNC.objects.all()

    # Получаем все записи из TempTableССКUNC, чтобы исключить связанные позиции
    linked_temp_records_ids = TempTableССКUNC.objects.values_list('temp_table_id', flat=True)

    try:
        for linked_record in all_CCP_UNC:
            project_id_unc = linked_record.temp_table_unc_id.project_id
            if ObjectAnalog.objects.filter(project_id=project_id_unc).exists():
                messages.error(request, f"Данный проект {project_id_unc} уже есть в базе")
                return redirect('myapp:CCP_UNC_page')

        with transaction.atomic():  # Используем транзакцию для атомарности операции
            # Проходим по всем связанным позициям
            for linked_record in all_CCP_UNC:
                temp_table_record = linked_record.temp_table_id
                temp_table_unc_record = linked_record.temp_table_unc_id
                project_name_unc = temp_table_unc_record.project_name
                project_id_unc = temp_table_unc_record.project_id
                key_id = linked_record.key_id
                matched_keyword = linked_record.matched_keyword
                additional_info = linked_record.additional_info

                # Если проект не существует, продолжаем добавление
                if temp_table_record.expenses_name and temp_table_record.expenses_name.strip() and temp_table_record.expenses_name.lower() != 'nan':
                    # Создаем объект ObjectAnalog для каждой связанной позиции
                    ObjectAnalog.objects.create(
                        project_id=project_id_unc,
                        project_name=project_name_unc,
                        chapter_id=temp_table_record.chapter_id,
                        object_costEstimate_id=temp_table_record.object_costEstimate_id,
                        local_costEstimate_id=temp_table_record.local_costEstimate_id,
                        expenses_name=temp_table_record.expenses_name,
                        quarter=temp_table_record.quarter,
                        construction_cost=temp_table_record.construction_cost,
                        installation_cost=temp_table_record.installation_cost,
                        equipment_cost=temp_table_record.equipment_cost,
                        other_cost=temp_table_record.other_cost,
                        total_cost=temp_table_record.total_cost,
                        unc_code=temp_table_unc_record.unc_code,
                        name_unc=temp_table_unc_record.name_unc,
                        name_object=temp_table_unc_record.name_object,
                        voltage=temp_table_unc_record.voltage,
                        TX=temp_table_unc_record.TX,
                        count=temp_table_unc_record.count,
                        unit=temp_table_unc_record.unit,
                        matched_keyword=matched_keyword,
                        additional_info=additional_info,
                        key_id=key_id, 
                    )

            # Проходим по всем несвязанным позициям из TempTable, которые не имеют связей с TempTableUNC
            unlinked_temp_records = all_temp_records.exclude(
                id__in=linked_temp_records_ids)

            for unlinked_record in unlinked_temp_records:
                if unlinked_record.expenses_name and unlinked_record.expenses_name.strip() and unlinked_record.expenses_name.lower() != 'nan':
                    # Создаем объект ObjectAnalog только с данными из TempTable, без привязки к УНЦ
                    ObjectAnalog.objects.create(
                        project_id=project_id_unc,
                        # Здесь можно оставить пустым или заполнить, если есть данные
                        project_name=project_name_unc,
                        chapter_id=unlinked_record.chapter_id,
                        object_costEstimate_id=unlinked_record.object_costEstimate_id,
                        local_costEstimate_id=unlinked_record.local_costEstimate_id,
                        expenses_name=unlinked_record.expenses_name,
                        quarter=unlinked_record.quarter,
                        construction_cost=unlinked_record.construction_cost,
                        installation_cost=unlinked_record.installation_cost,
                        equipment_cost=unlinked_record.equipment_cost,
                        other_cost=unlinked_record.other_cost,
                        total_cost=unlinked_record.total_cost,
                        unc_code="",
                        name_unc="",
                        name_object="",
                        voltage="",
                        TX="",
                        count=None,
                        unit="",
                        matched_keyword="",
                        additional_info="",
                    )
                else:
                    print('Строка пустая')

        # Если операция завершена успешно, можно вернуть соответствующее сообщение
        messages.success(request, f"Объект аналог успешно сохранен")
        return redirect('myapp:CCP_UNC_page')

    except Exception as e:
        # Если произошла ошибка, транзакция будет откатана
        messages.error(request, f"Ошибка в сохранении объекта аналога {e}")
        return redirect('myapp:CCP_UNC_page')

# Сохранение всех строк ОА
def save_all_object_analogs(request, project_id):
    if request.method == 'POST':
        all_object_analog = ObjectAnalog.objects.filter(project_id=project_id)

        for record in all_object_analog:
            # Проверяем наличие флага проверки
            is_checked = f'is_check_{record.id}' in request.POST
            description = request.POST.get(f'description_{record.id}', '')

            # Обновляем данные
            record.is_check = is_checked
            record.description = description
            record.save()

        messages.success(request, "Все изменения сохранены.")
        return redirect('myapp:object_analog_content', project_id=project_id)


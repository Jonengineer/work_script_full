from django.shortcuts import render
from .models import (TempTable, DictSecChapter, TempTableUNC, TempTableССКUNC, ExpensesToEpcMap, ExpensesToEpcMap, 
                        InvestProject, Object, EpcCalculation, EpcCosts, SummaryEstimateCalculation, LocalEstimateDataSort_2,
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
import logging
import numpy as np
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
import difflib
import traceback
from django.db.models import Count, Q

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

    dict_word = ExpensesToEpcMap.objects.all().order_by('expenses_to_epc_map_epc')
    # Группируем записи по главам
    context = {
        'dict_word': dict_word,
    }
    return render(request, 'dict_word_page.html', context)

# # Объектs аналог_2
# def object_analog_2(request):
#     # Получаем все проекты
#     projects = InvestProject.objects.all().order_by('invest_project_id')

#     # Словарь для хранения данных о проектах
#     project_data = []

#     for project in projects:
#         # Подсчитываем количество позиций в сметах для текущего проекта
#         total_expenses = Expenses.objects.filter(summary_estimate_calculation_id__invest_project_id=project).count()

#         # Подсчитываем количество связанных позиций
#         related_positions = ExpensesByEpc.objects.filter(expense_id__summary_estimate_calculation_id__invest_project_id=project).distinct().count()

#         # Подсчитываем количество проверенных позиций
#         checked_positions_expenses = Expenses.objects.filter(summary_estimate_calculation_id__invest_project_id=project, expense_checked=True).distinct().count()

#         # Подсчитываем количество проверенных позиций
#         checked_positions_expensesbyepc = ExpensesByEpc.objects.filter(expense_id__summary_estimate_calculation_id__invest_project_id=project, expenses_by_epc_checked=True).distinct().count()

#         # Подсчитываем количество отсортированых позиций
#         checked_positions_sort = LocalEstimateDataSort.objects.filter(local_cost_estimate__summary_estimate_calculation_id__invest_project_id=project).distinct().count()

#         # # Подсчитываем количество отсортированых позиций
#         # checked_positions_sort_2 = LocalEstimateDataSort_2.objects.filter(local_cost_estimate__summary_estimate_calculation_id__invest_project_id=project).distinct().count()
        
#         # Добавляем данные в список
#         project_data.append({
#             'project': project,
#             'num_records': total_expenses,
#             'num_records_TX': related_positions,
#             'num_checked': checked_positions_expenses,
#             'num_checked_byepc': checked_positions_expensesbyepc,
#             'num_checked_sort': checked_positions_sort,
#             # 'num_checked_sort_2': checked_positions_sort_2,
#         })

#     context = {
#         'projects': project_data,
#     }

#     return render(request, 'object_anlog_2.html', context)

def object_analog_2(request):
    # Получаем все проекты
    projects = InvestProject.objects.all().order_by('invest_project_id')
    # Собираем IDs проектов
    project_ids = list(projects.values_list('invest_project_id', flat=True))
    # Получаем все расчеты
    summary_calculations = SummaryEstimateCalculation.objects.filter(invest_project_id__in=project_ids)
    # Собираем IDs расчетов
    summary_ids = list(summary_calculations.values_list('summary_estimate_calculation_id', flat=True))
    # Загружаем все нужные данные за один раз
    expenses_count = Expenses.objects.filter(summary_estimate_calculation_id__in=summary_ids).values(
        'summary_estimate_calculation_id'
    ).annotate(
        total_expenses=Count('expense_id'),
        checked_positions_expenses=Count('expense_id', filter=Q(expense_checked=True))
    )

    expenses_by_epc_count = ExpensesByEpc.objects.filter(expense_id__summary_estimate_calculation_id__in=summary_ids).values(
        'expense_id__summary_estimate_calculation_id'
    ).annotate(
        related_positions=Count('expenses_by_epc_id', distinct=True),
        checked_positions_expensesbyepc=Count('expenses_by_epc_id', filter=Q(expenses_by_epc_checked=True), distinct=True)
    )

    estimate_sort_count = LocalEstimateDataSort.objects.filter(local_cost_estimate__summary_estimate_calculation_id__in=summary_ids).values(
        'local_cost_estimate__summary_estimate_calculation_id'
    ).annotate(
        checked_positions_sort=Count('sort_local_estimate_id', distinct=True)
    )

    estimate_sort_2_count = LocalEstimateDataSort_2.objects.filter(local_cost_estimate__summary_estimate_calculation_id__in=summary_ids).values(
        'local_cost_estimate__summary_estimate_calculation_id'
    ).annotate(
        checked_positions_sort_2=Count('sort_local_estimate_id', distinct=True)
    )

    # Создаем словари для быстрого поиска
    expenses_count_dict = {x['summary_estimate_calculation_id']: x for x in expenses_count}
    expenses_by_epc_dict = {x['expense_id__summary_estimate_calculation_id']: x for x in expenses_by_epc_count}
    estimate_sort_dict = {x['local_cost_estimate__summary_estimate_calculation_id']: x for x in estimate_sort_count}
    estimate_sort_2_dict = {x['local_cost_estimate__summary_estimate_calculation_id']: x for x in estimate_sort_2_count}

    # Формируем список данных о проектах
    project_data = []
    for project in projects:
        summary_id = summary_calculations.filter(invest_project_id=project.invest_project_id).values_list('summary_estimate_calculation_id', flat=True).first()

        project_data.append({
            'project': project,
            'num_records': expenses_count_dict.get(summary_id, {}).get('total_expenses', 0),
            'num_records_TX': expenses_by_epc_dict.get(summary_id, {}).get('related_positions', 0),
            'num_checked': expenses_count_dict.get(summary_id, {}).get('checked_positions_expenses', 0),
            'num_checked_byepc': expenses_by_epc_dict.get(summary_id, {}).get('checked_positions_expensesbyepc', 0),
            'num_checked_sort': estimate_sort_dict.get(summary_id, {}).get('checked_positions_sort', 0),
            'num_checked_sort_2': estimate_sort_2_dict.get(summary_id, {}).get('checked_positions_sort_2', 0),
        })

    context = {'projects': project_data}
    return render(request, 'object_anlog_2.html', context)

# Содержание Объекта аналога
def object_analog_content_2(request, project_id):
    # Получаем объект проекта по project_id
    invest_project = get_object_or_404(InvestProject, pk=project_id)

    # Получаем все объекты, связанные с этим проектом
    objects = Object.objects.filter(invest_project=invest_project)

    # Получаем все сводные сметы расчета, связанные с объектами этого проекта
    summary_estimates = SummaryEstimateCalculation.objects.get(invest_project_id=invest_project)

    expense_ids_in_epc = ExpensesByEpc.objects.filter(epc_costs_id__object__in=objects).values_list('expense_id', flat=True).distinct()  

    filtered_expenses = Expenses.objects.filter(summary_estimate_calculation_id=summary_estimates).exclude(expense_id__in=expense_ids_in_epc
                    ).order_by('dict_sec_chapter_id__dict_sec_chapter_id').distinct()

    # Получаем ID всех EpcCosts, которые связаны с ExpensesByEpc
    epc_cost_ids_in_expenses = ExpensesByEpc.objects.values_list('epc_costs_id', flat=True)

    # Исключаем те EpcCosts, которые уже присутствуют в ExpensesByEpc
    epccosts_expenses = EpcCosts.objects.filter(object__in=objects).exclude(epc_costs_id__in=epc_cost_ids_in_expenses)

    # Получаем все затраты по EPC, связанные с этими сводными сметами расчета
    expenses_by_epc_items = ExpensesByEpc.objects.filter(epc_costs_id__object__in=objects
                            ).select_related('expense_id', 'epc_costs_id').order_by(
                            'expense_id__dict_sec_chapter_id', 
                            'expense_id__local_cost_estimate_id__local_cost_estimate_code'
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
    summary_estimates = SummaryEstimateCalculation.objects.get(invest_project_id=invest_project)  

    # Получаем все локальные сметы расчета, связанные с ССР
    local_estimates = LocalCostEstimate.objects.filter(summary_estimate_calculation_id=summary_estimates) 

    local_estimates_data = LocalEstimateData.objects.filter(local_cost_estimate_id__in=local_estimates)

    # Список идентификаторов локальных смет для передачи в шаблон
    local_estimate_ids = list(local_estimates_data.values_list('local_cost_estimate_id', flat=True))

    context = {
        'project_id': project_id,
        'local_estimates_data': local_estimates_data,
        'local_estimate_ids': local_estimate_ids,
    }
    
    return render(request, 'local.html', context)

# Фильтрация смет
def async_filter_data(request):
    if request.method == 'POST':
        try:
            column_name = request.POST.get('column_name', None)  # Столбец
            keyword = request.POST.get('keyword', '')  # Ключевое слово
            estimate_ids = request.POST.getlist('estimate_ids[]', [])  # Идентификаторы локальных смет

            # Проверка входных данных
            if not estimate_ids:                
                return JsonResponse({'error': 'Не переданы идентификаторы локальных смет'}, status=400)

            # Фильтруем данные только по переданным идентификаторам локальных смет
            local_estimates_data = LocalEstimateData.objects.filter(local_cost_estimate_id__in=estimate_ids)           

            filtered_data = []
            column_key = f"Unnamed: {column_name}"

            if keyword:
                # Пройдемся по всем данным
                for data in local_estimates_data:
                    if column_name:                       

                        # Если указан столбец, ищем только в этом столбце
                        if column_key in data.local_estimate_row_data:
                            cell_value = str(data.local_estimate_row_data[column_key])

                            if re.search(keyword.lower(), cell_value.lower()):
                                filtered_data.append({
                                    'local_cost_estimate_code': data.local_cost_estimate_id.local_cost_estimate_code,
                                    'row_number': data.local_estimate_data_rn,
                                    'row_data': data.local_estimate_row_data
                                })
                    else:
                        # Если столбец не указан, ищем по всем столбцам (всему JSON)
                        for key, value in data.local_estimate_row_data.items():
                            cell_value = str(value)
                            
                            if re.search(keyword.lower(), cell_value.lower()):
                                filtered_data.append({
                                    'local_cost_estimate_code': data.local_cost_estimate_id.local_cost_estimate_code,
                                    'row_number': data.local_estimate_data_rn,
                                    'row_data': data.local_estimate_row_data
                                })
                                break

            return JsonResponse({'data': filtered_data})

        except Exception as e:
            # Логируем любую ошибку
            return JsonResponse({'error': 'Произошла ошибка', 'details': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Неправильный метод запроса'}, status=400)


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

# Поиск напряжения
def check_voltage_match(voltage_marker, value_str, cleaned_voltage):
    voltage_found = False
    save_record = False

    # Если voltage_marker равен 2, выполняем поиск напряжения в строке
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
                
                return voltage_found, save_record
        
        # Если найден диапазон напряжений
        if range_voltage_match:
            min_voltage = float(range_voltage_match.group(1).replace(',', '.'))
            max_voltage = float(range_voltage_match.group(3).replace(',', '.'))

            cleaned_voltage_normalized = float(re.sub(r'[^\d,]', '', cleaned_voltage).replace(',', '.'))

            # Проверяем, входит ли наше напряжение в диапазон
            if min_voltage <= cleaned_voltage_normalized <= max_voltage:
                voltage_found = True
                save_record = True
            else:
                save_record = False

            return voltage_found, save_record
        
        # Проверка совпадения конкретного напряжения
        print(f"Поиск напряжения {voltage_match}")
        if voltage_match:
            found_voltage = float(re.sub(r'[^\d,]', '', voltage_match.group(0)).replace(',', '.').strip())
            cleaned_voltage_normalized = float(re.sub(r'[^\d,]', '', cleaned_voltage).replace(',', '.'))
            voltage_found = True
            print(f"Найденное напряжение: {found_voltage}, Переданное напряжение: {cleaned_voltage_normalized}")

            if found_voltage >= cleaned_voltage_normalized:
                save_record = True
            else:
                save_record = False

    return voltage_found, save_record

# Поиск объекта
def find_object_in_local_estimates(local_estimates, unc_keyword_map):
    try:        
        print(f"unc_keyword_map {unc_keyword_map}")        
        similarity_threshold = 0.2

        if isinstance(unc_keyword_map, dict):
            # Для поиска объекта в локальной смете
            for local_record in local_estimates:
                if hasattr(local_record, 'row_data') and local_record.row_data is not None:
                    try:
                        # Извлечение данных из 'row_data', если он существует
                        local_record_data = local_record.row_data

                        # Проход по каждому ключевому слову для поиска совпадений
                        for _, keywords_info in unc_keyword_map.items():
                            for _, _, _, _, name_object, _, _ in keywords_info:
                                # Проверка на наличие значения name_object
                                if not name_object:
                                    continue

                                # Поиск совпадений в данных локальной сметы
                                for key, value in local_record_data.items():
                                    value_str = clean_and_normalize_string(str(value)).lower()
                                    similarity = difflib.SequenceMatcher(None, name_object, value_str).ratio()

                                    if similarity >= similarity_threshold:
                                        print(f"name_object '{name_object}' found in 'local_estimates' with value '{value_str}' (similarity {similarity})")
                                        return True  # Объект найден
                    except Exception as e:
                        print(f"Ошибка при проверке local_record {local_record}: {e}")
                        print(traceback.format_exc())

                else:

                    # Если 'row_data' не существует, проверяем совпадение в 'expense_record' (предполагаем, что это строка)
                    if isinstance(local_estimates, list):    
                        try:           
                        
                            cleaned_estimate_name = clean_and_normalize_string(str(local_estimates)).lower()

                            for _, keywords_info in unc_keyword_map.items():
                                for _, _, _, _, name_object, _, _ in keywords_info:
                                    if not name_object:
                                        continue

                                    similarity = difflib.SequenceMatcher(None, name_object, cleaned_estimate_name).ratio()

                                    if similarity >= similarity_threshold:
                                        print(f"name_object '{name_object}' found in 'expense_record' with name '{cleaned_estimate_name}' (similarity {similarity})")
                                        return True  # Объект найден
                        except Exception as e:
                            print(f"Ошибка при проверке local_estimates {local_estimates}: {e}")
                            print(traceback.format_exc())

    except Exception as e:
            print(f"Общая ошибка в find_object_in_local_estimates: {e}")
            print(traceback.format_exc())

    return False  # Объект не найден

# Если значение является NaN или пустым, возвращаем 0
def clean_value(value):
    if pd.isna(value) or value in ('', 'nan'):
        return 0
    return value


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
            expenses_to_epc_map_nme=expense_name, 
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
        expense.expenses_to_epc_map_nme = expense_name
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
        index = None

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

            stop_words = [
                "Непредвиденные затраты",       
            ]

            for data in rows_data:
                row_values = data['row_values']
                index = data['index']

                # Нормализуем строку
                combined_row = clean_and_normalize_string(
                    " ".join([str(rv) for rv in row_values if isinstance(rv, str)])
                )

                # Проверяем наличие нормализованных стоп-слов
                if any(clean_and_normalize_string(stop_word) == combined_row for stop_word in stop_words):
                    messages.warning(request, f"Найдена строка с содержанием стоп-слов: {combined_row}. Обрабатываем строку и завершаем парсинг.")

                    # Сохраняем строки, которые были накоплены до этого
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
                                total_cost=clean_decimal_value(r['total_cost']),
                                total_name=r['total_name']
                            )
                        rows_to_insert = []  # Очищаем список после сохранения

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
                                total_cost=clean_decimal_value(r['total_cost']),
                                total_name=r['total_name']
                            )
                        additional_rows = []  # Очищаем список после сохранения

                    # Завершаем цикл
                    break

                # Проверка на наличие главы
                for i in range(0, len(row_values)):
                    if isinstance(row_values[i], str):
                        match = re.search(r'\bГлава\s+(\d+)', row_values[i], re.IGNORECASE)
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
                                        total_cost=clean_decimal_value(r['total_cost']),
                                        total_name=r['total_name']
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
                                        total_cost=clean_decimal_value(r['total_cost']),
                                        total_name=r['total_name']
                                    )
                                additional_rows = []  # Очищаем список после сохранения

                            # Теперь обновляем текущую главу и chapter_instance
                            current_chapter = int(match.group(1))
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

                            row_data = {
                                'chapter_id': current_chapter,
                                'object_costEstimate_id': None,
                                'local_costEstimate_id': None,
                                'expenses_name': row_values[2] if len(row_values) > 2 else None,
                                'construction_cost': clean_decimal_value(row_values[3]) if len(row_values) > 3 else None,
                                'installation_cost': clean_decimal_value(row_values[4]) if len(row_values) > 4 else None,
                                'equipment_cost': clean_decimal_value(row_values[5]) if len(row_values) > 5 else None,
                                'other_cost': clean_decimal_value(row_values[6]) if len(row_values) > 6 else None,
                                'total_cost': clean_decimal_value(row_values[7]) if len(row_values) > 7 else None,
                                'total_name': row_values[1] if len(row_values) > 1 else None,
                            }
                            additional_rows.append(row_data)
                            break

                if current_chapter is not None:   
                    try:
                        cost_estimate_id = row_values[1]

                        if isinstance(cost_estimate_id, str):  # Проверяем, что это строка
                            cost_estimate_id = cost_estimate_id.replace(' ', '')
                        else:
                            cost_estimate_id = str(cost_estimate_id).replace(' ', '')      

                        patterns_OSR = [
                            r'\bОСР\b',                          # Содержит "ОСР"
                            r'^\d{2}-\d{2}$',                    # Формат: xx-xx
                            r'^ОСР\d{2}-\d{2}$',                 # Формат: ОСРxx-xx
                            r'^ОСР\s\d{2}-\d{2}$',              # Формат: ОСР xx-xx (с пробелом)
                            r'^\d{1,2}\.\d{2}-\d{2}$',           # Формат: x.xx-xx
                            r'^\d{1,2}_\d{1,2}\.\d{2}-\d{2}$',   # Формат: x_x.xx-xx
                        ]
                        
                        patterns_LSR = [
                            r'\bЛСР\b',                            # Содержит "ЛСР"
                            r'\bЛС\b$',                            # Заканчивается на "ЛС"
                            r'^\d{2}-\d{2}-\d{2}$',                # Формат: xx-xx-xx
                            r'^ЛСР\d{2}-\d{2}-\d{2}$',             # Формат: ЛСРxx-xx-xx
                            r'^ЛСР\s\d{2}-\d{2}-\d{2}$'            # Формат: ЛСР xx-xx-xx (с пробелом)
                            r'^\d{1,2}\.\d{2}-\d{2}-\d{2}$',       # Формат: x.xx-xx-xx
                            r'^\d{1,2}_\d{1,2}\.\d{2}-\d{2}-\d{2}$' # Формат: x_x.xx-xx-xx
                        ]

                        patterns_total = [
                            "Итого по главе",
                            "Итого по главам"           
                        ]

                        if row_values[1]:
                            cost_estimate = clean_and_normalize_string(row_values[1])

                        if any(re.search(pattern, cost_estimate_id) for pattern in patterns_OSR):
                            print(f"Найдено  {cost_estimate_id} ")
                            match = re.search(r'\d{2}-\d{2}\b', cost_estimate_id)                      
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
                                'total_name': None,                                
                            }

                        elif any(re.search(pattern, cost_estimate_id) for pattern in patterns_LSR):
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
                                'total_name': None,
                            }

                        elif any(clean_and_normalize_string(pattern) in cost_estimate for pattern in patterns_total):
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
                                'total_name': row_values[1] if row_values[1] else None,
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
                                'total_name': None,           
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
                        total_cost=clean_decimal_value(r['total_cost']),
                        total_name=r['total_name']
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
                        total_cost=clean_decimal_value(r['total_cost']),
                        total_name=r['total_name']
                    )

                additional_rows = []

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
                    'dict_project_type_id': 1,
                    'dict_project_status_id': 1,
                    'invest_project_type': 1,
                    'invest_project_version': None,
                    'invest_project_unc_forecast': None,
                    'invest_project_create_dttm': None,
                    'invest_project_update_dttm': None,
                    'invest_project_fullname': project_name,  # Устанавливаем имя проекта
                    'invest_project_code': project_code,
                }
            )

            for obj_data in objects_data:
                name_object = obj_data['name_object']

                # Создание объекта
                obj, created = Object.objects.get_or_create(
                    invest_project=invest_project,
                    object_name=name_object,
                    defaults={
                        'object_type_id': 1,
                        'dict_region_id': None,
                        'dict_work_type_id': 1,
                        'dict_substaion_type_id': None,
                        'start_up_complex_id': None,
                        'dict_regions_economic_zone_id': None,
                        'object_mrid': 1,
                        'object_is_analogue': None,
                        'object_create_dttm': None,
                        'object_update_dttm': None,
                    }
                )

                # Создание записи в EpcCalculation
                epc_calculation = EpcCalculation.objects.create(
                    object_id=obj,
                    epc_calculation_mrid=1,
                    epc_calculation_before_ded=1
                )

                # Создание записей в EpcCosts
                epc_costs_data = TempTableUNC.objects.filter(name_object=name_object)
                for epc_cost_data in epc_costs_data:
                    epc_cost = EpcCosts.objects.create(                    
                    epc_calculation_ind=epc_calculation,                    
                    dict_cost_epc_id=None,  # Обращаемся к полю через точку
                    dict_cost_epc_table_id=None,
                    equipment_parameter_id=None,
                    epc_costs_id_name=epc_cost_data.name_unc,  # Обращаемся к полю через точку
                    object_id=obj.object_id,
                    name_object=epc_cost_data.name_object,  # Обращаемся к полю через точку
                    voltage=epc_cost_data.voltage,  # Обращаемся к полю через точку
                    TX=epc_cost_data.TX,  # Обращаемся к полю через точку
                    count=epc_cost_data.count,  # Обращаемся к полю через точку
                    unit=epc_cost_data.unit,  # Обращаемся к полю через точку
                    code=epc_cost_data.unc_code,
                    )

            # Обработка данных из TempTable
            temp_data = TempTable.objects.all()

            for data in temp_data:
                summary_estimate_calculation, created = SummaryEstimateCalculation.objects.get_or_create(
                    invest_project_id=invest_project,
                    defaults={
                        'sum_est_calc_mrid': 1,
                        'sum_est_calc_before_ded': 1,
                    }
                )

                # Создание записи в ObjectCostEstimate, если есть object_costEstimate_id
                object_cost_estimate = None
                if data.object_costEstimate_id:
                    object_cost_estimate = ObjectCostEstimate.objects.create(
                        summary_estimate_calculation_id=summary_estimate_calculation if summary_estimate_calculation else None,
                        object_cost_estimate_code=data.object_costEstimate_id
                    )

                # Создание записи в LocalCostEstimate, если есть local_costEstimate_id
                local_cost_estimate = None
                if data.local_costEstimate_id:

                    object_cost_estimates = ObjectCostEstimate.objects.filter(
                        summary_estimate_calculation_id=summary_estimate_calculation
                    )

                    object_cost_estimate_prefix = '-'.join(data.local_costEstimate_id.split('-')[:2])

                    # Пытаемся найти соответствующую объектную смету по этому префиксу
                    linked_object_cost_estimate = object_cost_estimates.filter(
                        object_cost_estimate_code=object_cost_estimate_prefix
                    ).first()

                    local_cost_estimate, created = LocalCostEstimate.objects.get_or_create(
                        object_cost_estimate_id=linked_object_cost_estimate if linked_object_cost_estimate else object_cost_estimate,
                        summary_estimate_calculation_id=summary_estimate_calculation if summary_estimate_calculation else None,
                        local_cost_estimate_code=data.local_costEstimate_id
                    )

                    # Теперь переносим данные из TempTableLocal в LocalEstimateData
                    temp_table_locals = TempTableLocal.objects.filter(temp_table=data).order_by('row_number')

                    for temp_table_local in temp_table_locals:
                                LocalEstimateData.objects.create(
                                    local_cost_estimate_id=local_cost_estimate,
                                    local_estimate_data_rn=temp_table_local.row_number,
                                    local_estimate_row_data=temp_table_local.row_data
                                )

                forbidden_words = ["подпись", "должность, подпись", "(должность, подпись, расшифровка)", 
                                    'Директор филиала АО "ЦИУС ЕЭС" - ЦИУС Юга', '(подпись)',  "(инициалы.фамилия)",
                                    "(подпись.Ф.И.О.)", "подпись(инициалы.фамилия)", "тыс.руб.", "/", "(подпись, Ф.И.О.)",
                                    "(наименование)", "()", "( )", "(  )", "(О.С.Тюрина)", "подпись (инициалы, фамилия)",
                                    ""]
                
                normalized_forbidden_words = [clean_and_normalize_string(word) for word in forbidden_words]
                                    
                if pd.notna(data.expenses_name) and data.expenses_name not in ('', '0', 'nan', ' ', '  ', '  ', '    ',):

                    # Приводим строку к нормализованному виду и разбиваем на слова
                    normalized_expenses_name = clean_and_normalize_string(data.expenses_name)
                    expenses_words = set(normalized_expenses_name.split())

                    # Проверяем, есть ли точное совпадение с запрещённым словом
                    # Ищем совпадение с запрещённым словом
                    matching_word = next((word for word in normalized_forbidden_words if word in expenses_words), None)  
                    
                    if matching_word:
                        messages.error(request, f"В строке {data} {data.expenses_name} обнаружено запрещённое слово '{matching_word}'. Строка не записана.")
                        continue                   

                    # Создание записи в Expenses
                    expense = Expenses.objects.create(
                        local_cost_estimate_id=local_cost_estimate if local_cost_estimate else None,
                        object_cost_estimate_id=object_cost_estimate if object_cost_estimate else None,
                        summary_estimate_calculation_id=summary_estimate_calculation if summary_estimate_calculation else None,
                        dict_expenditure_id=None,
                        dict_sec_chapter_id=data.chapter_id,
                        expense_value=1,
                        expense_nme=data.expenses_name,
                        expense_qarter=data.quarter,
                        expense_construction_cost=clean_value(data.construction_cost),  
                        expense_installation_cost=clean_value(data.installation_cost),  
                        expense_equipment_cost=clean_value(data.equipment_cost),        
                        expense_other_cost=clean_value(data.other_cost),                
                        expense_total=clean_value(data.total_cost), 
                        expense_total_name=clean_value(data.total_cost),         
                    )

        messages.success(request, f"Проект с кодом {project_code} успешно сохранен!")
        return redirect('myapp:start')

    except Exception as e:
        messages.error(request, f"Ошибка при переносе: {e}")
        return redirect('myapp:start')


# ОБЪЕКТЫ АНАЛОГИ
# Удаление ОА
def delete_object_analog_2(request, project_id):
    print(project_id)
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

# Сохранение всех строк ОА в связанных ССР_УНЦ
def save_all_object_analogs_CCR_UNC(request, project_id):

    if request.method == 'POST':
        try:
            all_expenses_by_epc = ExpensesByEpc.objects.filter(expense_id__summary_estimate_calculation_id__invest_project_id=project_id)

            for record in all_expenses_by_epc:
                # Проверяем наличие флага проверки
                expenses_by_epc_checked = f'check_{record.expenses_by_epc_id}' in request.POST
                expenses_by_epc_descr = request.POST.get(f'description_{record.expenses_by_epc_id}', '')

                print(f"Record ID: {record.expenses_by_epc_id}, Checked: {expenses_by_epc_checked}, Description: {expenses_by_epc_descr}")

                # Обновляем данные
                record.expenses_by_epc_checked = expenses_by_epc_checked
                record.expenses_by_epc_descr = expenses_by_epc_descr
                try:
                    record.save()
                    print(f"Record {record.expenses_by_epc_id} saved successfully.")
                except Exception as e:
                    print(f"Error saving record {record.expenses_by_epc_id}: {e}")

        except Exception as e:
            print(f"Error saving record {record.expenses_by_epc_id}: {e}")

        messages.success(request, "Все изменения сохранены.")
        return redirect('myapp:object_analog_content_2', project_id=project_id)

# Сохранение всех строк ОА в связанных ССР
def save_all_object_analogs_CCR(request, project_id):
    if request.method == 'POST':
        # Получаем все записи Expenses, связанные с проектом
        all_expenses = Expenses.objects.filter(summary_estimate_calculation_id__invest_project_id=project_id)

        for record in all_expenses:
            # Проверяем наличие флага проверки
            is_checked = f'check_{record.expense_id}' in request.POST
            description = request.POST.get(f'description_{record.expense_id}', '')

            # Обновляем данные
            record.expense_checked = is_checked  # обновляем поле проверки
            record.expense_description = description  # обновляем описание
            record.save()  # сохраняем изменения в БД

        # Выводим сообщение об успешном сохранении
        messages.success(request, "Все изменения сохранены.")
        return redirect('myapp:object_analog_content_2', project_id=project_id)

# Сохранение всех строк ОА в связанных УНЦ
def save_all_object_analogs_UNC(request, project_id):
    if request.method == 'POST':
        # Получаем проект
        invest_project = get_object_or_404(InvestProject, pk=project_id)

        # Получаем все объекты, связанные с этим проектом
        objects = Object.objects.filter(invest_project=invest_project)

        # Получаем ID всех EpcCosts, которые уже присутствуют в ExpensesByEpc
        epc_cost_ids_in_expenses = ExpensesByEpc.objects.values_list('epc_costs_id', flat=True)

        # Исключаем те EpcCosts, которые уже присутствуют в ExpensesByEpc
        epccosts_expenses = EpcCosts.objects.filter(object__in=objects).exclude(epc_costs_id__in=epc_cost_ids_in_expenses)

        for epc in epccosts_expenses:
            # Проверяем наличие флага проверки и описания для каждого EpcCost
            epc_checked = f'check_epc_{epc.epc_costs_id}' in request.POST
            epc_description = request.POST.get(f'description_epc_{epc.epc_costs_id}', '')

            # Обновляем данные для EpcCosts
            epc.epc_costs_checked = epc_checked
            epc.epc_costs_description = epc_description

            # Пытаемся сохранить изменения
            try:
                epc.save()
                print(f"Затраты УНЦ ID {epc.epc_costs_id} успешно сохранены.")
            except Exception as e:
                print(f"Ошибка при сохранении затрат УНЦ ID {epc.epc_costs_id}: {e}")

        # Выводим сообщение об успешном сохранении
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
            cleaned_name_unc = clean_string(epc_cost_record.epc_costs_id_name)            
            cleaned_voltage = clean_voltage_string(epc_cost_record.voltage)
            name_object = clean_object_name(epc_cost_record.name_object)
            # Проверка наличия ключевой фразы в поле name_unc или voltage
            for key_phrase in key_phrases:
                cleaned_key_phrase = clean_string(key_phrase.expenses_to_epc_map_epc)

                if cleaned_key_phrase in cleaned_name_unc:
                    entry = (
                        clean_string(key_phrase.expenses_to_epc_map_nme),
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
        expenses_records = Expenses.objects.filter(summary_estimate_calculation_id__invest_project_id=project) 

        # Обрабатываем каждую запись по отдельности
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
        if expense_record.object_cost_estimate_id is not None:
            return

        local_match_found = False
        LCR = None
        local_records = []
        channel_layer = get_channel_layer()

        # Отдельно анализируем локальные сметы
        if expense_record.local_cost_estimate_id is not None:
            
            try:

                LCR = expense_record.local_cost_estimate_id.local_cost_estimate_code 

                # Берем одну локальную смету
                local_cost_estimate = expense_record.local_cost_estimate_id
                
                # Проверка на None для local_cost_estimate
                if local_cost_estimate is None:
                    messages.error(request, f"Ошибка: у записи расхода {expense_record.expense_id} отсутствует local_cost_estimate.")
                    return
                
                LCR = expense_record.local_cost_estimate_id.local_cost_estimate_code  
                
                # Получаем все записи из LocalEstimateData, связанные с этой сметой
                local_records = LocalEstimateData.objects.filter(local_cost_estimate_id=local_cost_estimate)

                # Получаем все записи из LocalEstimateDataSort, связанные с этой сметой
                local_records_sort = LocalEstimateDataSort.objects.filter(local_cost_estimate=local_cost_estimate)

                # Дополнительная проверка на None для каждого local_record
                valid_local_records = [record for record in local_records if record.local_cost_estimate_id is not None]

                if not valid_local_records:
                    return

                try:
                    # Преобразуем local_records в список для безопасного использования в async_to_sync
                    local_records_list = list(local_records)
                    local_records_sort_list = list(local_records_sort)

                    # Преобразуем unc_keyword_map_local в словарь/список для синхронного доступа
                    unc_keyword_map_local_items = list(unc_keyword_map_local.items())
                    local_match_found = async_to_sync(process_local_estimates)(request, local_records_list, unc_keyword_map_local_items, expense_record, local_records_sort_list)

                except Exception as e:
                    messages.error(request, f"Ошибка при вызове async_to_sync(process_local_estimates): {e}")

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

                        if voltage_marker == 1:
                            voltage_found = True

                        if voltage_marker == 2:
                            voltage_found, save_record = check_voltage_match(voltage_marker, cleaned_expenses_name, cleaned_voltage)
                        
                        object_name_found = False
                        if name_object:
                            object_name_found = find_object_in_local_estimates([cleaned_expenses_name], unc_keyword_map)
                                                                
                        messages.success(request,
                                        f'Связь по имен локальной сметы: Найдено ключевое слово "{keyword}" в строке {cleaned_expenses_name} '
                                        f'с напряжением "{voltage_found}" Имя объекта {name_object} - "{object_name_found}"'
                                    )    
                        
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
                                        expenses_by_epc_cost = 1
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
                    messages.error(request, f"Ошибка при обработке ключевого слова в имени ЛСР '{keyword}': {e}")
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
        object_name_found = False
        save_record = False
        keyword_found = False
        voltage_found = False

        # Извлекаем все существующие записи ExpensesByEpc для текущего expense_record и кэшируем их в памяти
        existing_expenses = await sync_to_async(list)(ExpensesByEpc.objects.filter(expense_id=expense_record).values_list('epc_costs_id', flat=True))
        existing_epc_ids = set(existing_expenses)

        try:
            # Проходим по каждой записи local_estimates для проверки объекта            
            if not object_name_found:
                print(f"Проверка объекта")
                object_name_found = await sync_to_async(find_object_in_local_estimates)(local_estimates, unc_keyword_map_local)
                await sync_to_async(messages.info)(request, f"Объект найден: {object_name_found}")
        except Exception as e:
            await sync_to_async(messages.error)(request, f"Ошибка при проверке объекта в локальных сметах: {e}")
        
        # Перебираем локальные сметы
        print(f"Перебираем локальные сметы")
        for sorted_record in local_records_sort_list:

            try:
                # Извлекаем данные из отсортированной записи
                data_part = sorted_record.local_estimate_data_part
                data_name = sorted_record.local_estimate_data_name
                data_type_code = int(sorted_record.local_estimate_data_type_code)

                # Ищем совпадение по каждому EpcCosts и ключевым словам
                for epc_cost_record, keywords_info in unc_keyword_map_local:

                    keyword_found = False
                    save_record = False
                    voltage_found = False

                    for keyword, cleaned_key_phrase, key_phrase_obj, cleaned_voltage, name_object, voltage_marker, key_type in keywords_info:                    

                        # Определяем, где искать ключевое слово, в зависимости от `data_type`
                        if key_type == 1 and data_type_code == 1:                            
                            search_field = data_name
                        elif key_type == 2 and data_type_code == 2:
                            search_field = data_name
                        elif key_type == 3 and data_type_code == 3:
                            search_field = data_name
                        elif key_type == 4 and data_type_code == 4:
                            search_field = data_name
                        else:
                            continue

                        save_record_messages = 'Не найдено'
                        pattern = re.escape(keyword.lower())

                        if search_field:                            
                            value_str = clean_and_normalize_string(str(search_field)).lower()           
                            print(f"Проверяем наличие ключевого {pattern} слова в {value_str}")                          

                            # Проверяем наличие ключевого слова
                            if re.search(pattern, value_str):
                                keyword_found = True           
                                found_value_str = value_str
                                save_record = True
                                save_record_messages = 'затрате'

                        if not keyword_found and data_part:
                            value_str = clean_and_normalize_string(str(data_part)).lower()

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
                            print(f"Ищем напряженеи: {cleaned_voltage}")
                            voltage_found, save_record = await sync_to_async(check_voltage_match)(voltage_marker, value_str, cleaned_voltage)

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
                    await sync_to_async(messages.error)(request, f"Ошибка при обработке ключевых слов локальных смет для записи: {e}")
                    print(traceback.format_exc())

    except Exception as e:
        await sync_to_async(messages.error)(request, f"Ошибка при обработке строки: {e}")
        print(traceback.format_exc())
    
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
            expenses_by_epc_nme=keyword,
            expenses_by_epc_cost = 1
        )
        await sync_to_async(messages.success)(request, f"Связь по ЛСР: ключевое слово {keyword}, ")

# Пересвязывание
def re_add_UNC_CCR_2(request, project_id):
    try:
        success_flag = True
        # Получаем объект проекта по project_id
        invest_project = get_object_or_404(InvestProject, pk=project_id)

        # Получаем все сводные сметы расчета, связанные с объектами этого проекта
        try:
            summary_estimates = SummaryEstimateCalculation.objects.get(invest_project_id=invest_project)
        except SummaryEstimateCalculation.DoesNotExist:
            summary_estimates = None

        if summary_estimates:
            # Получаем все расходы, связанные с данной сводной сметой
            filtered_expenses = Expenses.objects.filter(summary_estimate_calculation_id=summary_estimates)

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

# Поиск нужных столбцов для сортировки
def find_required_columns(row_data, found_columns=None, log_file_path="search_attempts.log"):
    # Словари для определения столбцов
    column_name_variations = {
        "Обоснование": ["Обоснование", "Обоснование сметы", "Основание", "Основание расчета", "Обоснование стоимости", "Шифр норматива", "Шифр и номер позиции норматива", "Обоснование расценок", "Обосно-вание", "Обоснование стоимости"],
        "Наименование работ и затрат": ["Наименование работ и затрат", "Наименование работ", "Наименование затрат", "Наименование", "Описание вида работ", "Наименование работ и затрат, единица измерения"],
        "Единица измерения": ["Единица измерения", "Ед. изм.", "Единица", "Ед. изм.", "ед. измер.", "ед. изм.", "Ед. измерен."],
        "на единицу": ["на единицу"],
        "коэффициенты": ["коэффициенты"],
        "всего с учетом коэффициентов": ["всего с учетом коэффициентов"],
        "на единицу_2": ["на единицу"],
        "коэффициенты_2": ["коэффициенты"],
        "всего": ["всего"],
        "Индексы": ["Индексы"],
        "Сметная стоимость в текущем уровне цен, руб.": ["Сметная стоимость в текущем уровне цен, руб."],
    }

    # Словарь для хранения найденных столбцов
    if found_columns is None:
        found_columns = {key: None for key in column_name_variations}

    used_columns = set()  # Хранит уже использованные столбцы

    try:
        # with open(log_file_path, "a", encoding="utf-8") as log_file:
        #     log_file.write("Начало поиска столбцов\n")

            # Проход по всем столбцам в строке
            for column_name, column_value in row_data.items():
                if not column_name or not column_value:
                    # log_file.write(f"Пропуск столбца: {column_name} - {column_value}\n")
                    continue

                try:
                    column_value_normalized = clean_and_normalize_string(str(column_value))
                except Exception as e:
                    # print(f"Ошибка нормализации значения столбца '{column_value}': {e}")
                    # log_file.write(f"Ошибка нормализации значения столбца '{column_value}': {e}\n")
                    continue

                for standard_name, variations in column_name_variations.items():
                    try:
                        # Пропускаем вторичные столбцы до нахождения первичных
                        if standard_name in ["на единицу_2", "коэффициенты_2"]:
                            if not (found_columns["на единицу"] and found_columns["коэффициенты"]):
                                continue

                        # Если столбец уже найден, пропускаем
                        if found_columns[standard_name] is not None:
                            continue

                        # Исключаем повторное использование столбцов для вторичных
                        if standard_name in ["на единицу_2", "коэффициенты_2"] and column_name in used_columns:
                            continue

                        # Проверяем совпадение
                        if any(clean_and_normalize_string(variation) == column_value_normalized for variation in variations):
                            found_columns[standard_name] = column_name
                            used_columns.add(column_name)  # Помечаем столбец как использованный
                            # log_file.write(f"Нашли '{column_value}' для '{standard_name}'\n")
                            break
                    except Exception as e:
                        pass
                        # print(f"Ошибка при проверке столбца '{column_name}' для '{standard_name}': {e}")
                        # log_file.write(f"Ошибка при проверке столбца '{column_name}' для '{standard_name}': {e}\n")

    except Exception as e:
        print(f"Ошибка при работе с файлом: {e}")
        raise e  # Выбрасываем исключение для более высокого уровня обработки
    return found_columns

# Поиск нужных итоговых строк для расценок
def find_total_value(local_records_data, total_column):

    for data in local_records_data:
        # После текущей строки начинаем искать "Всего по позиции"
        row_data = data.local_estimate_row_data
        if row_data:
            # Проходим по каждой ячейке строки
            for key, value in row_data.items():
                if value and isinstance(value, str):
                    normalized_value = clean_and_normalize_string(value)
                    if normalized_value == "всегопопозиции":
                        return row_data.get(total_column)
    return None

# Проверяем каждое ключевое слово
def keyword_in_text(keyword, text):
    pattern = rf'{re.escape(keyword)}'
    return re.search(pattern, text) is not None

# Сортироака локальных смет (Архив)
def local_estimates_data_sort(request, project_id):
    current_section_name = None
    success_flag = True
    total_deleted = 0

    #Списки для определения типа затраты
    equipment_materials_keywords = [
        "ос-15", "ос15", "ооо", "ао", "siemens", "ка№", "ка п.",
        "тка ооо", "конъюктурный анализ", "договор №", "договор поставки", "cisco", "тц_", "тц-",
        "-тц", "ткп", "кп ооо", "кп ао", "кп", "договорная цена", "прайс",
        "прайс-лист", "фссц", "спецификация №", "мониторинг", "счет ООО", "счет ао", "счет№",
        "счет-спецификация", "счет на оплату", "счет-фактура", "BEWARD", "Cisco", "http://www.", "Hyperline",
        "NETWORK", "N-Kabel", "Phoenix contact", "rittaler.ru", "RS24.ru", "X-COM от 15.04.2020", "Z kabel",
        "Z.KABEL", "Абсолют Сибирь", "АВС Электро", "Акт приема-передачи  оборудования", "Арсенал", "АСбергАС", "входит в комплект поставки",
        "входит в комплект поставки разъединителя", "Входит в комплект поставки ЩПТ", "входит в комплект поставки ячейки КРУ", "Гарден Центр Групп", "Договор поставки", "Евроавтоматика",
        "Завод ИНКАБ", "Заявка на поставку Товара", "из существующего подвеса", "Изм.6 Пр.1", "Инженерные строительные решения", "кабель.рф", "Калькуляция №",
        "Калькуляция определения", "Каскад Электро", "Каталог", "Коммерческое предложение", "Компания ИМАГ", "Конъюнктурный анализ", "Кталог ЭТМ",
        "Миг-Электро", "Минстрой РФ", "Монитонг цен", "на ж/б", "Надбавка к стоимости бетона", "Надбавка на водонепроницаемость", "Надбавка на морозостойкость",
        "накладная", "Не указано", "О.У. Приложение 15", "Оборудование заказчика", "ОП прил", "ОП ТССЦ", "П2200059",
        "Письмо Минстрой", "Поставка Заказчика", "Поставка подрядчика", "Поставляется комплектно с ЗВУ", "Поставляется комплекто с ШР1", "Постановление правительства РФ №310", "Прай",
        "Предложение ГК Блок", "Предложение Ижорастройком", "Приложенеи к договору", "Приложение к письму", "Приложение таблица", "Приложение к Допсоглашение", "ПрософтСистемы",
        "Пульс цен", "релейную защиту и автоматику", "Русский свет", "СБЦИИС", "ССЦ", "стоимость устройства входит", "Стоимость учтена",
        "СтройПром ЖБИ", "СФ №", "СЦ 7.5-1-2-01", "СЦиР5.4_0-16-267-7-2-12", "СЦиР5.4_0-16-267-7-2-2", "сч/ф", "Счет ЭТМ",
        "Т/Н №", "ТД УНКОМТЕХ", "ТД МЕГАПРОМ", "тех часть ТССЦ", "Тех. часть", "ТЗВА", "ТН №",
        "Товарная накладная", "Том", "ТОРГ", "ТССЦ", "ТСЦ", "ТСЭМ", "ТЦ",
        "ТЧ ", "ТЧ-", "УралЭнергоСервис", "ФСЭМ", "Фундболт", "Ц_", "Цена поставщика",
        "Шефмонтаж выключателя", "ЭКРА", "Элек.ру", "Электрокомплектсервис", "Электрощит", "Энергия", "ЭОК+",
        "ЭТМ", "Материал со склада", "Давальческий материал", "стоимость материала  входит в стоимость", "01.1.", "01.2.", "01.3.",
        "01.4.", "01.5.", "01.6.", "01.7.", "01.8.", "02.1.", "02.2.", "02.3.", "02.4.", "03.1.", "03.2.", "04.1.", "04.2.", "04.3.",
        "05.1.", "05.2.", "05.3.", "05.4.", "06.1.", "06.2.", "07.1.", "07.2.", "07.3.", "07.4.", "07.5.", "08.1.", "08.2.", "08.3.",
        "08.4.", "09.1.", "09.2.", "09.3.", "09.4.", "10.1.", "10.2.", "10.3.", "10.4.", "11.1.", "11.2.", "11.3.", "12.1.", "12.2.",
        "13.1.", "13.2.", "14.1.", "14.2.", "14.3.", "14.4.", "14.5.", "15.1.", "15.2.", "16.1.", "16.2.", "16.3.", "17.1.", "17.2.",
        "17.3.", "17.4.", "18.1.", "18.2.", "18.3.", "18.4.", "18.5.", "19.1.", "19.2.", "19.3.", "19.4.", "20.1.", "20.2.", "20.3.",
        "20.4.", "20.5.", "20.9.", "21.1.", "21.2.", "22.1.", "22.2.", "23.1. ", "23.2. ", "23.3. ", "23.4. ", "23.5. ", "23.6. ", "23.7. ",
        "23.8. ", "24.1. ", "24.2. ", "24.3. ", "25.1. ", "25.2. ", "25.3. ", "26.1.", "27.1. ", "27.2.", "100.1", "100.2", "101-", "102.1",
        "102.2", "102-", "103-", "104-", "105.1", "105-", "106.1", "107.1", "107-", "109.1", "109.2", "109-", "11.1", "11.2",
        "11.3", "110.", "110-", "111.1", "111.2", "111-", "112.1", "113-", "114.1", "114-", "115.", "116.", "117.",
        "117-", "118.", "119.", "120.1", "121.1", "122.1", "123.1", "124.1", "125.1", "126.1", "127.1", "128.1",
        "129.1", "13.1", "13.2", "130.1", "13-03", "131.1", "133.1", "134.1", "136.1", "137.1", "138.1", "14.1", "14.2", "14.3",
        "14.4", "14.5", "141.1", "142.1", "143.1", "144.2", "146.1", "147.1", "149.1", "15.1", "15.2", "150.1", "150302", "154.1",
        "154.2", "16.10", "16.11", "16.20", "161.1", "163.1", "163.2", "164.1", "165.1", "165.2", "166.1", "169.1",
        "17.1", "17.2", "170.1", "171.1", "172.1", "174.1", "174.2", "175.1", "176.1", "176.2", "179.1", "18.1", "18.2", "18.3",
        "18.4", "18.5", "180.1", "183.", "186.1", "189.1", "19.1", "19.2", "19.3", "19.4", "19.5", "194.1", "196.1", "196.2", "198.1",
        "2.10", "2.12", "2.13", "2.1.", "2.2.", "2.5.", "2.7.", "20.1", "20.2", "20.3", "20.4", "20.5",
        "201-", "202.1", "202-", "203-", "204-", "206-", "207.1", "208.1", "21.1", "21.2", "22.1", "22.2", "224.1",
        "224.2", "228.1", "23.1", "23.2", "23.3", "23.4", "23.5", "23.6", "23.7", "23.8", "234.1", "237.1", "24.1", "24.2",
        "24.3", "25.1", "25.2", "25.3", "254.", "26.1", "26.2", "263.", "266.", "268.", "27.1", "27.2", "274.", "28.1",
        "28.2", "292.", "3.10", "3.11", "3.12", "3.14", "3.20", "3.5.", "3.7.", "3.9.", "30.1", "301-", "302-", "31.1",
        "314.", "32.1", "32.2", "32.3", "32.4", "32.5", "33.1", "33.2", "338.", "34.1", "34.2", "35.1", "35.2", "36.1",
        "36.2", "362.", "364.", "37.1", "37.2", "37.3", "38.1", "38.2", "39.1", "4.10", "4.12", "4.13", "4.2.", "4.5.",
        "4.7.", "400004", "401-", "402-", "403-", "404-", "407-", "408-", "41.1", "410-", "411-", "412-", "413-", "414-",
        "42.1", "42.2", "43.1", "43.2", "44.1", "44.2", "45.1", "45.2", "46.1", "46.2", "47.1", "47.2", "48.1", "49.1",
        "49.2", "5.10", "5.11", "5.12", "5.14", "5.25", "50.1", "50.2", "501-", "502-", "503-", "504-", "506-", "507-",
        "508-", "509-", "51.1", "52.1", "53.1", "53.2", "54.1", "54.2", "55.1", "55.2", "55.3", "56.1", "56.2", "57.1",
        "58.1", "59.1", "59.2", "6.10", "6.11", "6.12", "6.20", "6.22", "60.1", "61.1", "61.2", "61.3", "62.1", "62.2",
        "62.3", "62.4", "62.5", "62.6", "62.7", "63.1", "63.2", "63.3", "63.4", "64.1", "64.2", "64.5", "65.1", "65.2",
        "65.3", "66.1", "66.2", "67.1", "67.2", "68.1", "68.2", "69.1", "69.2", "7.10", "7.11", "7.12", "7.13", "7.20",
        "7.23", "70.1", "71.1", "71.2", "72.1", "73.1", "73.2", "74.1", "74.2", "75.1", "77.1", "78.1", "78.2", "79.1",
        "8.10", "8.11", "8.12", "8.13", "8.14", "8.20", "80.1", "81.1", "82.1", "83.1", "84.1", "85.1", "86.1", "86.2",
        "9.10", "9.11", "9.13", "9.14", "9.20", "9.22", "90.1", "90.2", "91.0", "91.1", "92.1", "93.1", "93.2", "94.1",
        "95.1", "96.1", "98.1", "99.1", "99.2", "Заявка ", "Договор", "входит в", "вкл. В", "http", "КА 1", "КА 2", "КА №", "КА!",
        "КА1", "Калькул", "Коммерч", "Конъюнктур", "Монитонг", "ТСЦ ", "ТЦ.0", "ТЦ.1", "ТЦ10", "ТЦ20", "ТЦ21", "ТЦ61", "ТЦ62", "ТЧ -61",
        "ТЧ-10", "ТЧ-18", "ТЧ-21", "ТЧ-61", "Ц_10", "Ц_64", "ЭОК"
    ]
    works_keywords = ["фссцпг", "фер", "ферм", "тер", "терм", "ферп", "терп"]
    coefficient_keywords = ["приказ №", "приказ от", "Приказ"]
    building_keywords = ["999-9900"]
    unregulated_keywords = ["999-9950"]
    NR_SP_keywords = ["пр/"]

    # Шаг 1: Выбор данных локальных смет по проекту и удаление ранее отсортированных данных
    try:
        summary_estimate = SummaryEstimateCalculation.objects.filter(invest_project_id=project_id)
        local_records = LocalCostEstimate.objects.filter(summary_estimate_calculation_id__in=summary_estimate)


        for local_record_delete in local_records:
            deleted_count, _ = LocalEstimateDataSort.objects.filter(local_cost_estimate=local_record_delete).delete()
            total_deleted += deleted_count
        
        messages.success(request, f"Удалено {total_deleted} отсортированных записей")

    except Exception as e:
        messages.error(request, f"Ошибка при удалении старых записей: {e}")
        success_flag = False  

    # Шаг 2: Поиск нужных столбцов в  local_records_data
    try:        
        for local_record in local_records:

            local_records_expense_nme = Expenses.objects.filter(local_cost_estimate_id=local_record)


            demontazh_found = False
            for expense in local_records_expense_nme:
                if expense.expense_nme is not None and "демонтаж" in expense.expense_nme.lower():
                    LCR = expense.local_cost_estimate_id.local_cost_estimate_code
                    messages.info(request, f"Смета {LCR} не отсортирована, найдено слово демонтаж")
                    demontazh_found = True
                    break

            if demontazh_found:
                continue

            local_records_data = LocalEstimateData.objects.filter(local_cost_estimate_id=local_record).order_by('local_estimate_data_rn')
            
            try:
                found_columns = {
                    "Обоснование": None,
                    "Наименование работ и затрат": None,
                    "Единица измерения": None,
                    "Количество": None,
                    "Всего": None,
                }

                max_rows_to_check = 60  # Максимальное количество строк для обработки
                max_row_range = 5  # Количество строк, после которых сбрасываем результаты
                rows_buffer = []  # Буфер для хранения последних строк

                for idx, data in enumerate(local_records_data):

                    if idx >= max_rows_to_check:  # Ограничиваем поиск первыми 100 строками
                        break

                    row_data = data.local_estimate_row_data

                    if row_data:

                        rows_buffer.append(row_data)
                        if len(rows_buffer) > max_row_range:
                            rows_buffer.pop(0)  # Удаляем старую строку, если буфер превышает 5 строк

                        # Проверяем буфер из 5 строк
                        temp_found_columns = {key: None for key in found_columns.keys()}
                        for buffered_row in rows_buffer:
                            temp_found_columns = find_required_columns(buffered_row, temp_found_columns)                      

                        if all(temp_found_columns.values()):
                            found_columns = temp_found_columns
                            messages.success(request, f"Найдены все столбцы в локальной смете ID: {local_record.local_cost_estimate_code}")                                 
                            break

                        elif temp_found_columns["Обоснование"] is not None and temp_found_columns["Наименование работ и затрат"] is not None:
                            found_columns = temp_found_columns
                            messages.success(
                                request, 
                                f"Найдены столбцы 'Обоснование' и 'Наименование работ и затрат' в локальной смете ID: {local_record.local_cost_estimate_code}"
                            )
                            break

                if not all(found_columns.values()):
                    messages.error(request, f"Не найдены все столбцы в локальной смете ID: {local_record.local_cost_estimate_code} {found_columns}") 

            except Exception as e:
                messages.error(request, f"Ошибка при поиске нужных столбцов: {e} в локальной смете {local_record}" )
                success_flag = False
                continue

            try:
                for data in local_records_data:
                    row_data = data.local_estimate_row_data

                    if row_data:
                        obosnovanie_column = found_columns["Обоснование"]
                        naimenovanie_column = found_columns["Наименование работ и затрат"]
                        unit_column = found_columns["Единица измерения"]
                        quantity_column = found_columns["Количество"]
                        total_column = found_columns["Всего"]
                        
                        # Проверяем наличие ключевой фразы "Раздел" в данных
                        section_code_name = None
                        for key, value in row_data.items():
                            if isinstance(value, str) and "Раздел" in value:
                                section_code_name  = value
                                break

                        # Если нашли новый раздел, сохраняем его как текущий
                        if section_code_name:
                            current_section_name = section_code_name 

                        try:
                            # Инициализируем переменные с дефолтными значениями
                            estimate_type = "Прочее"
                            estimate_type_code = 40

                            lower_data_code = str(row_data.get(obosnovanie_column)).lower()

                            # Определяем тип по ключевым словам в названии раздела
                            if any(keyword_in_text(keyword.lower(), lower_data_code) for keyword in equipment_materials_keywords):
                                estimate_type = "Оборудование/Материал"                                
                                estimate_type_code = 1
                            elif any(keyword_in_text(keyword.lower(), lower_data_code) for keyword in works_keywords):
                                estimate_type = "Работы"
                                estimate_type_code = 2
                            elif any(keyword_in_text(keyword.lower(), lower_data_code) for keyword in coefficient_keywords):
                                estimate_type = "Коэффициент"
                                estimate_type_code = 3
                            elif any(keyword_in_text(keyword.lower(), lower_data_code) for keyword in unregulated_keywords):
                                estimate_type = "Вспомогательные ненормируемые материалы"
                                estimate_type_code = 4 
                            elif any(keyword_in_text(keyword.lower(), lower_data_code) for keyword in building_keywords):
                                estimate_type = "Строительный мусор"
                                estimate_type_code = 5
                            elif any(keyword_in_text(keyword.lower(), lower_data_code) for keyword in NR_SP_keywords):
                                estimate_type = "НР и СП"
                                estimate_type_code = 5

                            data_name = row_data.get(naimenovanie_column)
                            total_value = row_data.get(total_column)

                            # Если "Всего" отсутствует, ищем его в следующих строках
                            if not total_value or total_value == "":
                                total_value = find_total_value(local_records_data, total_column)

                            if data_name and isinstance(data_name, str) and all(word not in data_name for word in ("Итого", "в т.ч.", "Всего", "ВСЕГО", "Должность", "в том числе")):
                                sorted_data = LocalEstimateDataSort(
                                    local_cost_estimate=local_record,
                                    local_estimate_data_code=row_data.get(obosnovanie_column) or "Не определено",  # Значение по умолчанию
                                    local_estimate_data_part=current_section_name or "Не определено",  # Значение по умолчанию
                                    local_estimate_data_name=row_data.get(naimenovanie_column) or "Не определено",  # Значение по умолчанию
                                    local_estimate_data_type=estimate_type or "Не определено",  # Значение по умолчанию
                                    local_estimate_data_type_code=estimate_type_code or 0,  # Значение по умолчанию для кода типа
                                    local_estimate_data_unit=row_data.get(unit_column) or "шт.",  # Значение по умолчанию для единицы измерения
                                    local_estimate_data_count=row_data.get(quantity_column) or 0,  # Значение по умолчанию для количества
                                    local_estimate_data_total=total_value or 0,  # Значение по умолчанию для итоговой стоимости
                                )
                                sorted_data.save()

                        except Exception as e:
                            messages.error(request, f"Ошибка при сохранении отсортированных данных: {e}")
                            success_flag = False

            except Exception as e:
                messages.error(request, f"Ошибка при выделении типов затрат : {e}")
                success_flag = False
                continue      

    except Exception as e:
            messages.error(request, f"Ошибка при выделении типов затрат : {e}")
            success_flag = False

    # Сообщение об успешном завершении выводим только если не было ошибок
    if success_flag:
        messages.success(request, "Процесс сортировки ЛСР успешно завершен.")

    return redirect('myapp:object_analog_2')

# Сортироака локальных смет
def local_estimates_data_sort_new(request, project_id):
    current_section_name = None
    success_flag = True
    total_deleted = 0

    #Списки для определения типа затраты
    equipment_materials_keywords = ["ос-15", "ос15", "ооо", "ао", "siemens", "ка№", "ка п.", "тка ооо", "конъюктурный анализ", "договор №", "договор поставки"
                                        "cisco", "тц_", "тц-", "-тц", "ткп", "кп ооо", "кп ао", "кп", "договорная цена", "прайс", "прайс-лист",
                                        "62.4.01.01-0005", "20.2.03.09-0001", "12.1.02.15", "фссц", "спецификация №", "мониторинг",
                                        "счет ООО", "счет ао", "счет№", "счет-спецификация", "счет на оплату", "счет-фактура"]
    works_keywords = ["фссцпг", "фер", "ферм", "тер", "терм", "ферп", "терп"]
    coefficient_keywords = ["приказ №", "приказ от", "Приказ"]
    building_keywords = ["999-9900"]
    unregulated_keywords = ["999-9950"]
    NR_SP_keywords = ["пр/"]

    # Шаг 1: Выбор данных локальных смет по проекту и удаление ранее отсортированных данных
    try:
        summary_estimate = SummaryEstimateCalculation.objects.filter(invest_project_id=project_id)
        local_records = LocalCostEstimate.objects.filter(summary_estimate_calculation_id__in=summary_estimate)

        for local_record_delete in local_records:
            deleted_count, _ = LocalEstimateDataSort_2.objects.filter(local_cost_estimate=local_record_delete).delete()
            total_deleted += deleted_count
        
        messages.success(request, f"Удалено {total_deleted} отсортированных записей")

    except Exception as e:
        messages.error(request, f"Ошибка при удалении старых записей: {e}")
        success_flag = False  

    # Шаг 2: Поиск нужных столбцов в  local_records_data
    try:        
        for local_record in local_records:

            
            local_records_data = LocalEstimateData.objects.filter(local_cost_estimate_id=local_record).order_by('local_estimate_data_rn')
            
            try:
                found_columns = {
                    "Обоснование": None,
                    "Наименование работ и затрат": None,
                    "Единица измерения": None,
                    "на единицу": None,
                    "коэффициенты": None,
                    "всего с учетом коэффициентов": None,
                    "на единицу_2": None,
                    "коэффициенты_2": None,
                    "всего": None,
                    "Индексы": None,
                    "Сметная стоимость в текущем уровне цен, руб.": None,
                }

                max_rows_to_check = 40  # Максимальное количество строк для обработки
                max_row_range = 5  # Количество строк, после которых сбрасываем результаты
                rows_buffer = []  # Буфер для хранения последних строк

                for idx, data in enumerate(local_records_data):

                    if idx >= max_rows_to_check:  
                        break

                    row_data = data.local_estimate_row_data

                    if row_data:

                        rows_buffer.append(row_data)
                        if len(rows_buffer) > max_row_range:
                            rows_buffer.pop(0)  # Удаляем старую строку, если буфер превышает 5 строк

                        # Проверяем буфер из 5 строк
                        temp_found_columns = {key: None for key in found_columns.keys()}
                        for buffered_row in rows_buffer:
                            temp_found_columns = find_required_columns(buffered_row, temp_found_columns)                      

                        if all(temp_found_columns.values()):
                            found_columns = temp_found_columns
                            messages.success(request, f"Найдены все столбцы в локальной смете ID: {local_record.local_cost_estimate_code}")                                 
                            break

                if not all(found_columns.values()):
                    messages.error(request, f"Не найдены все столбцы в локальной смете ID: {local_record.local_cost_estimate_code} {found_columns}") 

            except Exception as e:
                messages.error(request, f"Ошибка при поиске нужных столбцов: {e} в локальной смете {local_record}" )
                success_flag = False
                continue

            try:
                for data in local_records_data:
                    row_data = data.local_estimate_row_data

                    if row_data:
                        obosnovanie_column = found_columns["Обоснование"]
                        naimenovanie_column = found_columns["Наименование работ и затрат"]
                        unit_column = found_columns["Единица измерения"]
                        unit_column_one = found_columns["на единицу"]
                        count_coef = found_columns["коэффициенты"]
                        total_count_coef = found_columns["всего с учетом коэффициентов"]
                        cost_one = found_columns["на единицу_2"]
                        cost_coef = found_columns["коэффициенты_2"]
                        cost_total_base = found_columns["всего"]
                        index = found_columns["Индексы"]
                        cost_total_now = found_columns["Сметная стоимость в текущем уровне цен, руб."]
                        
                        # Проверяем наличие ключевой фразы "Раздел" в данных
                        section_code_name = None
                        for key, value in row_data.items():
                            if isinstance(value, str) and "Раздел" in value:
                                section_code_name  = value
                                break

                        # Если нашли новый раздел, сохраняем его как текущий
                        if section_code_name:
                            current_section_name = section_code_name 

                        try:
                            # Инициализируем переменные с дефолтными значениями
                            estimate_type = "Прочее"
                            estimate_type_code = 40

                            lower_data_code = str(row_data.get(obosnovanie_column)).lower()                        

                            # Определяем тип по ключевым словам в названии раздела
                            if any(keyword in lower_data_code for keyword in equipment_materials_keywords):
                                estimate_type = "Оборудование/Материал"
                                estimate_type_code = 1
                            elif any(keyword in lower_data_code for keyword in works_keywords):
                                estimate_type = "Работы"
                                estimate_type_code = 2
                            elif any(keyword in lower_data_code for keyword in coefficient_keywords):
                                estimate_type = "Коэффициент"
                                estimate_type_code = 3
                            elif any(keyword in lower_data_code for keyword in unregulated_keywords):
                                estimate_type = "Вспомогательные ненормируемые материалы"
                                estimate_type_code = 4 
                            elif any(keyword in lower_data_code for keyword in building_keywords):
                                estimate_type = "Строительный мусор"
                                estimate_type_code = 5
                            elif any(keyword in lower_data_code for keyword in NR_SP_keywords):
                                estimate_type = "НР и СП"
                                estimate_type_code = 5

                            data_name = row_data.get(naimenovanie_column)
                            total_value = row_data.get(cost_total_base)

                            # Если "Всего" отсутствует, ищем его в следующих строках
                            if not total_value or total_value == "":
                                total_value = find_total_value(local_records_data, cost_total_base)


                            if data_name and isinstance(data_name, str) and all(word not in data_name for word in ("в т.ч.", "Всего", "ВСЕГО", "Должность", "в том числе")):
                                sorted_data = LocalEstimateDataSort_2(
                                    local_cost_estimate=local_record,
                                    local_estimate_data_code=row_data.get(obosnovanie_column),  
                                    local_estimate_data_part=current_section_name,  
                                    local_estimate_data_name=row_data.get(naimenovanie_column),  
                                    local_estimate_data_type=estimate_type,  
                                    local_estimate_data_type_code=estimate_type_code,  
                                    local_estimate_data_unit=row_data.get(unit_column),  
                                    local_estimate_data_count_one = row_data.get(unit_column_one), 
                                    local_estimate_data_count_coef =  row_data.get(count_coef),
                                    local_estimate_data_count_total = row_data.get(total_count_coef),
                                    local_estimate_data_cost_one = row_data.get(cost_one),
                                    local_estimate_data_cost_coef = row_data.get(cost_coef),
                                    local_estimate_data_cost_total_base = row_data.get(cost_total_base),
                                    local_estimate_data_index = row_data.get(index),
                                    local_estimate_data_cost_total_now = row_data.get(cost_total_now),
                                )
                                sorted_data.save()

                        except Exception as e:
                            messages.error(request, f"Ошибка при сохранении отсортированных данных: {e}")
                            success_flag = False

            except Exception as e:
                messages.error(request, f"Ошибка при выделении типов затрат : {e}")
                success_flag = False
                continue      

    except Exception as e:
            messages.error(request, f"Ошибка при выделении типов затрат : {e}")
            success_flag = False

    # Сообщение об успешном завершении выводим только если не было ошибок
    if success_flag:
        messages.success(request, "Процесс сортировки ЛСР успешно завершен.")

    return redirect('myapp:object_analog_2')


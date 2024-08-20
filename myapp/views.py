from django.shortcuts import render
from .models import TempTable, DictSecChapter, TempTableUNC, TempTableССКUNC, ExpensesToEpcMap, ExpensesToEpcMap
import pandas as pd
import re
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse
from collections import defaultdict
from collections import defaultdict, OrderedDict

# Валидация кварталов
def format_quarter_info(quarter_str):
    # Паттерн для извлечения квартала и года с пересчетом
    pattern_with_base_year = r'\b(\d{4})\s*г(?:од|года)?\s*с\s*пересчетом\s*на\s*(\d+|IV|I|II|III|IV)\s*квартал\s*(\d{4})\s*г(?:од|года)?\b'
    match_with_base_year = re.search(pattern_with_base_year, quarter_str, re.IGNORECASE)
    
    if match_with_base_year:
        quarter = match_with_base_year.group(2)
        year = match_with_base_year.group(3)
        # Приведение к формату 'IV квартал 2018 г.'
        return f'{quarter} квартал {year} г.)'
    
    # Паттерн для извлечения квартала и года без пересчета
    pattern_without_base_year = r'(\d+|IV|I|II|III|IV)\s*квартал\s*(\d{4})\s*г(?:од|года)?'
    match_without_base_year = re.search(pattern_without_base_year, quarter_str, re.IGNORECASE)
    
    if match_without_base_year:
        quarter = match_without_base_year.group(1)
        year = match_without_base_year.group(2)
        # Приведение к формату 'IV квартал 2018 г.'
        return f'{quarter} квартал {year} г.'
    
    # Паттерн для извлечения квартала и года без пересчета
    pattern_without_base_year = r'(\d+|IV|I|II|III|IV)\s*кв.\s*(\d{4})\s*г(?:од|года)?'
    match_without_base_year = re.search(pattern_without_base_year, quarter_str, re.IGNORECASE)
    
    if match_without_base_year:
        quarter = match_without_base_year.group(1)
        year = match_without_base_year.group(2)
        # Приведение к формату 'IV квартал 2018 г.'
        return f'{quarter} квартал {year} г.'
    
    # Новый паттерн для строки: "1 кв 2019 года с НДС"
    pattern_simple_quarter = r'(\d+|IV|I|II|III|IV)\s*кв(?:квартал)?\s*(\d{4})\s*г(?:од|года)?'
    match_simple_quarter = re.search(pattern_simple_quarter, quarter_str, re.IGNORECASE)
    
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

# Ввод нового ключевого слова
def add_expense_to_epc(request):
    if request.method == 'POST':
        expense_name = request.POST.get('expense_name')
        expense_epc = request.POST.get('expense_epc')
        
        # Создаем и сохраняем новый объект
        new_expense = ExpensesToEpcMap(expenses_to_epc_map_name=expense_name, expenses_to_epc_map_epc=expense_epc)
        new_expense.save()
        
        return redirect('myapp:dict_word_page')  # Перенаправляем на ту же страницу или другую по вашему выбору

    return render(request, 'dict_word_page.html')  # Укажите ваш шаблон

# Удаление ключевого слова
def delete_expense_to_epc(request):
    if request.method == 'POST':
        expense_id = request.POST.get('expense_id')
        
        try:
            # Находим объект и удаляем его
            expense = ExpensesToEpcMap.objects.get(expenses_to_epc_map_id=expense_id)
            expense.delete()
        except ExpensesToEpcMap.DoesNotExist:
            return HttpResponse("Ключевое слово с таким ID не найдено", status=404)
        
        return redirect('myapp:dict_word_page')  # Перенаправляем на ту же страницу или другую по вашему выбору

    return render(request, 'dict_word_page.html')  # Укажите ваш шаблон

# Очистка списка парсинга
def delete_temp(request):
    if request.method == 'POST':
        # Удаляем все записи из TempTable
        TempTable.objects.all().delete()
        
        # Удаляем все записи из TempTableUNC
        TempTableUNC.objects.all().delete()
        
        # Перенаправляем пользователя после удаления
        return redirect('myapp:start')  # Замените 'some_page' на нужный URL или название маршрута
    else:
        return redirect('myapp:start')  # Замените 'some_page' на нужный URL или название маршрута

# Очистка списка связывания
def delete_CCR_UNC(request):
    if request.method == 'POST':
        # Удаляем все записи из TempTableССКUNC
        TempTableССКUNC.objects.all().delete()        
       
        # Перенаправляем пользователя после удаления
        return redirect('myapp:CCP_UNC_page')  # Замените 'some_page' на нужный URL или название маршрута
    else:
        return redirect('myapp:CCP_UNC_page')  # Замените 'some_page' на нужный URL или название маршрута


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
        grouped_records[record.temp_table_id.chapter_id.dict_sec_chapter_id].append(record)

    # Сортировка по главам
    sorted_grouped_records = OrderedDict(sorted(grouped_records.items()))

    # Получаем все записи из TempTableССКUNC, чтобы исключить связанные позиции
    linked_temp_records_ids = TempTableССКUNC.objects.values_list('temp_table_id', flat=True)
    linked_temp_UNC_records_ids = TempTableССКUNC.objects.values_list('temp_table_unc_id', flat=True)

    # Фильтруем TempTable и TempTableUNC, чтобы оставить только несвязанные позиции
    unlinked_temp_records = all_temp_records.exclude(id__in=linked_temp_records_ids)
    unlinked_temp_UNC_records = all_temp_UNC_records.exclude(id__in=linked_temp_UNC_records_ids)

    # Группируем несвязанные TempTable записи по главам
    unlinked_grouped_records = defaultdict(list)
    for record in unlinked_temp_records:
        unlinked_grouped_records[record.chapter_id.dict_sec_chapter_id].append(record)

    # Сортировка по главам для несвязанных записей
    sorted_unlinked_grouped_records = OrderedDict(sorted(unlinked_grouped_records.items()))

    context = {
        'grouped_records': sorted_grouped_records,
        'unlinked_grouped_records': sorted_unlinked_grouped_records,
        'unlinked_temp_UNC_records': unlinked_temp_UNC_records,
    }
    print(sorted_unlinked_grouped_records)
    return render(request, 'CCP_UNC.html', context)

# Страница ключевых слов
def dict_word_page(request):

    dict_word = ExpensesToEpcMap.objects.all()
    # Группируем записи по главам
    context = {
            'dict_word': dict_word,
        }
    return render(request, 'dict_word_page.html', context)

# Импорт CCR
def add_CCR(request):
    if request.method == 'POST' and request.FILES.get('CCR'):
        uploaded_file = request.FILES['CCR']

        try:
            # Шаг 1: Чтение Excel-файла в DataFrame
            df = pd.read_excel(uploaded_file, sheet_name=0, engine='openpyxl')
            rows_data = []  # Список для хранения всех строк

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
                    print(f"Самая первая {row_values}")
                    
                    # Пробуем найти квартал в каждой строке по отдельности
                    for i in range(0, len(row_values)):
                        print(f"Первая проверка {i}")
                        if isinstance(row_values[i], str):
                            cleaned_value = re.sub(r'\s+', ' ', str(row_values[i]).strip().lower())
                            print(f"Перед условием {cleaned_value}")
                            if any(re.search(phrase.lower(), cleaned_value) for phrase in key_phrases_quarter):
                                print(f"Ищем квартал {cleaned_value}")
                                quarter_row = format_quarter_info(cleaned_value)
                                if quarter_row:
                                    messages.success(request, f"Найден квартал: {quarter_row}")
                                    break  # Если нашли квартал, выходим из цикла

                    # Если не нашли, объединяем все строки и ищем в объединенной строке
                    if quarter_row is None:
                        combined_str = " ".join([str(rv) for rv in row_values if isinstance(rv, str)]).strip()
                        print(f"Объединенная строка: {combined_str}")
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
                            print(f"инальная строка")
                            target_column = cleaned_value  
                            messages.success(request, f"Финальная строка найдена: {target_column}")
                            break

                if current_chapter is not None:
                    try:
                        row_data = {
                            'chapter_id': current_chapter,
                            'object_costEstimate_id': row_values[1],
                            'local_costEstimate_id': row_values[1],
                            'expenses_name': row_values[2],
                            'construction_cost': row_values[3],
                            'installation_cost': row_values[4],
                            'equipment_cost': row_values[5],
                            'other_cost': row_values[6],
                            'total_cost': row_values[7],
                        }
                        # Если строка найдена после "Итого по главе", добавляем ее в additional_rows
                        if target_column:
                            additional_rows.append(row_data)
                        else:
                            rows_to_insert.append(row_data)
                    except Exception as e:
                        messages.error(request, f"Ошибка в строке {index}: {e}")

            # Сохранение данных после последней главы
            if rows_to_insert:
                print(f"Сохраняем данные")
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

                print(f"Тип формы: {row_type}")
                
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
                
                if isinstance(row.iloc[4], str) and re.search(r'Итого', str(row.iloc[4]).strip(), re.IGNORECASE):
                    messages.info(request, f"Условие срабатывает для записи в базу на строке {index + 1}")
                    
                    if rows_to_insert:
                        try:
                            for r in rows_to_insert:
                                TempTableUNC.objects.create(
                                    project_id=r['project_id'],
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
                                'project_id': row.iloc[3], # id проекта
                                'name_unc': row.iloc[4], # Имя УНЦ
                                'name_object': row.iloc[5], # Имя объекта
                                'voltage': row.iloc[9], # Напряжение
                                'TX': row.iloc[10], # Техническая характеристика
                                'count': row.iloc[15], # количевство
                                'unit': row.iloc[16], # еденица измерени
                                'unc_code': row.iloc[17], # номер расценки
                            }
                        elif row_type == 2:
                            row_data = {
                                'project_id': row.iloc[3], # id проекта
                                'name_unc': row.iloc[5], # Имя УНЦ
                                'name_object': row.iloc[6], # Имя объекта
                                'voltage': row.iloc[10], # Напряжение
                                'TX': row.iloc[11], # Техническая характеристика
                                'count': row.iloc[18], # количевство
                                'unit': row.iloc[19], # еденица измерени
                                'unc_code': row.iloc[20], # номер расценки
                            }

                        rows_to_insert.append(row_data)
                        messages.info(request, f"Найдена и добавлена строка данных на строке {index + 1}")
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
    
# Связывание
def add_UNC_CCR(request):
    try:
        # Шаг 1: Загрузка всех ключевых слов из справочника
        key_phrases = ExpensesToEpcMap.objects.all()
    except Exception as e:
        print(f"Ошибка при загрузке ключевых слов из справочника: {e}")
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
                    matching_keywords.append(clean_string(key_phrase.expenses_to_epc_map_name))
            
            if matching_keywords:
                unc_keyword_map[unc_record] = matching_keywords

        print(f"Карта ключевых слов: {unc_keyword_map}")
    except Exception as e:
        print(f"Ошибка при определении ключевых слов: {e}")
        messages.error(request, f"Ошибка при определении ключевых слов: {e}")
        return redirect('myapp:CCP_UNC_page')

    try:
        # Шаг 3: Проход по записям TempTable и поиск соответствий
        for unc_record, keywords in unc_keyword_map.items():
            for keyword in keywords:                
                for temp_record in TempTable.objects.all():
                    cleaned_expenses_name = clean_string(temp_record.expenses_name)
                    print(f"cleaned_expenses_name: {cleaned_expenses_name}")
                    # print(f"keyword: {keyword}")
                    if keyword in cleaned_expenses_name:
                        print(f"Найдено соответствие: {temp_record}")

                        # Проверка на наличие дубликатов
                        existing_record = TempTableССКUNC.objects.filter(
                            temp_table_id=temp_record,
                            temp_table_unc_id=unc_record,
                        ).exists()
                        print(f"existing_record: {existing_record}")

                        # Шаг 4: Сохранение результата в TempTableССКUNC
                        if not existing_record:
                            TempTableССКUNC.objects.create(
                                temp_table_id=temp_record,
                                temp_table_unc_id=unc_record,
                                matched_keyword=keyword,
                                additional_info=f"Связь по ключевому слову: {keyword}"
                            )
    except Exception as e:
        print(f"Ошибка при сохранении результатов: {e}")
        messages.error(request, f"Ошибка при сохранении результатов: {e}")
        return redirect('myapp:CCP_UNC_page')

    messages.success(request, "Процесс сопоставления успешно завершен.")
    return redirect('myapp:CCP_UNC_page')
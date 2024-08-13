from django.shortcuts import render
from .models import TempTable, DictSecChapter, TempTableUNC, TempTableССКUNC, ExpensesToEpcMap
import pandas as pd
import re
from django.shortcuts import redirect
from django.db import connection
from django.contrib import messages

# Удаляем пробелы и заменяем запятую на точку
def clean_decimal_value(value):
    if isinstance(value, str):
        value = value.replace(' ', '').replace(',', '.')
    return value

# Удаляем все записи из временной таблицы
def clear_temp_table():
    TempTable.objects.all().delete()
    with connection.cursor() as cursor:
        cursor.execute("ALTER SEQUENCE myapp_temptable_id_seq RESTART WITH 1")

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
    
    return None

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
    # Группируем записи по главам
    context = {
            'all_CCP_UNC': all_CCP_UNC,
        }
    return render(request, 'CCP_UNC.html', context)


# Импорт CCR
def add_CCR(request):
    if request.method == 'POST' and request.FILES.get('CCR'):
        uploaded_file = request.FILES['CCR']

        # Чтение Excel-файла в DataFrame
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        current_chapter = None
        rows_to_insert = []

        # Проход по строкам DataFrame и сохранение данных в базу
        for index, row in df.iterrows():
            row_values = row.tolist() 
            key_phrases_chapter = ["Глава"]
            for i in range(0, len(row)):
                if isinstance(row.iloc[i], str) and any(phrase in row.iloc[i].strip() for phrase in key_phrases_chapter):                          
                    match = re.search(r'\bГлава\s+(\d+)', row.iloc[i])
                    if match:
                        current_chapter = match.group(1)  # Извлекаем номер главы
                        chapter_instance = DictSecChapter.objects.get(dict_sec_chapter_id=current_chapter)
                        print(f"Номер главы {chapter_instance}")
                    continue         

            key_phrases_quarter = [
                "Составлен в ценах по состоянию на ",
                "Cоставлен в ценах по состоянию на  ",
                "Составлен в базисном (текущем) уровне цен"
            ]
            
            for i in range(len(row_values)):
                    value = row_values[i]
                    if isinstance(value, str):
                        cleaned_value = value.strip()                       
                        if any(phrase in cleaned_value for phrase in key_phrases_quarter):
                        # Объединяем все строки, если они содержат ключевые фразы
                            combined_str = " ".join([row_values[i] for i in range(len(row_values)) if isinstance(row_values[i], str)]).strip()                            
                            quarter_row = format_quarter_info(cleaned_value)                            
                            print(quarter_row)
                            if quarter_row:
                                break

            key_phrases = ["Итого по"]
            target_column = None
            for i in range(0, len(row)):
                if isinstance(row.iloc[i], str):
                    cleaned_value = row.iloc[i].strip()
                    if any(phrase in cleaned_value for phrase in key_phrases) and "главе" in cleaned_value:
                        target_column = cleaned_value  # Присваиваем найденное значение
                        break  # Прерываем цикл, если нашли нужное слово
 
            print(f"Перед условием {target_column} Список для сохранения в базу {rows_to_insert}")
            if target_column and rows_to_insert:
                # Записываем данные в базу только один раз
                for r in rows_to_insert:
                    TempTable.objects.create(
                        chapter_id=chapter_instance,
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
                # Очищаем список после записи
                rows_to_insert = []
                current_chapter = None
                continue

            # Если текущая строка относится к главе
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
                    # Проверяем на наличие NaN значений перед добавлением в список
                    if not any(pd.isna(value) for value in row_data.values()):
                        rows_to_insert.append(row_data)
                        print(f"Исходный список {rows_to_insert}")

                except Exception as e:
                    print(f"Error in row {index}: {e}")
                    print(f"Строка {index}: {row}")

        messages.success(request, "Данные успешно загружены в базу данных.")
        return redirect('myapp:start')
    else:
        print(f'Файла нет')
        return redirect('myapp:start')

# Импорт UNC
def add_UNC(request):
    if request.method == 'POST' and request.FILES.get('UNC'):
        uploaded_file = request.FILES['UNC']

        # Чтение Excel-файла в DataFrame
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        rows_to_insert = []                
        recording = False  # Переменная для начала записи

        try:
            # Проход по строкам DataFrame и сохранение данных в базу
            for index, row in df.iterrows():

                # Ожидаемая последовательность от 1 до 16
                expected_sequence = list(map(str, range(1, 16)))

                # Проверка на строку с нумерацией столбцов от 1 до 16
                if not recording:
                    # Проверка на пустую строку
                    if row.isnull().all():
                        continue  # Пропускаем пустые строки

                    # Проверяем, что первые 16 ячеек содержат именно последовательность чисел от 1 до 16
                    actual_sequence = [str(cell).strip() for cell in row[:16] if pd.notna(cell)]
                    print(f"actual_sequence: {actual_sequence}")
                    print(f"expected_sequence: {expected_sequence}")
                    if actual_sequence == expected_sequence:
                        recording = True
                        print(f"Начало записи данных с индекса строки: {index}")
                        continue

                # Используем регулярное выражение для поиска ключевой строки
                if isinstance(row.iloc[5], str) and re.search(r'Итого', row.iloc[5].strip(), re.IGNORECASE):
                    print(f"Нашли нужную строку: {index}")
                    # Если строка соответствует шаблону "Итого", сохраняем все накопленные данные в базу
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
                            print(f"Данные записаны в БД для {len(rows_to_insert)} строк.")
                            rows_to_insert = []  # Очищаем список после записи
                        except Exception as e:
                            print(f"Ошибка при сохранении данных в БД: {e}")
                    continue  # Переходим к следующей строке

                if recording:                    
                    try:
                        # Создаем словарь для каждой строки затрат
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
                        print(f"Нашли нужную строку: {rows_to_insert}")
                    except Exception as e:
                        print(f"Ошибка при сохранении данных в БД: {e}")

        except Exception as e:
            print(f"Ошибка на строке {index}: {e}")                  

        messages.success(request, "Данные успешно загружены в базу данных.")
        return redirect('myapp:start')
    else:
        print(f'Файла нет')
        return redirect('myapp:start')
    
# Связывание
def add_UNC_CCR(request):
    # Шаг 1: Загрузка всех ключевых слов из справочника
    key_phrases = ExpensesToEpcMap.objects.all()

    # Шаг 2: Проход по записям TempTableUNC и определение ключевых слов
    unc_keyword_map = {}
    for unc_record in TempTableUNC.objects.all():
        matching_keywords = []
        for key_phrase in key_phrases:
            if key_phrase.expenses_to_epc_map_epc.lower() in unc_record.name_unc.lower():
                matching_keywords.append(key_phrase.expenses_to_epc_map_name)
        
        if matching_keywords:
            unc_keyword_map[unc_record] = matching_keywords

    # Шаг 3: Проход по записям TempTable и поиск соответствий
    for unc_record, keywords in unc_keyword_map.items():
        for keyword in keywords:
            for temp_record in TempTable.objects.filter(expenses_name__icontains=keyword.lower()):
                # Шаг 4: Сохранение результата в TempTableССКUNC
                TempTableССКUNC.objects.create(
                    temp_table_id=temp_record,
                    temp_table_unc_id=unc_record,
                    matched_keyword=keyword,
                    additional_info=f"Связь по ключевому слову: {keyword}"
                )

    return redirect('myapp:CCP_UNC_page')
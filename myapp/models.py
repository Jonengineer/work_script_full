from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    # Добавьте любые дополнительные поля, если необходимо
    pass

class DictExpenditure(models.Model):
    dict_expenditure_id = models.AutoField(primary_key=True)
    dict_expense_type_id = models.IntegerField(null=True, blank=True)
    dict_expenditure_name = models.TextField(null=False, blank=False)

    class Meta:
        db_table = 'dict_expenditures'

class ExpensesToEpcMap(models.Model):
    expenses_to_epc_map_id = models.AutoField(primary_key=True)
    expenses_to_epc_map_nme = models.TextField(null=False, blank=False)
    expenses_to_epc_map_epc = models.TextField(null=False, blank=False)
    expenses_to_epc_number = models.IntegerField(null=False, blank=False)  
    expenses_to_epc_voltage_marker = models.IntegerField(null=True, blank=True)
    expenses_to_epc_type = models.IntegerField(null=False, blank=False)  

    class Meta:
        db_table = 'expenses_to_epc_map'

class DictSecChapter(models.Model):
    dict_sec_chapter_id = models.AutoField(primary_key=True)
    dict_sec_chapter_name = models.TextField()

    class Meta:
        db_table = 'dict_sec_chapters'

class TempTable(models.Model):
    id = models.AutoField(primary_key=True)
    project_id = models.TextField()
    chapter_id = models.ForeignKey('DictSecChapter', on_delete=models.CASCADE)
    object_costEstimate_id = models.TextField(null=True, blank=True)
    local_costEstimate_id = models.TextField(null=True, blank=True)
    expenses_name = models.TextField()
    quarter = models.TextField(null=True, blank=True)    
    # Поля для различных типов стоимости
    construction_cost = models.TextField(null=True, blank=True, verbose_name="Стоимость строительных работ")
    installation_cost = models.TextField(null=True, blank=True, verbose_name="Стоимость монтажных работ")
    equipment_cost = models.TextField(null=True, blank=True, verbose_name="Стоимость оборудования, мебели, инвентаря")
    other_cost = models.TextField(null=True, blank=True, verbose_name="Стоимость прочих затрат")
    total_cost = models.TextField(null=True, blank=True, verbose_name="Общая сметная стоимость")

    class Meta:
        db_table = 'temp_table'

class TempTableUNC(models.Model):
    id = models.AutoField(primary_key=True)
    project_id = models.TextField()
    project_name = models.TextField()
    name_unc = models.TextField()
    name_object = models.TextField()
    voltage = models.TextField()
    TX = models.TextField()
    count = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit = models.TextField()
    unc_code = models.TextField()
    
    class Meta:
        db_table = 'temp_table_unc'       

class TempTableLocal(models.Model):
    parsed_local_estimate_id = models.AutoField(primary_key=True)  # Основной ключ
    temp_table = models.ForeignKey('TempTable', on_delete=models.CASCADE, related_name='parsed_data')  # Связь с таблицей TempTable
    row_number = models.IntegerField(verbose_name="Номер строки")  # Поле для хранения номера строки из TempTable
    row_data = models.JSONField(verbose_name="Данные строки в формате JSON")  # Поле для хранения данных строки в формате JSON

    class Meta:
        db_table = 'temp_table_local'
        verbose_name = 'Данные парсинга локальной сметы'
        verbose_name_plural = 'Данные парсинга локальных смет'

    def __str__(self):
        return f"Parsed Data ID: {self.parsed_local_estimate_id} - (Строка: {self.row_number})"

class TempTableССКUNC(models.Model):
    id = models.AutoField(primary_key=True)
    temp_table_id = models.ForeignKey(TempTable, on_delete=models.CASCADE)
    temp_table_unc_id = models.ForeignKey(TempTableUNC, on_delete=models.CASCADE)
    key_id = models.ForeignKey('ExpensesToEpcMap', on_delete=models.CASCADE)
    matched_keyword = models.TextField()  # Ключевое слово, по которому произошло связывание
    additional_info = models.TextField(null=True, blank=True)  # Дополнительная информация о связывании

    class Meta:
        db_table = 'temp_table_cck_unc'

class ObjectAnalog(models.Model):
    id = models.AutoField(primary_key=True)
    project_id = models.TextField()
    project_name = models.TextField()
    chapter_id = models.ForeignKey('DictSecChapter', on_delete=models.CASCADE)
    object_costEstimate_id = models.TextField()
    local_costEstimate_id = models.TextField()
    expenses_name = models.TextField()
    quarter = models.TextField()
    construction_cost = models.TextField(null=True, blank=True, verbose_name="Стоимость строительных работ")
    installation_cost = models.TextField(null=True, blank=True, verbose_name="Стоимость монтажных работ")
    equipment_cost = models.TextField(null=True, blank=True, verbose_name="Стоимость оборудования, мебели, инвентаря")
    other_cost = models.TextField(null=True, blank=True, verbose_name="Стоимость прочих затрат")
    total_cost = models.TextField(null=True, blank=True, verbose_name="Общая сметная стоимость")    
    unc_code = models.TextField()
    name_unc = models.TextField()
    name_object = models.TextField()
    voltage = models.TextField()
    TX = models.TextField()
    count = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit = models.TextField()
    matched_keyword = models.TextField()  # Ключевое слово, по которому произошло связывание
    additional_info = models.TextField(null=True, blank=True)  # Дополнительная информация о связывании
    key_id = models.ForeignKey('ExpensesToEpcMap', on_delete=models.CASCADE, null=True, blank=True)
    is_check = models.BooleanField(default=False, verbose_name="Проверено")
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'object_analog'

class InvestProject(models.Model):
    # Поля модели
    invest_project_id = models.AutoField(primary_key=True)
    dict_project_type_id = models.IntegerField()  # DictKey equivalent
    dict_project_status_id = models.IntegerField()  # DictKey equivalent
    summary_estimate_calculation_id = models.IntegerField(null=True)
    invest_project_type = models.IntegerField()
    invest_project_mrid = models.CharField(max_length=36, null=True) 
    invest_project_version = models.IntegerField(null=True)  # Version equivalent
    invest_project_unc_forecast = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Price equivalent
    invest_project_create_dttm = models.DateTimeField(null=True)  # DateTimeDomain equivalent
    invest_project_update_dttm = models.DateTimeField(null=True)  # DateTimeDomain equivalent
    invest_project_group_number = models.TextField(null=True)  # TEXT equivalent
    invest_project_stage = models.TextField(null=True)  # TEXT equivalent
    invest_project_is_analogue = models.BooleanField(null=True)  # Flag equivalent
    invest_project_shortname = models.CharField(max_length=255, null=True)  # PersonName equivalent    
    invest_project_begindate = models.DateTimeField(null=True)  # DateTimeDomain equivalent
    invest_project_enddate = models.DateTimeField(null=True)  # DateTimeDomain equivalent
    invest_project_description = models.TextField(null=True)  # LONG_NAME equivalent
    invest_project_fullname = models.TextField()
    invest_project_code = models.TextField()
    invest_project_ptk_id = models.UUIDField(default=uuid.uuid4, editable=False)  # Unique project identifier, используется UUID для уникальности
    invest_project_titul_pir = models.BooleanField(default=False)  # Флаг
    invest_project_auto_bs = models.BooleanField(default=False)  # Флаг
    invest_project_auto_pir = models.BooleanField(default=False)  # Флаг

    class Meta:
        db_table = 'invest_project'
        verbose_name = 'Инвестиционный проект'
        verbose_name_plural = 'Инвестиционные проекты'

    def __str__(self):
        return f"Invest Project ID: {self.invest_project_id}"

class Object(models.Model):
    object_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    invest_project = models.ForeignKey('InvestProject', on_delete=models.CASCADE)  # Связь с моделью InvestProject
    object_type_id = models.IntegerField()  # DictKey, не может быть null
    dict_region_id = models.IntegerField(null=True)  # DictKey, может быть null
    dict_work_type_id = models.IntegerField()  # DictKey, не может быть null
    dict_substaion_type_id = models.IntegerField(null=True)  # DictKey, может быть null
    start_up_complex_id = models.IntegerField(null=True)  # INT4, может быть null
    dict_regions_economic_zone_id = models.IntegerField(null=True)  # DictKey, может быть null
    object_name = models.CharField(max_length=255)  # NameDomain, not null
    object_mrid = models.UUIDField()  # UUIDDomain, not null
    object_is_analogue = models.BooleanField(null=True)  # BOOL, может быть null
    object_create_dttm = models.DateTimeField(null=True)  # TIMESTAMP WITH TIME ZONE, может быть null
    object_update_dttm = models.DateTimeField(null=True)  # TIMESTAMP WITH TIME ZONE, может быть null
    object_calc_type = models.TextField(null=True)  # TEXT, может быть null

    class Meta:
        db_table = 'object'
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'

    def __str__(self):
        return f"Object ID: {self.object_id} - {self.object_name}"

class EpcCalculation(models.Model):
    epc_calculation_ind = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    object_id = models.ForeignKey('Object', on_delete=models.CASCADE, related_name='epc_calculations', null=True)  # Внешний ключ на Object, может быть null
    epc_calculation_mrid = models.UUIDField()  # UUIDDomain, not null
    epc_calculation_before_ded = models.BooleanField()  # Flag, not null
    epc_calculation_link_ptk = models.TextField(null=True)  # TEXT, может быть null

    class Meta:
        db_table = 'epc_calculation'
        verbose_name = 'Расчет УНЦ'
        verbose_name_plural = 'Расчеты УНЦ'

    def __str__(self):
        return f"EPC Calculation ID: {self.epc_calculation_ind} - Object ID: {self.object_id}"

class AtypicalExpenses(models.Model):
    atypical_expenses_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    dict_atypical_expenses_id = models.IntegerField(null=True)  # DictKey, может быть null
    epc_calculation_ind = models.ForeignKey('EpcCalculation', on_delete=models.CASCADE, null=True)  # Внешний ключ на EpcCalculation, может быть null

    class Meta:
        db_table = 'atypical_expenses'
        verbose_name = 'Ненормированные затраты'
        verbose_name_plural = 'Ненормированные затраты'

class EpcCosts(models.Model):
    epc_costs_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    epc_calculation_ind = models.ForeignKey('EpcCalculation', on_delete=models.CASCADE, null=True)  # Внешний ключ на EpcCalculation, может быть null
    dict_cost_epc_id = models.IntegerField(null=True)  # DictKey, идентификатор расценки УНЦ
    dict_cost_epc_table_id = models.IntegerField(null=True)  # DictKey, идентификатор таблицы УНЦ
    equipment_parameter_id = models.IntegerField(null=True)  # INT4, идентификатор оборудования
    epc_costs_id_name = models.CharField(max_length=255, null=True)  # NameDomain, может быть null
    epc_costs_description = models.TextField(null=True, blank=True)  # LONG_NAME, может быть null
    epc_costs_checked = models.BooleanField(default=False, verbose_name="Проверено")  # Flag, может быть null
    object = models.ForeignKey('Object', on_delete=models.CASCADE)  # Связь с моделью Object
    name_object = models.TextField()
    voltage = models.TextField()
    TX = models.TextField()
    count = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit = models.TextField()
    code = models.TextField()

    class Meta:
        db_table = 'epc_costs'
        verbose_name = 'Расценка УНЦ'
        verbose_name_plural = 'Расценки УНЦ'

    def __str__(self):
        return f"EpcCosts ID: {self.epc_costs_id} - Object ID: {self.object.object_id}"

class ExpensesByEpc(models.Model):
    expenses_by_epc_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    epc_costs_id = models.ForeignKey('EpcCosts', on_delete=models.CASCADE)  # Внешний ключ на EpcCosts, не может быть null
    dict_typical_epc_work_id = models.IntegerField(null=True)  # DictKey, может быть null
    dict_budgeting_id = models.IntegerField(null=True)  # DictKey, может быть null
    expense_id = models.ForeignKey('Expenses', on_delete=models.CASCADE)  # Внешний ключ на Expenses, не может быть null
    expenses_to_epc_map_id = models.ForeignKey('ExpensesToEpcMap', on_delete=models.CASCADE)  # Внешний ключ на ExpensesToEpcMap, не может быть null
    expenses_by_epc_nme = models.CharField(max_length=255, null=True)  # NameDomain, может быть null
    expenses_by_epc_descr = models.TextField(null=True, blank=True)  # LONG_NAME, может быть null
    expenses_by_epc_checked = models.BooleanField(default=False, verbose_name="Проверено")  # Flag, не может быть null
    expenses_by_epc_cost = models.DecimalField(max_digits=12, decimal_places=2)  # Price, not null

    class Meta:
        db_table = 'expenses_by_epc'
        verbose_name = 'Затраты по УНЦ'
        verbose_name_plural = 'Затраты по УНЦ'

    def __str__(self):
        return f"ExpensesByEpc ID: {self.expenses_by_epc_id} - {self.expenses_by_epc_nme}"

class SummaryEstimateCalculation(models.Model):
    summary_estimate_calculation_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    invest_project_id = models.ForeignKey('InvestProject', on_delete=models.CASCADE, null=True)  # Может быть null, согласно SQL-схеме
    sum_est_calc_mrid = models.UUIDField()  # UUIDDomain, обязательное поле
    sum_est_calc_before_ded = models.BooleanField()  # Flag, обязательное поле

    class Meta:
        db_table = 'summary_estimate_calculation'
        verbose_name = 'Сводная смета расчета'
        verbose_name_plural = 'Сводные сметы расчетов'

    def __str__(self):
        return f"Summary Estimate Calculation ID: {self.summary_estimate_calculation_id} - Project ID: {self.invest_project_id}"

class ObjectCostEstimate(models.Model):
    object_cost_estimate_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    summary_estimate_calculation_id = models.ForeignKey('SummaryEstimateCalculation', on_delete=models.CASCADE, null=True)  # Может быть null, согласно SQL-схеме
    object_cost_estimate_code = models.CharField(max_length=255)

    class Meta:
        db_table = 'object_cost_estimates'
        verbose_name = 'Объектная смета'
        verbose_name_plural = 'Объектные сметы'

    def __str__(self):
        return f"Object Cost Estimate ID: {self.object_cost_estimate_id} - Summary Estimate Calculation ID: {self.summary_estimate_calculation_id}"

class LocalCostEstimate(models.Model):
    local_cost_estimate_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    object_cost_estimate_id = models.ForeignKey('ObjectCostEstimate', on_delete=models.CASCADE, null=True, blank=True)  # Может быть null
    summary_estimate_calculation_id = models.ForeignKey('SummaryEstimateCalculation', on_delete=models.CASCADE, null=True)  # Может быть null
    local_cost_estimate_code = models.CharField(max_length=255)

    class Meta:
        db_table = 'local_cost_estimates'
        verbose_name = 'Локальная смета'
        verbose_name_plural = 'Локальные сметы'

    def __str__(self):
        return f"Local Cost Estimate ID: {self.local_cost_estimate_id}"

class LocalEstimateData(models.Model):
    local_estimate_data_id = models.AutoField(primary_key=True)  # Основной ключ
    local_cost_estimate_id = models.ForeignKey('LocalCostEstimate', on_delete=models.CASCADE, related_name='parsed_data', null=True)  # Может быть null
    local_estimate_data_rn = models.IntegerField(verbose_name="Номер строки", null=True)  # Поле может быть null
    local_estimate_row_data = models.JSONField(verbose_name="Данные строки в формате JSON", null=True)  # Поле может быть null

    class Meta:
        db_table = 'local_estimates_data'
        verbose_name = 'Данные парсинга локальной сметы'
        verbose_name_plural = 'Данные парсинга локальных смет'

    def __str__(self):
        return f"Parsed Data ID: {self.local_estimate_data_id} - {self.local_cost_estimate_id.local_cost_estimate_code} (Строка: {self.local_estimate_data_rn})"

class LocalEstimateDataSort(models.Model):
    sort_local_estimate_id = models.AutoField(primary_key=True)  # Основной ключ
    local_cost_estimate = models.ForeignKey('LocalCostEstimate', on_delete=models.CASCADE, related_name='estimate_sort_data')  # Связь с локальной сметой
    local_estimate_data_code = models.TextField(null=True)
    local_estimate_data_part = models.TextField(null=True)
    local_estimate_data_name = models.TextField(null=True)
    local_estimate_data_type = models.TextField(null=True)
    local_estimate_data_type_code = models.TextField(null=True)
    local_estimate_data_unit = models.TextField(null=True)
    local_estimate_data_count = models.TextField(null=True)

    class Meta:
        db_table = 'local_estimate_data_sort'
        verbose_name = 'Данные сортировки локальной сметы'
        verbose_name_plural = 'Данные сортировки локальных смет'

    def __str__(self):
        return f"Parsed Data ID: {self.sort_local_estimate_id} - {self.local_cost_estimate.local_cost_estimate_code})"

class Expenses(models.Model):
    expense_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    local_cost_estimate_id = models.ForeignKey('LocalCostEstimate', on_delete=models.CASCADE, null=True, blank=True)  # Может быть null
    object_cost_estimate_id = models.ForeignKey('ObjectCostEstimate', on_delete=models.CASCADE, null=True, blank=True)  # Может быть null
    summary_estimate_calculation_id = models.ForeignKey('SummaryEstimateCalculation', on_delete=models.CASCADE, null=True)  # Может быть null
    dict_expenditure_id = models.IntegerField(null=True)  # DictKey, может быть null
    dict_sec_chapter_id = models.ForeignKey('DictSecChapter', on_delete=models.CASCADE, null=True)  # DictKey, может быть null
    expense_value = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # Price
    expense_nme = models.CharField(max_length=255, null=True)  # NameDomain, может быть null
    expense_qarter = models.TextField(null=True)  # TEXT, квартал, может быть null
    expense_construction_cost = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Стоимость строительных работ")  # Price
    expense_installation_cost = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Стоимость монтажных работ")  # Price
    expense_equipment_cost = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Стоимость оборудования, мебели, инвентаря")  # Price
    expense_other_cost = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Стоимость прочих затрат")  # Price
    expense_total = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Общая сметная стоимость")  # Price
    expense_description = models.TextField(null=True, blank=True)  # LONG_NAME, может быть null
    expense_checked = models.BooleanField(default=False, verbose_name="Проверено", null=True, blank=True)  # Flag


    class Meta:
        db_table = 'expenses'
        verbose_name = 'Затрата'
        verbose_name_plural = 'Затраты'

    def __str__(self):
        return f"Expense ID: {self.expense_id} - {self.expense_nme}"

# ТХ
class TechicalPlace(models.Model):
    technical_place_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    dict_voltage_id = models.IntegerField(null=True, blank=True)  # DictKey, может быть null
    object_id = models.IntegerField(null=False)  # INT4, не может быть null
    dict_technical_place_type_id = models.IntegerField(null=False)  # DictKey, не может быть null
    tec_technical_place_id = models.IntegerField(null=True, blank=True)  # INT4, может быть null
    technical_place_name = models.CharField(max_length=255)  # NameDomain, не может быть null
    technical_place_mrid = models.UUIDField(default=uuid.uuid4, editable=False)  # UUIDDomain, не может быть null
    technical_place_create_dttm = models.DateTimeField(auto_now_add=True, null=True)  # TimestampDomain, может быть null
    technical_place_update_dttm = models.DateTimeField(auto_now=True, null=True)  # TimestampDomain, может быть null
    technical_place_order_number = models.IntegerField(null=True, blank=True)  # INT4, может быть null

    class Meta:
        db_table = 'techical_place'
        verbose_name = 'Техническое место'
        verbose_name_plural = 'Технические места'
    
    def __str__(self):
        return f"{self.technical_place_name} ({self.technical_place_mrid})"

class Equipment(models.Model):
    equipment_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    technical_place_id = models.IntegerField(null=False)  # INT4, не может быть null
    dict_equipment_type_id = models.IntegerField(null=False)  # DictKey, не может быть null
    equ_equipment_id = models.IntegerField(null=True, blank=True)  # INT4, может быть null
    equipment_name = models.CharField(max_length=255)  # NameDomain, не может быть null
    equipment_count = models.IntegerField(null=True, blank=True)  # INT4, может быть null
    equipment_is_autogen = models.BooleanField(default=False, null=True)  # BOOL, может быть null
    equipment_price_unc = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)  # Price, может быть null
    equipment_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)  # Price, может быть null
    equipment_mrid = models.UUIDField(default=uuid.uuid4, editable=False)  # UUIDDomain, не может быть null
    equipment_order_number = models.IntegerField(null=True, blank=True)  # INT4, может быть null

    class Meta:
        db_table = 'equipment'
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'

    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_mrid})"

class EquipmentParameters(models.Model):
    equipment_parameter_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    equipment_id = models.IntegerField(null=False)  # INT4, не может быть null
    dict_equipment_parameter_id = models.IntegerField(null=False)  # DictKey, не может быть null
    equipment_parameter_val = models.TextField(null=True, blank=True)  # LONG_NAME, может быть null
    equipment_parameter_mrid = models.UUIDField(default=uuid.uuid4, editable=False)  # UUIDDomain, не может быть null
    equipment_parameter_create_dttm = models.DateTimeField(auto_now_add=True, null=True)  # DateTimeDomain, может быть null
    equipment_parameter_update_dttm = models.DateTimeField(auto_now=True, null=True)  # DateTimeDomain, может быть null

    class Meta:
        db_table = 'equipment_parameters'
        verbose_name = 'Параметр оборудования'
        verbose_name_plural = 'Параметры оборудования'

    def __str__(self):
        return f"Parameter {self.equipment_parameter_id} for Equipment ID {self.equipment_id}"

class DictTechnicalPlaceTypes(models.Model):
    dict_technical_place_type_id = models.AutoField(primary_key=True)  # DictKey, основной ключ
    dict_tech_place_type_id = models.IntegerField(null=True, blank=True)  # DictKey, может быть null
    object_type_id = models.IntegerField(null=True, blank=True)  # DictKey, может быть null
    dict_technical_place_type_name = models.CharField(max_length=255)  # NameDomain, не может быть null
    dict_tech_place_typ_nme_lvl = models.IntegerField(null=True, blank=True)  # DictKey, может быть null
    dict_tech_place_typ_full_nme = models.TextField(null=True, blank=True)  # LONG_NAME, может быть null

    class Meta:
        db_table = 'dict_technical_place_types'
        verbose_name = 'Тип технического места'
        verbose_name_plural = 'Типы технических мест'

    def __str__(self):
        return self.dict_technical_place_type_name

class DictVoltages(models.Model):
    dict_voltage_id = models.AutoField(primary_key=True)  # DictKey, основной ключ
    dict_voltage_name = models.CharField(max_length=255) 

    class Meta:
        db_table = 'dict_voltages'
        verbose_name = 'Вольтаж'
        verbose_name_plural = 'Вольтажи'

    def __str__(self):
        return self.dict_voltage_name

class DictEquipmentType(models.Model):
    dict_equipment_type_id = models.AutoField(primary_key=True)  # DictKey, основной ключ
    dict_equipment_type_name = models.CharField(max_length=255)  # NameDomain, не может быть null
    dict_equipment_type_is_hidden = models.BooleanField(default=False, null=True)  # BOOL, может быть null

    class Meta:
        db_table = 'dict_equipment_types'
        verbose_name = 'Тип оборудования'
        verbose_name_plural = 'Типы оборудования'

    def __str__(self):
        return self.dict_equipment_type_name

class TechPlaceEquipTypeLink(models.Model):
    dict_technical_place_type_id = models.IntegerField(null=False)  # DictKey, не может быть null
    dict_equipment_type_id = models.IntegerField(null=False)  # DictKey, не может быть null

    class Meta:
        db_table = 'tech_place_equip_type_link'
        verbose_name = 'Тип технического места и оборудования'
        verbose_name_plural = 'Типы технического места и оборудования'

    def __str__(self):
        return f"Technical Place Type ID: {self.dict_technical_place_type_id}, Equipment Type ID: {self.dict_equipment_type_id}"

class EquipmentTypeConsistsOf(models.Model):
    dic_dict_equipment_type_id = models.IntegerField(null=False)  # DictKey, не может быть null
    dict_equipment_type_id = models.IntegerField(null=False)  # DictKey, не может быть null

    class Meta:
        db_table = 'equipmentTypeConsistsOf'
        verbose_name = 'Связь типов оборудования'
        verbose_name_plural = 'Связи типов оборудования'
        constraints = [
            models.UniqueConstraint(fields=['dic_dict_equipment_type_id', 'dict_equipment_type_id'], name='pk_equipment_type_consists_of')
        ]

    def __str__(self):
        return f"Relation: {self.dic_dict_equipment_type_id} - {self.dict_equipment_type_id}"

class EquipmentTypeHasParameters(models.Model):
    dict_equipment_parameter_id = models.IntegerField(null=False)  # DictKey, не может быть null
    dict_equipment_type_id = models.IntegerField(null=False)  # DictKey, не может быть null

    class Meta:
        db_table = 'equipmentTypeHasParameters'
        verbose_name = 'Тип параметра оборудования'
        verbose_name_plural = 'Типы параметров оборудования'
        constraints = [
            models.UniqueConstraint(fields=['dict_equipment_parameter_id', 'dict_equipment_type_id'], name='pk_equipment_type_has_parameters')
        ]

    def __str__(self):
        return f"Equipment Type: {self.dict_equipment_type_id}, Parameter Type: {self.dict_equipment_parameter_id}"

class DictEquipmentParameterAllowedValue(models.Model):
    dict_equip_param_allowed_id = models.AutoField(primary_key=True)  # DictKey, основной ключ
    dict_equipment_parameter_id = models.IntegerField(null=False)  # DictKey, не может быть null
    dict_unit_id = models.IntegerField(null=True, blank=True)  # DictKey, может быть null
    dict_equip_param_allowed_val = models.TextField(null=False, blank=True)  # LONG_NAME, не может быть null
    dict_equip_param_a_min_val = models.CharField(max_length=2000, null=True, blank=True)  # VARCHAR(2000), может быть null
    dict_equip_param_a_max_val = models.CharField(max_length=2000, null=True, blank=True)  # VARCHAR(2000), может быть null

    class Meta:
        db_table = 'dict_equip_param_allowed_value'
        verbose_name = 'Допустимое значение параметра оборудования'
        verbose_name_plural = 'Допустимые значения параметров оборудования'

    def __str__(self):
        return f"Parameter ID: {self.dict_equipment_parameter_id}, Allowed Value: {self.dict_equip_param_allowed_val}"

class DictEquipmentParameters(models.Model):
    dict_equipment_parameter_id = models.IntegerField(null=False)  # DictKey, не может быть null
    dict_unit_id = models.IntegerField(null=True, blank=True)  # DictKey, может быть null
    dict_unit_multiplier_id = models.IntegerField(null=True, blank=True)  # DictKey, может быть null
    dict_equipment_parameter_name = models.CharField(max_length=255, null=True, blank=True)  # NameDomain, может быть null
    dict_equip_par_descr = models.TextField(null=True, blank=True)  # LONG_NAME, может быть null
    dict_equipment_parameters_code = models.CharField(max_length=255, null=True, blank=True)  # PersonName, может быть null
    dict_equip_par_is_min_max = models.BooleanField(default=False)  # Flag, может быть null

    class Meta:
        db_table = 'dict_equipment_parameters'
        verbose_name = 'Параметр оборудования'
        verbose_name_plural = 'Параметры оборудования'

    def __str__(self):
        return f"{self.dict_equipment_parameter_name} ({self.dict_equipment_parameter_id})"
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    # Добавьте любые дополнительные поля, если необходимо
    pass

class DictExpenditure(models.Model):
    dict_expenditure_id = models.AutoField(primary_key=True)
    dict_expense_type_id = models.IntegerField()
    dict_expenditure_name = models.TextField()

    class Meta:
        db_table = 'dict_expenditure'

class ExpensesToEpcMap(models.Model):
    expenses_to_epc_map_id = models.AutoField(primary_key=True)
    expenses_to_epc_map_name = models.TextField()
    expenses_to_epc_map_epc = models.TextField()

    class Meta:
        db_table = 'expenses_to_epc_map'

        
class DictSecChapter(models.Model):
    dict_sec_chapter_id = models.AutoField(primary_key=True)
    dict_sec_chapter_name = models.TextField()

    class Meta:
        db_table = 'dict_sec_chapter'

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
    project_name = models.TextField()
    project_code = models.TextField()
    dict_project_type_id = models.IntegerField(null=True)  
    dict_project_status_id = models.IntegerField(null=True)  
    invest_project_type = models.IntegerField(null=True)  
    invest_project_mrid = models.CharField(max_length=36, null=True)  
    invest_project_version = models.IntegerField(null=True)  
    invest_project_unc_forecast = models.DecimalField(max_digits=10, decimal_places=2, null=True)  
    invest_project_create_dttm = models.DateTimeField(null=True)  
    invest_project_update_dttm = models.DateTimeField(null=True)  


    class Meta:
        db_table = 'invest_project'
        verbose_name = 'Инвестиционный проект'
        verbose_name_plural = 'Инвестиционные проекты'

    def __str__(self):
        return f"Invest Project ID: {self.invest_project_id}"

class Object(models.Model):
    # Поля модели
    object_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    invest_project = models.ForeignKey(InvestProject, on_delete=models.CASCADE)  # Связь с моделью InvestProject
    object_type_id = models.IntegerField(null=True)  # INT4, не может быть null
    dict_region_id = models.IntegerField(null=True)  # INT4, может быть null
    dict_work_type_id = models.IntegerField(null=True)  # INT4, не может быть null
    dict_substaion_type_id = models.IntegerField(null=True)  # INT4, может быть null
    start_up_complex_id = models.IntegerField(null=True)  # INT4, может быть null
    dict_regions_economic_zone_id = models.IntegerField(null=True)  # INT4, может быть null
    object_name = models.TextField(null=True)  # TEXT, название объекта, может быть null
    object_mrid = models.CharField(max_length=36, null=True)  # CHAR(36), UUID, может быть null
    object_is_analogue = models.BooleanField(null=True)  # BOOL, является объектом-аналогом, может быть null
    object_create_dttm = models.DateTimeField(null=True)  # TIMESTAMP WITH TIME ZONE, дата создания объекта, может быть null
    object_update_dttm = models.DateTimeField(null=True)  # TIMESTAMP WITH TIME ZONE, дата обновления объекта, может быть null

    class Meta:
        db_table = 'object'
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'

    def __str__(self):
        return f"Object ID: {self.object_id} - {self.object_name}"
    
class EpcCalculation(models.Model):
    epc_calculation_ind = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name='epc_calculations')  # Внешний ключ на Object
    epc_calculation_mrid = models.CharField(max_length=36, null=True)  # CHAR(36), UUID, может быть null
    epc_calculation_before_ded = models.BooleanField(null=True)  # BOOL, флаг "УНЦ до ПСД", может быть null

    class Meta:
        db_table = 'epc_calculation'
        verbose_name = 'Расчет УНЦ'
        verbose_name_plural = 'Расчеты УНЦ'

    def __str__(self):
        return f"EPC Calculation ID: {self.epc_calculation_ind} - Object ID: {self.object_id}"
    
class AtypicalExpenses(models.Model):
    atypical_expenses_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    dict_atypical_expenses_id = models.IntegerField(null=True)  # INT4, ключ справочника не типовых работ
    object = models.ForeignKey(Object, on_delete=models.CASCADE)  # Внешний ключ на Object
    epc_calculation = models.ForeignKey(EpcCalculation, on_delete=models.CASCADE)  # Внешний ключ на EpcCalculation

    class Meta:
        db_table = 'atypical_expenses'
        verbose_name = 'Ненормированные затраты'
        verbose_name_plural = 'Ненормированные затраты'

    def __str__(self):
        return f"Atypical Expenses ID: {self.atypical_expenses_id} - Object ID: {self.object.object_id}"

class EpcCosts(models.Model):
    epc_costs_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    object = models.ForeignKey('Object', on_delete=models.CASCADE)  # Связь с моделью Object
    epc_calculation = models.ForeignKey('EpcCalculation', on_delete=models.CASCADE)  # Связь с моделью EpcCalculation
    dict_cost_epc_id = models.TextField() # INT4, идентификатор расценки УНЦ
    dict_cost_epc_table_id = models.IntegerField(null=True)  # INT4, идентификатор таблицы УНЦ
    name_unc = models.TextField()
    name_object = models.TextField()
    voltage = models.TextField()
    TX = models.TextField()
    count = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unit = models.TextField()
    is_check = models.BooleanField(default=False, verbose_name="Проверено")
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'epc_costs'
        verbose_name = 'Расценка УНЦ'
        verbose_name_plural = 'Расценки УНЦ'

    def __str__(self):
        return f"EpcCosts ID: {self.epc_costs_id} - Object ID: {self.object.object_id}"

class ExpensesByEpc(models.Model):
    expenses_by_epc_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    epc_costs_id = models.ForeignKey('EpcCosts', on_delete=models.CASCADE)  # Связь с моделью EpcCalculation  # INT4, идентификатор расценок УНЦ, не может быть null
    dict_typical_epc_work_id = models.IntegerField(null=True)  # INT4, идентификатор типовой работы по УНЦ, не может быть null
    dict_budgeting_id = models.IntegerField(null=True)  # INT4, ключ типа бюджетирования, не может быть null
    expense_id =models.ForeignKey('Expenses', on_delete=models.CASCADE)  # INT4, идентификатор затраты, не может быть null
    expenses_to_epc_map_id = models.ForeignKey('ExpensesToEpcMap', on_delete=models.CASCADE)  # INT4, идентификатор мапинга, не может быть null
    expenses_by_epc_nme = models.TextField(null=True)  # TEXT, наименование затраты УНЦ, может быть null
    is_check = models.BooleanField(default=False, verbose_name="Проверено", null=True, blank=True)
    description = models.TextField(null=True, blank=True)


    class Meta:
        db_table = 'expenses_by_epc'
        verbose_name = 'Затраты по УНЦ'
        verbose_name_plural = 'Затраты по УНЦ'

    def __str__(self):
        return f"ExpensesByEpc ID: {self.expenses_by_epc_id} - {self.expenses_by_epc_nme}"
    
class SummaryEstimateCalculation(models.Model):
    summary_estimate_calculation_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    invest_project = models.ForeignKey(InvestProject, on_delete=models.CASCADE)
    sum_est_calc_mrid = models.CharField(max_length=36, null=True)  # CHAR(36), mRID ССР, может быть null
    sum_est_calc_before_ded = models.BooleanField(null=True)  # BOOL, ССР до ПСД, может быть null

    class Meta:
        db_table = 'summary_estimate_calculation'
        verbose_name = 'Сводная смета расчета'
        verbose_name_plural = 'Сводные сметы расчетов'

    def __str__(self):
        return f"Summary Estimate Calculation ID: {self.summary_estimate_calculation_id} - Project ID: {self.invest_project_id}"
    
class ObjectCostEstimate(models.Model):
    object_cost_estimate_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    summary_estimate_calculation = models.ForeignKey('SummaryEstimateCalculation', on_delete=models.CASCADE)  # Связь с моделью SummaryEstimateCalculation
    object_cost_estimate_code = models.TextField()
    class Meta:
        db_table = 'object_cost_estimates'
        verbose_name = 'Объектная смета'
        verbose_name_plural = 'Объектные сметы'

    def __str__(self):
        return f"Object Cost Estimate ID: {self.object_cost_estimate_id} - Summary Estimate Calculation ID: {self.summary_estimate_calculation.summary_estimate_calculation_id}"
    
class LocalCostEstimate(models.Model):
    local_cost_estimate_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    object_cost_estimate = models.ForeignKey('ObjectCostEstimate', on_delete=models.CASCADE, null=True, blank=True)  # Связь с моделью ObjectCostEstimate
    summary_estimate_calculation = models.ForeignKey('SummaryEstimateCalculation', on_delete=models.CASCADE)  # Связь с моделью SummaryEstimateCalculation
    local_cost_estimate_code = models.TextField()

    class Meta:
        db_table = 'local_cost_estimates'
        verbose_name = 'Локальная смета'
        verbose_name_plural = 'Локальные сметы'

    def __str__(self):
        return f"Local Cost Estimate ID: {self.local_cost_estimate_id}"

class Expenses(models.Model):
    expense_id = models.AutoField(primary_key=True)  # SERIAL, основной ключ
    local_cost_estimate = models.ForeignKey('LocalCostEstimate', on_delete=models.CASCADE, null=True, blank=True)  # Связь с моделью LocalCostEstimate
    object_cost_estimate = models.ForeignKey('ObjectCostEstimate', on_delete=models.CASCADE, null=True, blank=True)  # Связь с моделью ObjectCostEstimate
    summary_estimate_calculation = models.ForeignKey('SummaryEstimateCalculation', on_delete=models.CASCADE)  # Связь с моделью SummaryEstimateCalculation
    dict_expenditure_id = models.IntegerField(null=True)  # INT4, идентификатор статьи затрат, ключ справочника    
    expense_nme = models.TextField(null=True)  # TEXT, наименование затраты, может быть null
    quarter = models.TextField() # Квартал
    construction_cost = models.TextField(null=True, blank=True, verbose_name="Стоимость строительных работ")
    installation_cost = models.TextField(null=True, blank=True, verbose_name="Стоимость монтажных работ")
    equipment_cost = models.TextField(null=True, blank=True, verbose_name="Стоимость оборудования, мебели, инвентаря")
    other_cost = models.TextField(null=True, blank=True, verbose_name="Стоимость прочих затрат")
    total_cost = models.TextField(null=True, blank=True, verbose_name="Общая сметная стоимость")  
    chapter_id = models.ForeignKey('DictSecChapter', on_delete=models.CASCADE)
    is_check = models.BooleanField(default=False, verbose_name="Проверено", null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'expenses'
        verbose_name = 'Затрата'
        verbose_name_plural = 'Затраты'

    def __str__(self):
        return f"Expense ID: {self.expense_id} - {self.expense_nme}"
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    # Добавьте любые дополнительные поля, если необходимо
    pass

class SummaryEstimateCalculation(models.Model):
    summary_estimate_calculation_id = models.AutoField(primary_key=True)
    object_id = models.IntegerField()
    sum_est_calc_mrid = models.UUIDField(default=uuid.uuid4, editable=False)
    sum_est_calc_before_ded = models.BooleanField()

    class Meta:
        db_table = 'summary_estimate_calculation'

class ObjectCostEstimate(models.Model):
    object_cost_estimate_id = models.AutoField(primary_key=True)
    summary_estimate_calculation = models.ForeignKey(SummaryEstimateCalculation, on_delete=models.CASCADE)

    class Meta:
        db_table = 'object_cost_estimate'

class LocalCostEstimate(models.Model):
    local_cost_estimate_id = models.AutoField(primary_key=True)
    object_cost_estimate = models.ForeignKey(ObjectCostEstimate, on_delete=models.CASCADE)
    summary_estimate_calculation = models.ForeignKey(SummaryEstimateCalculation, on_delete=models.CASCADE)

    class Meta:
        db_table = 'local_cost_estimate'

class Expense(models.Model):
    expense_id = models.AutoField(primary_key=True)
    local_cost_estimate = models.ForeignKey(LocalCostEstimate, on_delete=models.CASCADE)
    object_cost_estimate = models.ForeignKey(ObjectCostEstimate, on_delete=models.CASCADE)
    summary_estimate_calculation = models.ForeignKey(SummaryEstimateCalculation, on_delete=models.CASCADE)
    dict_expenditure_id = models.IntegerField()
    expense_value = models.DecimalField(max_digits=10, decimal_places=2)
    expense_name = models.TextField()

    class Meta:
        db_table = 'expense'

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


class ExpensesByEpc(models.Model):
    expenses_by_epc_id = models.AutoField(primary_key=True)
    epc_costs_id = models.IntegerField()
    dict_typical_epc_work_id = models.IntegerField()
    dict_budgeting_id = models.IntegerField()
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    expenses_to_epc_map = models.ForeignKey(ExpensesToEpcMap, on_delete=models.CASCADE)
    expenses_by_epc_name = models.TextField()

    class Meta:
        db_table = 'expenses_by_epc'
        
class DictSecChapter(models.Model):
    dict_sec_chapter_id = models.AutoField(primary_key=True)
    dict_sec_chapter_name = models.TextField()

    class Meta:
        db_table = 'dict_sec_chapter'

class TempTable(models.Model):
    id = models.AutoField(primary_key=True)
    project_id = models.TextField()
    chapter_id = models.ForeignKey('DictSecChapter', on_delete=models.CASCADE)
    object_costEstimate_id = models.TextField()
    local_costEstimate_id = models.TextField()
    expenses_name = models.TextField()
    quarter = models.TextField()    
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
    is_check = models.BooleanField(default=False, verbose_name="Проверено")
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'object_analog'

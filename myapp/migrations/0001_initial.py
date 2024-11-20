# Generated by Django 5.0 on 2024-10-27 20:19

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='DictEquipmentParameterAllowedValue',
            fields=[
                ('dict_equip_param_allowed_id', models.AutoField(primary_key=True, serialize=False)),
                ('dict_equipment_parameter_id', models.IntegerField()),
                ('dict_unit_id', models.IntegerField(blank=True, null=True)),
                ('dict_equip_param_allowed_val', models.TextField(blank=True)),
                ('dict_equip_param_a_min_val', models.CharField(blank=True, max_length=2000, null=True)),
                ('dict_equip_param_a_max_val', models.CharField(blank=True, max_length=2000, null=True)),
            ],
            options={
                'verbose_name': 'Допустимое значение параметра оборудования',
                'verbose_name_plural': 'Допустимые значения параметров оборудования',
                'db_table': 'dict_equip_param_allowed_value',
            },
        ),
        migrations.CreateModel(
            name='DictEquipmentParameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dict_equipment_parameter_id', models.IntegerField()),
                ('dict_unit_id', models.IntegerField(blank=True, null=True)),
                ('dict_unit_multiplier_id', models.IntegerField(blank=True, null=True)),
                ('dict_equipment_parameter_name', models.CharField(blank=True, max_length=255, null=True)),
                ('dict_equip_par_descr', models.TextField(blank=True, null=True)),
                ('dict_equipment_parameters_code', models.CharField(blank=True, max_length=255, null=True)),
                ('dict_equip_par_is_min_max', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Параметр оборудования',
                'verbose_name_plural': 'Параметры оборудования',
                'db_table': 'dict_equipment_parameters',
            },
        ),
        migrations.CreateModel(
            name='DictEquipmentType',
            fields=[
                ('dict_equipment_type_id', models.AutoField(primary_key=True, serialize=False)),
                ('dict_equipment_type_name', models.CharField(max_length=255)),
                ('dict_equipment_type_is_hidden', models.BooleanField(default=False, null=True)),
            ],
            options={
                'verbose_name': 'Тип оборудования',
                'verbose_name_plural': 'Типы оборудования',
                'db_table': 'dict_equipment_types',
            },
        ),
        migrations.CreateModel(
            name='DictExpenditure',
            fields=[
                ('dict_expenditure_id', models.AutoField(primary_key=True, serialize=False)),
                ('dict_expense_type_id', models.IntegerField(blank=True, null=True)),
                ('dict_expenditure_name', models.TextField()),
            ],
            options={
                'db_table': 'dict_expenditures',
            },
        ),
        migrations.CreateModel(
            name='DictSecChapter',
            fields=[
                ('dict_sec_chapter_id', models.AutoField(primary_key=True, serialize=False)),
                ('dict_sec_chapter_name', models.TextField()),
            ],
            options={
                'db_table': 'dict_sec_chapters',
            },
        ),
        migrations.CreateModel(
            name='DictTechnicalPlaceTypes',
            fields=[
                ('dict_technical_place_type_id', models.AutoField(primary_key=True, serialize=False)),
                ('dict_tech_place_type_id', models.IntegerField(blank=True, null=True)),
                ('object_type_id', models.IntegerField(blank=True, null=True)),
                ('dict_technical_place_type_name', models.CharField(max_length=255)),
                ('dict_tech_place_typ_nme_lvl', models.IntegerField(blank=True, null=True)),
                ('dict_tech_place_typ_full_nme', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Тип технического места',
                'verbose_name_plural': 'Типы технических мест',
                'db_table': 'dict_technical_place_types',
            },
        ),
        migrations.CreateModel(
            name='DictVoltages',
            fields=[
                ('dict_voltage_id', models.AutoField(primary_key=True, serialize=False)),
                ('dict_voltage_name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Вольтаж',
                'verbose_name_plural': 'Вольтажи',
                'db_table': 'dict_voltages',
            },
        ),        
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('equipment_id', models.AutoField(primary_key=True, serialize=False)),
                ('technical_place_id', models.IntegerField()),
                ('dict_equipment_type_id', models.IntegerField()),
                ('equ_equipment_id', models.IntegerField(blank=True, null=True)),
                ('equipment_name', models.CharField(max_length=255)),
                ('equipment_count', models.IntegerField(blank=True, null=True)),
                ('equipment_is_autogen', models.BooleanField(default=False, null=True)),
                ('equipment_price_unc', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('equipment_price', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('equipment_mrid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('equipment_order_number', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Оборудование',
                'verbose_name_plural': 'Оборудование',
                'db_table': 'equipment',
            },
        ),
        migrations.CreateModel(
            name='EquipmentParameters',
            fields=[
                ('equipment_parameter_id', models.AutoField(primary_key=True, serialize=False)),
                ('equipment_id', models.IntegerField()),
                ('dict_equipment_parameter_id', models.IntegerField()),
                ('equipment_parameter_val', models.TextField(blank=True, null=True)),
                ('equipment_parameter_mrid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('equipment_parameter_create_dttm', models.DateTimeField(auto_now_add=True, null=True)),
                ('equipment_parameter_update_dttm', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'Параметр оборудования',
                'verbose_name_plural': 'Параметры оборудования',
                'db_table': 'equipment_parameters',
            },
        ),
        migrations.CreateModel(
            name='EquipmentTypeConsistsOf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dic_dict_equipment_type_id', models.IntegerField()),
                ('dict_equipment_type_id', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Связь типов оборудования',
                'verbose_name_plural': 'Связи типов оборудования',
                'db_table': 'equipmentTypeConsistsOf',
            },
        ),
        migrations.CreateModel(
            name='EquipmentTypeHasParameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dict_equipment_parameter_id', models.IntegerField()),
                ('dict_equipment_type_id', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Тип параметра оборудования',
                'verbose_name_plural': 'Типы параметров оборудования',
                'db_table': 'equipmentTypeHasParameters',
            },
        ),                
        migrations.CreateModel(
            name='ExpensesToEpcMap',
            fields=[
                ('expenses_to_epc_map_id', models.AutoField(primary_key=True, serialize=False)),
                ('expenses_to_epc_map_nme', models.TextField()),
                ('expenses_to_epc_map_epc', models.TextField()),
                ('expenses_to_epc_number', models.IntegerField()),
                ('expenses_to_epc_voltage_marker', models.IntegerField(blank=True, null=True)),
                ('expenses_to_epc_type', models.IntegerField()),
            ],
            options={
                'db_table': 'expenses_to_epc_map',
            },
        ),
        migrations.CreateModel(
            name='InvestProject',
            fields=[
                ('invest_project_id', models.AutoField(primary_key=True, serialize=False)),
                ('dict_project_type_id', models.IntegerField()),
                ('dict_project_status_id', models.IntegerField()),
                ('summary_estimate_calculation_id', models.IntegerField(null=True)),
                ('invest_project_type', models.IntegerField()),
                ('invest_project_mrid', models.CharField(max_length=36, null=True)),
                ('invest_project_version', models.IntegerField(null=True)),
                ('invest_project_unc_forecast', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('invest_project_create_dttm', models.DateTimeField(null=True)),
                ('invest_project_update_dttm', models.DateTimeField(null=True)),
                ('invest_project_group_number', models.TextField(null=True)),
                ('invest_project_stage', models.TextField(null=True)),
                ('invest_project_is_analogue', models.BooleanField(null=True)),
                ('invest_project_shortname', models.CharField(max_length=255, null=True)),
                ('invest_project_begindate', models.DateTimeField(null=True)),
                ('invest_project_enddate', models.DateTimeField(null=True)),
                ('invest_project_description', models.TextField(null=True)),
                ('invest_project_fullname', models.TextField()),
                ('invest_project_code', models.TextField()),
                ('invest_project_ptk_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('invest_project_titul_pir', models.BooleanField(default=False)),
                ('invest_project_auto_bs', models.BooleanField(default=False)),
                ('invest_project_auto_pir', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Инвестиционный проект',
                'verbose_name_plural': 'Инвестиционные проекты',
                'db_table': 'invest_project',
            },
        ),        
        migrations.CreateModel(
            name='Object',
            fields=[
            ('object_id', models.AutoField(primary_key=True, serialize=False)),
            ('invest_project', models.ForeignKey('InvestProject', on_delete=models.CASCADE)),  # Добавлен ForeignKey на InvestProject
            ('object_type_id', models.IntegerField()),
            ('dict_region_id', models.IntegerField(null=True)),
            ('dict_work_type_id', models.IntegerField()),
            ('dict_substaion_type_id', models.IntegerField(null=True)),
            ('start_up_complex_id', models.IntegerField(null=True)),
            ('dict_regions_economic_zone_id', models.IntegerField(null=True)),
            ('object_name', models.CharField(max_length=255)),
            ('object_mrid', models.UUIDField()),
            ('object_is_analogue', models.BooleanField(null=True)),  # Исправлено имя на object_is_analogue
            ('object_create_dttm', models.DateTimeField(null=True)),
            ('object_update_dttm', models.DateTimeField(null=True)),
            ('object_calc_type', models.TextField(null=True)),
        ],
            options={
                'verbose_name': 'Объект',
                'verbose_name_plural': 'Объекты',
                'db_table': 'object',
            },
        ),
        migrations.CreateModel(
            name='EpcCalculation',
            fields=[
                ('epc_calculation_ind', models.AutoField(primary_key=True, serialize=False)),
                ('object_id', models.ForeignKey('Object', on_delete=models.CASCADE, related_name='epc_calculations', null=True)),  # Внешний ключ на Object, может быть null
                ('epc_calculation_mrid', models.UUIDField()),
                ('epc_calculation_before_ded', models.BooleanField()),
                ('epc_calculation_link_ptk', models.TextField(null=True)),
            ],
            options={
                'verbose_name': 'Расчет УНЦ',
                'verbose_name_plural': 'Расчеты УНЦ',
                'db_table': 'epc_calculation',
            },
        ),
        migrations.CreateModel(
            name='ObjectAnalog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('project_id', models.TextField()),
                ('project_name', models.TextField()),
                ('object_costEstimate_id', models.TextField()),
                ('local_costEstimate_id', models.TextField()),
                ('expenses_name', models.TextField()),
                ('quarter', models.TextField()),
                ('construction_cost', models.TextField(blank=True, null=True, verbose_name='Стоимость строительных работ')),
                ('installation_cost', models.TextField(blank=True, null=True, verbose_name='Стоимость монтажных работ')),
                ('equipment_cost', models.TextField(blank=True, null=True, verbose_name='Стоимость оборудования, мебели, инвентаря')),
                ('other_cost', models.TextField(blank=True, null=True, verbose_name='Стоимость прочих затрат')),
                ('total_cost', models.TextField(blank=True, null=True, verbose_name='Общая сметная стоимость')),
                ('unc_code', models.TextField()),
                ('name_unc', models.TextField()),
                ('name_object', models.TextField()),
                ('voltage', models.TextField()),
                ('TX', models.TextField()),
                ('count', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unit', models.TextField()),
                ('matched_keyword', models.TextField()),
                ('additional_info', models.TextField(blank=True, null=True)),
                ('is_check', models.BooleanField(default=False, verbose_name='Проверено')),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'object_analog',
            },
        ),
        migrations.CreateModel(
            name='SummaryEstimateCalculation',
            fields=[
                ('summary_estimate_calculation_id', models.AutoField(primary_key=True, serialize=False)),
                ('invest_project_id', models.ForeignKey('InvestProject', on_delete=models.CASCADE, null=True)),
                ('sum_est_calc_mrid', models.UUIDField()),
                ('sum_est_calc_before_ded', models.BooleanField()),
            ],
            options={
                'verbose_name': 'Сводная смета расчета',
                'verbose_name_plural': 'Сводные сметы расчетов',
                'db_table': 'summary_estimate_calculation',
            },
        ),
        migrations.CreateModel(
            name='ObjectCostEstimate',
            fields=[
                ('object_cost_estimate_id', models.AutoField(primary_key=True, serialize=False)),
                ('summary_estimate_calculation_id', models.ForeignKey('SummaryEstimateCalculation', on_delete=models.CASCADE, null=True)), 
                ('object_cost_estimate_code', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Объектная смета',
                'verbose_name_plural': 'Объектные сметы',
                'db_table': 'object_cost_estimates',
            },
        ),
        migrations.CreateModel(
            name='LocalCostEstimate',
            fields=[
                ('local_cost_estimate_id', models.AutoField(primary_key=True, serialize=False)),
                ('local_cost_estimate_code', models.CharField(max_length=255)),
                ('object_cost_estimate_id', models.ForeignKey('ObjectCostEstimate', on_delete=models.CASCADE, null=True, blank=True)),
                ('summary_estimate_calculation_id', models.ForeignKey('SummaryEstimateCalculation', on_delete=models.CASCADE, null=True)),
            ],
            options={
                'verbose_name': 'Локальная смета',
                'verbose_name_plural': 'Локальные сметы',
                'db_table': 'local_cost_estimates',
            },
        ),
        migrations.CreateModel(
            name='LocalEstimateData',
            fields=[
                ('local_estimate_data_id', models.AutoField(primary_key=True, serialize=False)),
                ('local_cost_estimate_id', models.ForeignKey('myapp.LocalCostEstimate', on_delete=models.CASCADE, related_name='parsed_data', null=True)),
                ('local_estimate_data_rn', models.IntegerField(null=True, verbose_name='Номер строки')),
                ('local_estimate_row_data', models.JSONField(null=True, verbose_name='Данные строки в формате JSON')),
            ],
            options={
                'verbose_name': 'Данные парсинга локальной сметы',
                'verbose_name_plural': 'Данные парсинга локальных смет',
                'db_table': 'local_estimates_data',
            },
        ),
        migrations.CreateModel(
            name='LocalEstimateDataSort',
            fields=[
                ('sort_local_estimate_id', models.AutoField(primary_key=True, serialize=False)),
                ('local_cost_estimate', models.ForeignKey('LocalCostEstimate', on_delete=models.CASCADE, related_name='estimate_sort_data')),  # Связь с локальной сметой
                ('local_estimate_data_code', models.TextField(null=True)),
                ('local_estimate_data_part', models.TextField(null=True)),
                ('local_estimate_data_name', models.TextField(null=True)),
                ('local_estimate_data_type', models.TextField(null=True)),
                ('local_estimate_data_type_code', models.TextField(null=True)),
            ],
            options={
                'verbose_name': 'Данные сортировки локальной сметы',
                'verbose_name_plural': 'Данные сортировки локальных смет',
                'db_table': 'local_estimate_data_sort',
            },
        ),
        migrations.CreateModel(
            name='TechicalPlace',
            fields=[
                ('technical_place_id', models.AutoField(primary_key=True, serialize=False)),
                ('dict_voltage_id', models.IntegerField(blank=True, null=True)),
                ('object_id', models.IntegerField()),
                ('dict_technical_place_type_id', models.IntegerField()),
                ('tec_technical_place_id', models.IntegerField(blank=True, null=True)),
                ('technical_place_name', models.CharField(max_length=255)),
                ('technical_place_mrid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('technical_place_create_dttm', models.DateTimeField(auto_now_add=True, null=True)),
                ('technical_place_update_dttm', models.DateTimeField(auto_now=True, null=True)),
                ('technical_place_order_number', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Техническое место',
                'verbose_name_plural': 'Технические места',
                'db_table': 'techical_place',
            },
        ),
        migrations.CreateModel(
            name='TechPlaceEquipTypeLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dict_technical_place_type_id', models.IntegerField()),
                ('dict_equipment_type_id', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Тип технического места и оборудования',
                'verbose_name_plural': 'Типы технического места и оборудования',
                'db_table': 'tech_place_equip_type_link',
            },
        ),
        migrations.CreateModel(
            name='TempTable',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('project_id', models.TextField()),
                ('object_costEstimate_id', models.TextField(blank=True, null=True)),
                ('local_costEstimate_id', models.TextField(blank=True, null=True)),
                ('expenses_name', models.TextField()),
                ('quarter', models.TextField(blank=True, null=True)),
                ('construction_cost', models.TextField(blank=True, null=True, verbose_name='Стоимость строительных работ')),
                ('installation_cost', models.TextField(blank=True, null=True, verbose_name='Стоимость монтажных работ')),
                ('equipment_cost', models.TextField(blank=True, null=True, verbose_name='Стоимость оборудования, мебели, инвентаря')),
                ('other_cost', models.TextField(blank=True, null=True, verbose_name='Стоимость прочих затрат')),
                ('total_cost', models.TextField(blank=True, null=True, verbose_name='Общая сметная стоимость')),
            ],
            options={
                'db_table': 'temp_table',
            },
        ),
        migrations.CreateModel(
            name='TempTableLocal',
            fields=[
                ('parsed_local_estimate_id', models.AutoField(primary_key=True, serialize=False)),
                ('row_number', models.IntegerField(verbose_name='Номер строки')),
                ('row_data', models.JSONField(verbose_name='Данные строки в формате JSON')),
            ],
            options={
                'verbose_name': 'Данные парсинга локальной сметы',
                'verbose_name_plural': 'Данные парсинга локальных смет',
                'db_table': 'temp_table_local',
            },
        ),
        migrations.CreateModel(
            name='TempTableUNC',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('project_id', models.TextField()),
                ('project_name', models.TextField()),
                ('name_unc', models.TextField()),
                ('name_object', models.TextField()),
                ('voltage', models.TextField()),
                ('TX', models.TextField()),
                ('count', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unit', models.TextField()),
                ('unc_code', models.TextField()),
            ],
            options={
                'db_table': 'temp_table_unc',
            },
        ),
        migrations.CreateModel(
            name='TempTableССКUNC',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('matched_keyword', models.TextField()),
                ('additional_info', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'temp_table_cck_unc',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Expenses',
            fields=[
                ('expense_id', models.AutoField(primary_key=True, serialize=False)),
                ('local_cost_estimate_id', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.LocalCostEstimate')),
                ('object_cost_estimate_id', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.ObjectCostEstimate')),
                ('summary_estimate_calculation_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.SummaryEstimateCalculation')),
                ('dict_expenditure_id', models.IntegerField(null=True)),
                ('dict_sec_chapter_id', models.ForeignKey('DictSecChapter', on_delete=models.CASCADE, null=True)),
                ('expense_value', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('expense_nme', models.CharField(max_length=255, null=True)),
                ('expense_qarter', models.TextField(null=True)),
                ('expense_construction_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, verbose_name='Стоимость строительных работ')),
                ('expense_installation_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, verbose_name='Стоимость монтажных работ')),
                ('expense_equipment_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, verbose_name='Стоимость оборудования, мебели, инвентаря')),
                ('expense_other_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, verbose_name='Стоимость прочих затрат')),
                ('expense_total', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, verbose_name='Общая сметная стоимость')),
                ('expense_description', models.TextField(blank=True, null=True)),
                ('expense_checked', models.BooleanField(blank=True, default=False, null=True, verbose_name='Проверено')),
            ],
            options={
                'verbose_name': 'Затрата',
                'verbose_name_plural': 'Затраты',
                'db_table': 'expenses',
            },
        ),
        migrations.CreateModel(
            name='AtypicalExpenses',
            fields=[
                ('atypical_expenses_id', models.AutoField(primary_key=True, serialize=False)),
                ('dict_atypical_expenses_id', models.IntegerField(null=True)),
                ('epc_calculation_ind', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.epccalculation')),
            ],
            options={
                'verbose_name': 'Ненормированные затраты',
                'verbose_name_plural': 'Ненормированные затраты',
                'db_table': 'atypical_expenses',
            },
        ),        
        migrations.CreateModel(
            name='EpcCosts',
            fields=[
                ('epc_costs_id', models.AutoField(primary_key=True, serialize=False)),
                ('epc_calculation_ind', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.epccalculation')),
                ('dict_cost_epc_id', models.IntegerField(null=True)),
                ('dict_cost_epc_table_id', models.IntegerField(null=True)),
                ('equipment_parameter_id', models.IntegerField(null=True)),
                ('epc_costs_id_name', models.CharField(max_length=255, null=True)),
                ('epc_costs_description', models.TextField(blank=True, null=True)),
                ('epc_costs_checked', models.BooleanField(default=False, verbose_name='Проверено')),
                ('object', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.object')),
                ('name_object', models.TextField()),
                ('voltage', models.TextField()),
                ('TX', models.TextField()),
                ('count', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unit', models.TextField()),
                ('code', models.TextField()),      
            ],
            options={
                'verbose_name': 'Расценка УНЦ',
                'verbose_name_plural': 'Расценки УНЦ',
                'db_table': 'epc_costs',
            },
        ),
        migrations.CreateModel(
            name='ExpensesByEpc',
            fields=[
                ('expenses_by_epc_id', models.AutoField(primary_key=True, serialize=False)),
                ('epc_costs_id', models.ForeignKey('EpcCosts', on_delete=models.CASCADE)),  # ForeignKey на EpcCosts
                ('dict_typical_epc_work_id', models.IntegerField(null=True)),
                ('dict_budgeting_id', models.IntegerField(null=True)),
                ('expense_id', models.ForeignKey('Expenses', on_delete=models.CASCADE)),  # ForeignKey на Expenses
                ('expenses_to_epc_map_id', models.ForeignKey('ExpensesToEpcMap', on_delete=models.CASCADE)),  # ForeignKey на ExpensesToEpcMap
                ('expenses_by_epc_nme', models.CharField(max_length=255, null=True)),
                ('expenses_by_epc_descr', models.TextField(blank=True, null=True)),
                ('expenses_by_epc_checked', models.BooleanField(default=False, verbose_name='Проверено')),
                ('expenses_by_epc_cost', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
            options={
                'verbose_name': 'Затраты по УНЦ',
                'verbose_name_plural': 'Затраты по УНЦ',
                'db_table': 'expenses_by_epc',
            },
        ),        
        migrations.AddConstraint(
            model_name='equipmenttypeconsistsof',
            constraint=models.UniqueConstraint(fields=('dic_dict_equipment_type_id', 'dict_equipment_type_id'), name='pk_equipment_type_consists_of'),
        ),
        migrations.AddConstraint(
            model_name='equipmenttypehasparameters',
            constraint=models.UniqueConstraint(fields=('dict_equipment_parameter_id', 'dict_equipment_type_id'), name='pk_equipment_type_has_parameters'),
        ),
        migrations.AddField(
            model_name='objectanalog',
            name='chapter_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.dictsecchapter'),
        ),
        migrations.AddField(
            model_name='objectanalog',
            name='key_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.expensestoepcmap'),
        ),
        migrations.AddField(
            model_name='temptable',
            name='chapter_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.dictsecchapter'),
        ),
        migrations.AddField(
            model_name='temptablelocal',
            name='temp_table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parsed_data', to='myapp.temptable'),
        ),
        migrations.AddField(
            model_name='temptableсскunc',
            name='key_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.expensestoepcmap'),
        ),
        migrations.AddField(
            model_name='temptableсскunc',
            name='temp_table_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.temptable'),
        ),
        migrations.AddField(
            model_name='temptableсскunc',
            name='temp_table_unc_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.temptableunc'),
        ),
    ]

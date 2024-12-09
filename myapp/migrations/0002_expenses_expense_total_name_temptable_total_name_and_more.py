# Generated by Django 5.0 on 2024-12-09 11:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenses',
            name='expense_total_name',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='temptable',
            name='total_name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='epccalculation',
            name='object_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='epc_calculations', to='myapp.object'),
        ),
        migrations.AlterField(
            model_name='epccosts',
            name='epc_costs_id_name',
            field=models.CharField(max_length=2055, null=True),
        ),
        migrations.AlterField(
            model_name='epccosts',
            name='object',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.object'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expenses',
            name='dict_sec_chapter_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.dictsecchapter'),
        ),
        migrations.AlterField(
            model_name='expenses',
            name='expense_nme',
            field=models.CharField(max_length=2055, null=True),
        ),
        migrations.AlterField(
            model_name='expensesbyepc',
            name='epc_costs_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.epccosts'),
        ),
        migrations.AlterField(
            model_name='expensesbyepc',
            name='expense_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.expenses'),
        ),
        migrations.AlterField(
            model_name='expensesbyepc',
            name='expenses_to_epc_map_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.expensestoepcmap'),
        ),
        migrations.AlterField(
            model_name='investproject',
            name='invest_project_shortname',
            field=models.CharField(max_length=2055, null=True),
        ),
        migrations.AlterField(
            model_name='localcostestimate',
            name='object_cost_estimate_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.objectcostestimate'),
        ),
        migrations.AlterField(
            model_name='localcostestimate',
            name='summary_estimate_calculation_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.summaryestimatecalculation'),
        ),
        migrations.AlterField(
            model_name='localestimatedatasort',
            name='local_cost_estimate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estimate_sort_data_2', to='myapp.localcostestimate'),
        ),
        migrations.AlterField(
            model_name='object',
            name='invest_project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.investproject'),
        ),
        migrations.AlterField(
            model_name='object',
            name='object_name',
            field=models.CharField(max_length=2055),
        ),
        migrations.AlterField(
            model_name='objectcostestimate',
            name='summary_estimate_calculation_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.summaryestimatecalculation'),
        ),
        migrations.AlterField(
            model_name='summaryestimatecalculation',
            name='invest_project_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.investproject'),
        ),
        migrations.CreateModel(
            name='LocalEstimateDataSort_2',
            fields=[
                ('sort_local_estimate_id', models.AutoField(primary_key=True, serialize=False)),
                ('local_estimate_data_code', models.TextField(null=True)),
                ('local_estimate_data_part', models.TextField(null=True)),
                ('local_estimate_data_name', models.TextField(null=True)),
                ('local_estimate_data_type', models.TextField(null=True)),
                ('local_estimate_data_type_code', models.TextField(null=True)),
                ('local_estimate_data_unit', models.TextField(null=True)),
                ('local_estimate_data_count_one', models.TextField(null=True)),
                ('local_estimate_data_count_coef', models.TextField(null=True)),
                ('local_estimate_data_count_total', models.TextField(null=True)),
                ('local_estimate_data_cost_one', models.TextField(null=True)),
                ('local_estimate_data_cost_coef', models.TextField(null=True)),
                ('local_estimate_data_cost_total_base', models.TextField(null=True)),
                ('local_estimate_data_index', models.TextField(null=True)),
                ('local_estimate_data_cost_total_now', models.TextField(null=True)),
                ('local_estimate_data_cost_index_id', models.TextField(null=True)),
                ('local_cost_estimate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estimate_sort_data', to='myapp.localcostestimate')),
            ],
            options={
                'verbose_name': 'Данные сортировки локальной сметы',
                'verbose_name_plural': 'Данные сортировки локальных смет',
                'db_table': 'local_estimate_data_sort_2',
            },
        ),
    ]

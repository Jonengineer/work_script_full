# Generated by Django 5.0 on 2024-09-04 15:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_expensesbyepc_description_expensesbyepc_is_check'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParsedLocalEstimateData',
            fields=[
                ('parsed_local_estimate_id', models.AutoField(primary_key=True, serialize=False)),
                ('row_number', models.IntegerField(verbose_name='Номер строки')),
                ('row_data', models.JSONField(verbose_name='Данные строки в формате JSON')),
                ('local_cost_estimate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parsed_data', to='myapp.localcostestimate')),
            ],
            options={
                'verbose_name': 'Данные парсинга локальной сметы',
                'verbose_name_plural': 'Данные парсинга локальных смет',
                'db_table': 'parsed_local_estimate_data',
            },
        ),
    ]
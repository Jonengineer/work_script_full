# Generated by Django 5.0 on 2024-08-13 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_temptableunc_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='temptable',
            name='construction_cost',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True, verbose_name='Стоимость строительных работ'),
        ),
        migrations.AlterField(
            model_name='temptable',
            name='equipment_cost',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True, verbose_name='Стоимость оборудования, мебели, инвентаря'),
        ),
        migrations.AlterField(
            model_name='temptable',
            name='installation_cost',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True, verbose_name='Стоимость монтажных работ'),
        ),
        migrations.AlterField(
            model_name='temptable',
            name='other_cost',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True, verbose_name='Стоимость прочих затрат'),
        ),
        migrations.AlterField(
            model_name='temptable',
            name='total_cost',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True, verbose_name='Общая сметная стоимость'),
        ),
    ]

# Generated by Django 5.0 on 2025-02-06 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenses',
            name='expense_checked',
            field=models.BooleanField(blank=True, db_index=True, default=False, null=True, verbose_name='Проверено'),
        ),
    ]

# Generated by Django 5.0 on 2024-08-21 21:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_remove_temptableсскunc_is_check_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objectanalog',
            name='key_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.expensestoepcmap'),
        ),
    ]
# Generated by Django 5.0 on 2024-08-21 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_objectanalog_chapter_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='temptableunc',
            name='project_name',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
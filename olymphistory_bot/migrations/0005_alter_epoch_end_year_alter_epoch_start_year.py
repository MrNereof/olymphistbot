# Generated by Django 4.2.5 on 2023-09-23 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olymphistory_bot', '0004_alter_epoch_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='epoch',
            name='end_year',
            field=models.CharField(blank=True, max_length=25, null=True, verbose_name='Конец'),
        ),
        migrations.AlterField(
            model_name='epoch',
            name='start_year',
            field=models.CharField(blank=True, max_length=25, null=True, verbose_name='Начало'),
        ),
    ]

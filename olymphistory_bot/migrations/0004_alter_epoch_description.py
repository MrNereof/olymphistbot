# Generated by Django 4.2.5 on 2023-09-23 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olymphistory_bot', '0003_epoch_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='epoch',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
    ]

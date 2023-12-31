# Generated by Django 4.2.5 on 2023-10-02 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olymphistory_bot', '0005_alter_epoch_end_year_alter_epoch_start_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='epoch',
            name='image',
            field=models.ImageField(blank=True, upload_to='epochs', verbose_name='Картинка'),
        ),
        migrations.AddField(
            model_name='topic',
            name='image',
            field=models.ImageField(blank=True, upload_to='topics', verbose_name='Картинка'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
    ]

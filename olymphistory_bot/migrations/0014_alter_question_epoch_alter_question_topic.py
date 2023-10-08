# Generated by Django 4.1 on 2023-10-08 09:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('olymphistory_bot', '0013_remove_epoch_emoji'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='epoch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='olymphistory_bot.epoch', verbose_name='Эпоха'),
        ),
        migrations.AlterField(
            model_name='question',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='olymphistory_bot.topic', verbose_name='Тема'),
        ),
    ]

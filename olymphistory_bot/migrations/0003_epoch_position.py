# Generated by Django 4.2.5 on 2023-09-23 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olymphistory_bot', '0002_epoch_note_questiontype_topic_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='epoch',
            name='position',
            field=models.IntegerField(blank=True, null=True, verbose_name='Позиция'),
        ),
    ]

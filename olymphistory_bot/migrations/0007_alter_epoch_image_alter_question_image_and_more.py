# Generated by Django 4.2.5 on 2023-10-02 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olymphistory_bot', '0006_epoch_image_topic_image_alter_topic_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='epoch',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='epochs', verbose_name='Картинка'),
        ),
        migrations.AlterField(
            model_name='question',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='questions', verbose_name='Картинка'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='topics', verbose_name='Картинка'),
        ),
    ]

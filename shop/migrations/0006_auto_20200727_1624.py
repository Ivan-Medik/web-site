# Generated by Django 3.0.8 on 2020-07-27 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_auto_20200727_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='background',
            field=models.CharField(max_length=150, verbose_name='Цвет фона'),
        ),
    ]

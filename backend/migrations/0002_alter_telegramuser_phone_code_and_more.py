# Generated by Django 4.0.4 on 2022-09-23 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramuser',
            name='phone_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='phone_code_hash',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
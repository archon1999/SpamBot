# Generated by Django 4.0.3 on 2022-09-28 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_alter_mailing_options_alter_telegramuser_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramuser',
            name='session_string',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

# Generated by Django 4.0.3 on 2022-10-02 19:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0007_alter_balancereplenishment_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailing',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

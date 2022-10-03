# Generated by Django 4.0.3 on 2022-10-02 13:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_rename_purchase_purchasetarrif_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='balancereplenishment',
            options={'verbose_name': 'Пополнение баланса', 'verbose_name_plural': 'История пополнение баланса'},
        ),
        migrations.AddField(
            model_name='balancereplenishment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

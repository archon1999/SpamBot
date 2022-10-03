from django_q.tasks import async_task
from django.contrib.auth.models import AbstractUser
from django.db import models
from ckeditor.fields import RichTextField


class TelegramUser(models.Model):
    class Status(models.IntegerChoices):
        UNKNOWN = 0, 'Неизвестно'
        OK = 1, 'Работает'
        NOT_WORKING = 2, 'Не работает'

    api_id = models.IntegerField()
    api_hash = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    session_string = models.TextField(null=True,
                                      blank=True)
    status = models.IntegerField(choices=Status.choices,
                                 default=Status.UNKNOWN)

    class Meta:
        verbose_name = 'Телеграм аккаунт'
        verbose_name_plural = 'Телеграм аккаунты'


class User(AbstractUser):
    balance = models.IntegerField(default=0)
    available_messages_count = models.IntegerField(default=10)


class Tarrif(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    messages_count = models.IntegerField(verbose_name='Количество сообщений')
    price = models.IntegerField(verbose_name='Цена')

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'

    def __str__(self):
        return self.name


class Mailing(models.Model):
    text = RichTextField()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mailings',
    )
    users = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def users_count(self):
        return len(self.users.split())

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        async_task('backend.tasks.mailing', self.id)
        return result

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class PurchaseTarrif(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='purchases',
    )
    tarrif = models.ForeignKey(Tarrif, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Покупка тарифа'
        verbose_name_plural = 'Покупки тарифа'


class BalanceReplenishment(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='balance_replenishments'
    )
    value = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Пополнение баланса'
        verbose_name_plural = 'История пополнение баланса'

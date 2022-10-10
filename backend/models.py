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


def avatar_directory_path(instance, filename):
    return f'images/avatars/{instance.username}.jpg'


class User(AbstractUser):
    balance = models.IntegerField(default=0)
    available_messages_count = models.IntegerField(default=10)
    avatar = models.ImageField(upload_to=avatar_directory_path,
                               null=True,
                               blank=True)


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
    class Status(models.IntegerChoices):
        CREATED = 0, 'Ждет потдверждение'
        RUNNING = 1, 'В работе'
        FINISHED = 2, 'Завершен'
        SCHEDULED = 3, 'Запланирован'

    name = models.CharField(max_length=255)
    text = RichTextField()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mailings',
    )
    status = models.IntegerField(default=Status.CREATED,
                                 choices=Status.choices)
    datetime = models.DateTimeField()
    image = models.ImageField(upload_to='backend/images', null=True)
    users = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def users_count(self):
        return len(self.users.split())

    def get_badge_class(self):
        return {
            Mailing.Status.CREATED: 'secondary',
            Mailing.Status.RUNNING: 'warning',
            Mailing.Status.FINISHED: 'success',
            Mailing.Status.SCHEDULED: 'info',
        }[self.status]

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class ParseredChat(models.Model):
    class Status(models.IntegerChoices):
        IN_QUEUE = 0, 'В очереди'
        RUNNING = 1, 'В работе'
        ERROR = 2, 'Ошибка'
        OK = 3, 'ОК'

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='parsered_chats',
    )
    status = models.IntegerField(choices=Status.choices,
                                 default=Status.IN_QUEUE)
    chat_name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def get_badge_class(self):
        return {
            ParseredChat.Status.IN_QUEUE: 'secondary',
            ParseredChat.Status.RUNNING: 'warning',
            ParseredChat.Status.OK: 'success',
            ParseredChat.Status.ERROR: 'danger',
        }[self.status]


class ChatMember(models.Model):
    chat = models.ForeignKey(
        to=ParseredChat,
        on_delete=models.CASCADE,
        related_name='members',
    )
    user_id = models.BigIntegerField()
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=255, null=True)


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

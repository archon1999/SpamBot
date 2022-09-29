from django.contrib import admin

from .models import TelegramUser, Mailing


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone_number']


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ['id']

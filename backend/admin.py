from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import (BalanceReplenishment, Mailing, PurchaseTarrif, Tarrif,
                     TelegramUser, User)


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone_number', 'check_', 'status_']

    @admin.display(description='')
    def check_(self, obj):
        href = f'/telegramuser_check/{obj.id}'
        return format_html(f'<a href="{href}" class="button">Проверить</a>')

    @admin.display(description='status')
    def status_(self, obj):
        if obj.status == TelegramUser.Status.OK:
            color = 'success'
        elif obj.status == TelegramUser.Status.UNKNOWN:
            color = 'secondary'
        elif obj.status == TelegramUser.Status.NOT_WORKING:
            color = 'danger'

        html = f'<b class="text-{color}">{obj.get_status_display()}</b>'
        return format_html(html)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(User)
class UserAdmin_(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": (
        "balance",
        'available_messages_count')}),)
    list_display = ['id', 'first_name', 'username',
                    'balance', 'available_messages_count']


@admin.register(Tarrif)
class TarrifAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'messages_count', 'price']


@admin.register(PurchaseTarrif)
class PurchaseTarrifAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'tarrif', 'created']


@admin.register(BalanceReplenishment)
class BalanceReplenishmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'value']

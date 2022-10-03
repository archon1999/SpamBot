import asyncio
import traceback

from django.shortcuts import get_object_or_404, redirect
from django.views import View

from backend.models import TelegramUser


class TelegramuserCheckView(View):
    def get(self, request, id):
        from pyrogram import Client
        telegram_user = get_object_or_404(TelegramUser, id=id)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            client = Client(':memory:',
                            telegram_user.api_id,
                            telegram_user.api_hash,
                            session_string=telegram_user.session_string,
                            in_memory=True)
            client.start()
            client.send_message('me', 'Проверка')
            client.stop()
        except Exception:
            telegram_user.status = TelegramUser.Status.NOT_WORKING
            traceback.print_exc()
        else:
            telegram_user.status = TelegramUser.Status.OK
        finally:
            telegram_user.save()
            asyncio.get_event_loop().stop()

        return redirect('/admin/backend/telegramuser/')

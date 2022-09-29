import asyncio
import time
import traceback

from pyrogram import Client, enums

from .models import TelegramUser
from .utils import filter_html


def mailing(users, text):
    text = filter_html(text)
    i = 0
    for _ in range(10):
        if i == len(users):
            break

        for telegram_user in TelegramUser.objects.all():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            client = Client(':memory:',
                            telegram_user.api_id,
                            telegram_user.api_hash,
                            session_string=telegram_user.session_string,
                            in_memory=True)
            client.start()
            while i < len(users):
                try:
                    client.send_message(users[i], text,
                                        parse_mode=enums.parse_mode.ParseMode.HTML)
                except Exception:
                    traceback.print_exc()
                else:
                    i += 1
                finally:
                    time.sleep(1)

            client.stop()
            asyncio.get_event_loop().stop()

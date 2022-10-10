import asyncio
import time
import traceback

from pyrogram import Client
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.errors.exceptions.bad_request_400 import UsernameNotOccupied

from .models import TelegramUser, Mailing, ParseredChat
from .utils import filter_html


def mailing(mailing_id):
    mailing = Mailing.objects.get(id=mailing_id)
    mailing.status = Mailing.Status.RUNNING
    mailing.save()
    text = filter_html(mailing.text)
    users = mailing.users.split()
    i = 0
    for _ in range(1):
        if i == len(users):
            break

        for telegram_user in TelegramUser.objects.filter(
            status=TelegramUser.Status.OK
        ):
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
                    if mailing.image:
                        with open(mailing.image.name, 'rb') as photo:
                            client.send_photo(
                                chat_id=users[i],
                                caption=text,
                                photo=photo,
                                parse_mode=ParseMode.HTML,
                            )
                    else:
                        client.send_message(
                            chat_id=users[i],
                            text=text,
                            parse_mode=ParseMode.HTML,
                        )

                except UsernameNotOccupied:
                    pass
                except Exception:
                    traceback.print_exc()
                finally:
                    i += 1
                    time.sleep(1)

            client.stop()
            asyncio.get_event_loop().stop()

    mailing.status = Mailing.Status.FINISHED
    mailing.save()


def mailing_check(mailing_id):
    mailing = Mailing.objects.get(id=mailing_id)
    text = mailing.text
    text = filter_html(text)
    user_id = int(mailing.user.social_auth.first().extra_data['id'][0])
    telegram_user = TelegramUser.objects.filter(
        status=TelegramUser.Status.OK
    ).first()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = Client(':memory:',
                    telegram_user.api_id,
                    telegram_user.api_hash,
                    session_string=telegram_user.session_string,
                    in_memory=True)
    client.start()
    try:
        if mailing.image:
            with open(mailing.image.name, 'rb') as photo:
                client.send_photo(
                    chat_id=user_id,
                    caption=text,
                    photo=photo,
                    parse_mode=ParseMode.HTML,
                )
        else:
            client.send_message(
                chat_id=user_id,
                text=text,
                parse_mode=ParseMode.HTML,
            )
    except Exception:
        traceback.print_exc()
        return False

    client.stop()
    asyncio.get_event_loop().stop()
    return True


def parser_chat_members(parsered_chat_id):
    chat = ParseredChat.objects.get(id=parsered_chat_id)
    chat.status = ParseredChat.Status.RUNNING
    chat.save()
    telegram_user = TelegramUser.objects.filter(
        status=TelegramUser.Status.OK
    ).first()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = Client(':memory:',
                    telegram_user.api_id,
                    telegram_user.api_hash,
                    session_string=telegram_user.session_string,
                    in_memory=True)
    client.start()
    try:
        client.get_chat(chat.chat_name)
        chat_members = client.get_chat_members(chat.chat_name)
    except Exception:
        chat.status = ParseredChat.Status.ERROR
        chat.save()
        return

    for chat_member in chat_members:
        if chat_member.status != 'left':
            user = chat_member.user
            if not user.is_bot:
                info = dict()
                info['first_name'] = user.first_name
                info['user_id'] = user.id
                if user.last_name:
                    info['last_name'] = user.last_name

                if user.username:
                    info['username'] = user.username

                if user.phone_number:
                    info['phone_number'] = user.phone_number

                chat.members.create(**info)

    chat.status = ParseredChat.Status.OK
    chat.save()

    client.stop()
    asyncio.get_event_loop().stop()

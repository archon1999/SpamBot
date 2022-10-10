import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from backend.tasks import parser_chat_members
from backend.models import ParseredChat, Mailing, User, TelegramUser
from social_django.models import UserSocialAuth
from pyrogram import Client

#user = User.objects.first()
# user.social_auth.set(UserSocialAuth.objects.all())
# user.social_auth
# print(user.social_auth.first().extra_data['id'][0])

telegram_user = TelegramUser.objects.first()

# client.set_send_as_chat

client = Client(':memory:',
                telegram_user.api_id,
                telegram_user.api_hash,
                session_string=telegram_user.session_string,
                in_memory=True)
client.start()
print(client.get_send_as_chats('me'))

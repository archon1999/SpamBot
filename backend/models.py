import asyncio

from pyrogram import Client
from django.db import models
from ckeditor.fields import RichTextField


class TelegramUser(models.Model):
    api_id = models.IntegerField()
    api_hash = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    phone_code_hash = models.CharField(max_length=255,
                                       null=True,
                                       blank=True)
    phone_code = models.CharField(max_length=255,
                                  null=True,
                                  blank=True)
    ok = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        if not self.phone_code and not self.phone_code_hash:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            session_name = f'session-{self.id}'
            client = Client(session_name,
                            self.api_id,
                            self.api_hash,
                            phone_number=self.phone_number)
            client.connect()
            sent_code = client.send_code(client.phone_number)
            self.phone_code_hash = sent_code.phone_code_hash
            self.save()
            asyncio.get_event_loop().stop()

        if self.phone_code and not self.ok:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            session_name = f'session-{self.id}'
            client = Client(session_name,
                            self.api_id,
                            self.api_hash,
                            phone_number=self.phone_number)
            client.connect()
            client.sign_in(client.phone_number,
                           self.phone_code_hash,
                           client.phone_code)
            self.ok = True
            self.save()
            asyncio.get_event_loop().stop()

        return result


class Mailing(models.Model):
    text = RichTextField()
    users = models.TextField()

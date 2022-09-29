import subprocess

from django_q.tasks import async_task
from django.db import models
from ckeditor.fields import RichTextField


class TelegramUser(models.Model):
    api_id = models.IntegerField()
    api_hash = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    session_string = models.TextField(null=True,
                                      blank=True)

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        return result
        session_name = f'session-{self.id}'
        if not self.phone_code and not self.phone_code_hash:
            data = [session_name, self.api_id, self.api_hash,
                    self.phone_number]
            input = '\n'.join(map(str, data))
            proc = subprocess.Popen(
                ['python3.10', 'backend/send_code.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            proc.communicate(input.encode('utf-8'))
            while True:
                line = proc.stdout.readline().strip()
                if line:
                    self.phone_code_hash = line
                    self.save()
                    break

            exit_code = proc.wait()
            if exit_code == 0:
                self.ok = True
                self.save()

        if self.phone_code and not self.ok:
            file_path = f'backend/sessions/{session_name}-code'
            with open(file_path, 'w') as file:
                file.write(self.phone_code)

        return result

    class Meta:
        verbose_name = 'Телеграм аккаунт'
        verbose_name_plural = 'Телеграм аккаунты'


class Mailing(models.Model):
    text = RichTextField()
    users = models.TextField()

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        users = self.users.replace('\r', '').split('\n')
        async_task('backend.tasks.mailing', users, self.text)
        return result

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

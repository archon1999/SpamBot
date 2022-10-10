import os
import time
import json
from pathlib import Path

from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django_q.tasks import async_task, schedule, Schedule
from yoomoney import Quickpay

from backend.models import (BalanceReplenishment, Mailing, ParseredChat,
                            PurchaseTarrif, Tarrif, User)
from .forms import MailingForm


class HomeView(View):
    template_name = 'index.html'

    def get(self, request):
        return render(request, self.template_name, {})


class ProfileView(LoginRequiredMixin, View):
    template_name = 'profile.html'

    def get(self, request):
        success_buy = request.session.get('success_buy')
        request.session['success_buy'] = None
        return render(request, self.template_name, {
            'success_buy': success_buy
        })

    def post(self, request):
        try:
            value = abs(int(request.POST['value']))
            receiver = os.getenv('YOOMONEY_CARD')
            quickpay = Quickpay(
                receiver=receiver,
                quickpay_form="shop",
                targets="",
                paymentType="SB",
                sum=value,
                label=f'user-{request.user.id}',
                successURL="https://smmanalyze.ru/profile",
            )
            return redirect(quickpay.redirected_url)
        except Exception:
            return self.get(request)


class TarrifsView(View):
    template_name = 'tarrifs.html'

    def get(self, request):
        error = request.session.get('error', None)
        request.session['error'] = None
        tarrifs = Tarrif.objects.all()
        return render(request, self.template_name, {
            'tarrifs': tarrifs,
            'error': error,
        })


class TarrifsBuyView(LoginRequiredMixin, View):
    def get(self, request, tarrif_id):
        user = request.user
        tarrif = get_object_or_404(Tarrif, id=tarrif_id)
        if tarrif.price <= user.balance:
            PurchaseTarrif.objects.create(
                tarrif=tarrif,
                user=user,
            )
            user.balance -= tarrif.price
            user.available_messages_count += tarrif.messages_count
            user.save()
            request.session['success_buy'] = True
            return redirect('/profile')
        else:
            request.session['error'] = True
            return redirect('/tarrifs')


class MailingsView(View):
    template_name = 'mailings.html'

    def get(self, request):
        form = MailingForm()
        tab = request.session.get('mailing_tab', 'mailing')
        request.session.pop('mailing_tab', None)
        parsered_chats = None
        if request.user.is_authenticated:
            parsered_chats = request.user.parsered_chats.filter(
                status=ParseredChat.Status.OK
            )

        return render(request, self.template_name, {
            'form': form,
            'tab': tab,
            'parsered_chats': parsered_chats,
        })

    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return self.get(request)

        form = MailingForm(request.POST, request.FILES)
        if form.is_valid():
            text = form.cleaned_data['text']
            name = form.cleaned_data['name']
            users = form.cleaned_data['users']
            dt = form.cleaned_data['datetime']
            users_file = form.cleaned_data['users_file']
            if users_file:
                try:
                    users += '\n' + users_file.read().decode('utf-8')
                except Exception:
                    form.add_error('users_file', 'Некорректный файл')

            image = form.cleaned_data['image']
            if image:
                image = image.read()

            parsered_chats = form.cleaned_data['parsered_chats']
            users_count = len(users.split())
            for parsered_chat in parsered_chats:
                users_count += parsered_chat.members.count()

            if user.available_messages_count < users_count:
                form.add_error('users', 'Не хватает доступных сообщений')
            else:
                for parsered_chat in parsered_chats:
                    chat_members = parsered_chat.members.all()
                    members = '\n'.join(map(str, chat_members.values_list(
                        'user_id', flat=True)))
                    users += '\n' + members

        parsered_chats = request.user.parsered_chats.filter(
            status=ParseredChat.Status.OK
        )
        if form.errors:
            return render(request, self.template_name, {
                'form': form,
                'parsered_chats': parsered_chats,
                'tab': 'mailing',
            })
        else:
            user.available_messages_count -= users_count
            user.save()
            mailing = Mailing.objects.create(
                user=user,
                text=text,
                users=users,
                name=name,
                datetime=dt,
            )
            if image:
                path = Path(__file__).parent.parent
                filename = f'backend/images/{mailing.id}.jpg'
                filepath = path / filename
                with open(filepath, 'wb') as file:
                    file.write(image)

                mailing.image = filename
                mailing.save()

            request.session['mailing_tab'] = 'my-mailings'
            return self.get(request)


class MailingConfirmView(LoginRequiredMixin, View):
    def get(self, request, mailing_id):
        mailing = Mailing.objects.get(id=mailing_id)
        user = request.user
        if mailing.user == user:
            mailing.status = Mailing.Status.SCHEDULED
            mailing.save()
            schedule('backend.tasks.mailing', mailing_id,
                     next_run=mailing.datetime,
                     schedule_type=Schedule.ONCE,
                     name=f'mailing-{mailing_id}')

        request.session['mailing_tab'] = 'my-mailings'
        return redirect('/')


class MailingCheckView(LoginRequiredMixin, View):
    def get(self, request, mailing_id):
        mailing = Mailing.objects.get(id=mailing_id)
        user = request.user
        if mailing.user == user:
            user.social_auth.first().extra_data['id'][0]
            async_task('backend.tasks.mailing_check', mailing_id)

        request.session['mailing_tab'] = 'my-mailings'
        return redirect('/')


class MailingDeleteView(LoginRequiredMixin, View):
    def get(self, request, mailing_id):
        mailing = Mailing.objects.get(id=mailing_id)
        user = request.user
        if mailing.user == user and mailing.status == Mailing.Status.CREATED:
            users_count = mailing.users_count()
            mailing.delete()
            time.sleep(1)
            user.available_messages_count += users_count
            user.save()

        request.session['mailing_tab'] = 'my-mailings'
        return redirect('/')


class ParseredChatView(LoginRequiredMixin, View):
    def post(self, request):
        chat_name = request.POST['chat_name']
        parsered_chat = request.user.parsered_chats.create(chat_name=chat_name)
        async_task('backend.tasks.parser_chat_members', parsered_chat.id)
        request.session['mailing_tab'] = 'parser'
        return redirect('/')


class ParseredChatDeleteView(LoginRequiredMixin, View):
    def get(self, request, parsered_chat_id):
        parsered_chat = ParseredChat.objects.filter(id=parsered_chat_id).first()
        if parsered_chat and parsered_chat.user == request.user:
            parsered_chat.delete()

        request.session['mailing_tab'] = 'parser'
        return redirect('/')


class ParseredChatExportView(LoginRequiredMixin, View):
    def get(self, request, parsered_chat_id):
        parsered_chat = ParseredChat.objects.filter(
            id=parsered_chat_id
        ).first()
        if parsered_chat and parsered_chat.user == request.user:
            data = []
            for chat_member in parsered_chat.members.all():
                data.append({
                    'id': chat_member.user_id,
                    'first_name': chat_member.first_name,
                    'last_name': chat_member.last_name,
                    'username': chat_member.username,
                    'phone_number': chat_member.phone_number,
                })

            return JsonResponse(data, safe=False)

        return redirect('/')


@method_decorator(csrf_exempt, name='dispatch')
class YoomoneyView(View):
    def post(self, request):
        with open(os.path.join(os.path.dirname(__file__), 'yoomoney.txt'), 'w') as file:
            file.write(str(request.POST))

        try:
            label = request.POST.get('label', None)
            if label and label.startswith('user'):
                _, user_id = label.split('-')
                user = User.objects.get(id=int(user_id))
                amount = float(request.POST['withdraw_amount'])
                user.balance += amount
                user.save()
                BalanceReplenishment.objects.create(
                    user=user,
                    value=amount,
                )

            return HttpResponse('')
        except Exception as e:
            with open(os.path.join(os.path.dirname(__file__), 'error.txt'), 'w') as file:
                file.write(str(e))


class AuthLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/')

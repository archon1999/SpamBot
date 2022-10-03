import os

from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from yoomoney import Quickpay

from backend.models import (BalanceReplenishment, Mailing, PurchaseTarrif,
                            Tarrif, User)
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


class MailingsView(LoginRequiredMixin, View):
    template_name = 'mailings.html'

    def get(self, request):
        form = MailingForm()
        created = request.session.get('created', None)
        request.session['created'] = None
        return render(request, self.template_name, {
            'form': form,
            'created': created,
        })

    def post(self, request):
        user = request.user
        form = MailingForm(request.POST)
        if form.is_valid():
            users = form.cleaned_data['users']
            text = form.cleaned_data['text']
            users_count = len(users.split())
            if user.available_messages_count < users_count:
                form.add_error('users', 'Не хватает доступных сообщений')

        if form.errors:
            return render(request, self.template_name, {
                'form': form,
            })
        else:
            user.available_messages_count -= users_count
            user.save()
            Mailing.objects.create(
                user=user,
                text=text,
                users=users,
            )
            request.session['created'] = True
            return self.get(request)


@method_decorator(csrf_exempt, name='dispatch')
class YoomoneyView(View):
    def post(self, request):
        if (label := request.POST.get('label', None)):
            if label.startswith('user'):
                _, user_id = label.split('-')
                user = User.objects.get(id=int(user_id))
                amount = float(request.POST['amount'])
                user.balance += amount
                BalanceReplenishment.objects.create(
                    user=user,
                    value=amount,
                )

        return HttpResponse('')


class AuthLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/')

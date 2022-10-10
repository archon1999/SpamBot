from django.urls import path

from . import views

urlpatterns = [
    path('', views.MailingsView.as_view()),
    path('profile', views.ProfileView.as_view()),
    path('mailings', views.MailingsView.as_view()),
    path('mailing/confirm/<int:mailing_id>',
         views.MailingConfirmView.as_view()),
    path('mailing/check/<int:mailing_id>',
         views.MailingCheckView.as_view()),
    path('mailing/delete/<int:mailing_id>',
         views.MailingDeleteView.as_view()),
    path('tarrifs', views.TarrifsView.as_view()),
    path('parsered_chat', views.ParseredChatView.as_view()),
    path('parsered_chat/export/<int:parsered_chat_id>',
         views.ParseredChatExportView.as_view()),
    path('parsered_chat/delete/<int:parsered_chat_id>',
         views.ParseredChatDeleteView.as_view()),
    path('tarrifs/buy/<int:tarrif_id>', views.TarrifsBuyView.as_view()),
    path('logout', views.AuthLogoutView.as_view()),
    path('yoomoney', views.YoomoneyView.as_view()),
]

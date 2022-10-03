from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view()),
    path('profile', views.ProfileView.as_view()),
    path('mailings', views.MailingsView.as_view()),
    path('tarrifs', views.TarrifsView.as_view()),
    path('tarrifs/buy/<int:tarrif_id>', views.TarrifsBuyView.as_view()),
    path('logout', views.AuthLogoutView.as_view()),
    path('yoomoney', views.YoomoneyView.as_view()),
]

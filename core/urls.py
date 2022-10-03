from django.contrib import admin
from django.urls import path, re_path, include

from backend.views import TelegramuserCheckView

urlpatterns = [
    re_path('^jet', include('jet.urls', 'jet')),
    path('admin/', admin.site.urls),
    path('', include('frontend.urls')),
    path('telegramuser_check/<int:id>/',
         TelegramuserCheckView.as_view()),
]

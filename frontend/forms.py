from django import forms
from ckeditor.fields import CKEditorWidget

from backend.models import ParseredChat


class MailingForm(forms.Form):
    name = forms.CharField(max_length=255,
                           required=True)
    text = forms.CharField(widget=CKEditorWidget(),
                           required=True,
                           max_length=2000)
    users = forms.CharField(max_length=2000,
                            required=False)
    users_file = forms.FileField(required=False)
    image = forms.ImageField(required=False)
    datetime = forms.DateTimeField(input_formats='Y-m-d H:i',
                                   required=True)
    parsered_chats = forms.ModelMultipleChoiceField(ParseredChat.objects.all(),
                                                    required=False)

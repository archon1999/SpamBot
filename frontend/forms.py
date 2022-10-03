from django import forms
from ckeditor.fields import CKEditorWidget


class MailingForm(forms.Form):
    text = forms.CharField(widget=CKEditorWidget(),
                           required=True,
                           max_length=2000)
    users = forms.CharField(max_length=2000, required=True)

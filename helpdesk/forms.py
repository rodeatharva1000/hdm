from django import forms
from django.db import models
from .models import Feedback, Help


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['product', 'feedback', 'rating']


class HelpForm(forms.ModelForm):
    class Meta:
        model = Help
        fields = ['product', 'help', 'p_img']

class ReplyForm(forms.Form):
    reply = forms.CharField(widget=forms.Textarea, max_length=1000)
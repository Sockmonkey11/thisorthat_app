from django import forms
from .models import Polls

class PollForm(forms.ModelForm):
    class Meta:
        model = Polls
        fields = ('question', 'option1', 'option2')
from django import forms
from .models import Ticket


class TicketStatusForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('status', 'id')
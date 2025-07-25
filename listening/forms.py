from django import forms
from .models import ListeningTest

class ListeningTestForm(forms.ModelForm):
    """
    A simplified form for creating the main ListeningTest object.
    Parts and questions are added in the admin panel.
    """
    class Meta:
        model = ListeningTest
        fields = ['title']

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class AdminUserCreationForm(UserCreationForm):
    """A form for creating new users, without passwords."""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)

class ProfileForm(forms.ModelForm):
    """A form for editing the extra data in a user's profile."""
    class Meta:
        model = Profile
        exclude = ('user', 'is_blocked')

class AppealForm(forms.Form):
    """A form for a blocked user to submit an appeal."""
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        help_text="Please explain why you believe your account should be unblocked."
    )

from django import forms
from .models import Channel, Subscription

class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ['name', 'description', 'banner']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Channel Name'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Channel Description', 'rows': 4}),
            'banner': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = []
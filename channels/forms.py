from django import forms
from .models import Channel

class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ['name', 'description', 'banner']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Channel Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Channel Description', 'rows': 4}),
            'banner': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
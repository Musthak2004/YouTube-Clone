from django import forms

from .models import Playlist


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ["title", "description", "visibility"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter playlist name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Add a description (optional)",
                }
            ),
            "visibility": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

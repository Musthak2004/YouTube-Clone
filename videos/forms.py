from django import forms
from .models import Video

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = [
            'title',
            'description',
            'video_file',
            'thumbnail',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter video title',
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter video description',
            }),

            'video_file': forms.FileInput(attrs={
                'class': 'form-control',
            }),

            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
            })
        }
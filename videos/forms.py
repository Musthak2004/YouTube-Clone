from django import forms
from .models import Video


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = [
            'title',
            'description',
            'cloudinary_video_id',
            'cloudinary_thumbnail_id',
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

            'cloudinary_video_id': forms.HiddenInput(),
            'cloudinary_thumbnail_id': forms.HiddenInput(),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('cloudinary_video_id'):
            raise forms.ValidationError("Please upload a video using the Cloudinary uploader.")
        return cleaned
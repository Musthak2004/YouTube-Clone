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

            'video_file': forms.FileInput(attrs={
                'class': 'form-control',
            }),

            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
            }),

            'cloudinary_video_id': forms.HiddenInput(),
            'cloudinary_thumbnail_id': forms.HiddenInput(),
        }

    def clean(self):
        cleaned = super().clean()
        video_id = cleaned.get('cloudinary_video_id')
        video_file = cleaned.get('video_file')
        if not video_id and not video_file:
            raise forms.ValidationError(
                "Provide a video file or use Cloudinary upload."
            )
        return cleaned
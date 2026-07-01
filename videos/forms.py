from django import forms
from django.core.exceptions import ValidationError
from .models import Video

MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_THUMBNAIL_SIZE = 5 * 1024 * 1024  # 5 MB


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
        }

    def clean_video_file(self):
        video = self.cleaned_data.get('video_file')
        if video and video.size > MAX_VIDEO_SIZE:
            mb = MAX_VIDEO_SIZE / 1024 / 1024
            raise ValidationError(f"Video file must be under {mb:.0f} MB.")
        return video

    def clean_thumbnail(self):
        thumb = self.cleaned_data.get('thumbnail')
        if thumb and thumb.size > MAX_THUMBNAIL_SIZE:
            raise ValidationError("Thumbnail must be under 5 MB.")
        return thumb
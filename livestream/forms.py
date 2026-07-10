from django import forms

from .models import Stream, StreamKey


class StartStreamForm(forms.ModelForm):
    stream_key = forms.CharField(
        max_length=64,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter your stream key"}
        ),
        help_text="The stream key from your stream settings.",
        label="Stream Key",
    )

    class Meta:
        model = Stream
        fields = ["title", "description", "thumbnail"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Stream title"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe your stream...",
                }
            ),
            "thumbnail": forms.FileInput(attrs={"class": "form-control"}),
        }

    def clean_stream_key(self):
        value = self.cleaned_data.get("stream_key")
        try:
            sk = StreamKey.objects.get(key=value, is_active=True)
        except StreamKey.DoesNotExist:
            raise forms.ValidationError("Invalid or inactive stream key.")
        self.resolved_key = sk
        return value


class StreamSettingsForm(forms.ModelForm):
    regenerate_key = forms.BooleanField(
        required=False,
        label="Regenerate stream key",
        help_text="Check this to generate a new stream key. The old key will stop working immediately.",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = StreamKey
        fields = ["display_name"]
        widgets = {
            "display_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Optional label"}
            ),
        }

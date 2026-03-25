from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content", "image", "file", "link"]

    def clean(self):
        cleaned_data = super().clean()

        attachments = [
            cleaned_data.get("image"),
            cleaned_data.get("file"),
            cleaned_data.get("link"),
        ]

        if sum(bool(a) for a in attachments) > 1:
            raise forms.ValidationError(
                "You can attach only one item (image, file, or link)."
            )

        return cleaned_data

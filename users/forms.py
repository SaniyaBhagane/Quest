from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # 🔥 CRITICAL
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar", "bio"]

        widgets = {
            "bio": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Tell something about yourself…"
            }),
        }
        

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]

        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email address"}),
        }
from django import forms
from .models import Community, Resource

class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ["name", "description", "category", "icon"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Community name"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "icon": forms.TextInput(attrs={"placeholder": "🔥 🚀 🎨"}),
        }
        labels = {
            "name": "Community Name",
            "description": "Description",
            "category": "Category",
            "icon": "Icon",
        }
        
class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ["title", "resource_type", "file", "link"]
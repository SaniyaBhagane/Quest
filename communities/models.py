from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Community(models.Model):
    CATEGORY_CHOICES = [
        ("tech", "Technology"),
        ("edu", "Education"),
        ("health", "Health"),
        ("art", "Art"),
        ("career", "Career"),
    ]

    owner = models.ForeignKey(
        User,
        related_name="owned_communities",
        on_delete=models.CASCADE,
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        default="avatars/default.png",
        blank=True
    )

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    icon = models.CharField(max_length=5, default="🌐")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class CommunityMembership(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("member", "Member"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(
        Community,
        related_name="memberships",
        on_delete=models.CASCADE,
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "community")

    def __str__(self):
        return f"{self.user.username} → {self.community.name}"


class Resource(models.Model):
    RESOURCE_TYPES = (
        ("link", "Link"),
        ("file", "File"),
    )

    community = models.ForeignKey(
        Community,
        related_name="resources",
        on_delete=models.CASCADE,
        null=True,          # ✅ prevents migration crash
        blank=True
    )

    title = models.CharField(max_length=200)

    resource_type = models.CharField(
        max_length=10,
        choices=RESOURCE_TYPES,
        default="link"
    )

    link = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to="resources/", blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        related_name="resources",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

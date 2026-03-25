from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    bio = models.TextField(
        blank=True,
        help_text="Tell something about yourself"
    )

    def __str__(self):
        return self.user.username

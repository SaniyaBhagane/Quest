from django.db import models
from django.contrib.auth.models import User
from communities.models import Community


# =========================
# POST MODEL
# =========================
class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    title = models.CharField(
        max_length=200,
        blank=True
    )

    content = models.TextField()

    # -------- Attachments (one per post) --------
    image = models.ImageField(
        upload_to="posts/images/",
        blank=True,
        null=True
    )

    video = models.FileField(
        upload_to="posts/videos/",
        blank=True,
        null=True
    )

    file = models.FileField(
        upload_to="posts/files/",
        blank=True,
        null=True
    )

    link = models.URLField(
        blank=True,
        null=True
    )

    # -------- State --------
    is_pinned = models.BooleanField(default=False)

    upvotes = models.ManyToManyField(
        User,
        related_name="upvoted_posts",
        blank=True
    )

    # -------- AI --------
    ai_summary = models.TextField(
        blank=True,
        null=True,
        help_text="AI-generated summary of discussion"
    )

    summary_updated_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_pinned", "-created_at"]
        indexes = [
            models.Index(fields=["community"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title or self.content[:40]

    # -------- Helpers --------
    def upvote_count(self):
        return self.upvotes.count()

    def has_attachment(self):
        return any([self.image, self.video, self.file, self.link])

    def has_summary(self):
        return bool(self.ai_summary)


# =========================
# COMMENT MODEL (Nested)
# =========================
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    content = models.TextField()

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="replies",
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["post"]),
            models.Index(fields=["parent"]),
        ]

    def __str__(self):
        return f"Comment by {self.author.username}"

    # -------- Helpers --------
    def is_reply(self):
        return self.parent is not None

    def reply_count(self):
        return self.replies.count()

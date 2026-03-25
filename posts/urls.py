from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    # Create post inside a community
    path("create/<int:community_id>/", views.create_post, name="create"),

    # Post detail
    path("<int:post_id>/", views.post_detail, name="post_detail"),

    # Edit / Delete
    path("<int:post_id>/edit/", views.edit_post, name="edit_post"),
    path("<int:post_id>/delete/", views.delete_post, name="delete_post"),

    # Actions
    path("<int:post_id>/pin/", views.toggle_pin, name="pin"),
    path("<int:post_id>/upvote/", views.toggle_upvote, name="upvote"),

    # AI summary
    path("<int:post_id>/summarize/", views.summarize_post, name="summarize"),
]

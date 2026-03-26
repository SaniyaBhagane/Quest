from django.urls import path
from . import views

app_name = "communities"

urlpatterns = [
    path("", views.community_list, name="list"),
    path("create/", views.community_create, name="create"),

    # ✅ FIX: put chatbot BEFORE slug
    path("chatbot/", views.chatbot_api, name="chatbot_api"),

    path("<slug:slug>/", views.community_detail, name="detail"),
    path("<slug:slug>/edit/", views.edit_community, name="edit"),
    path("<slug:slug>/delete/", views.delete_community, name="delete"),
    path("<slug:slug>/join/", views.join_community, name="join"),
    path("<slug:slug>/leave/", views.leave_community, name="leave"),

    path("<int:community_id>/load-more/", views.load_more_posts, name="load_more"),
]
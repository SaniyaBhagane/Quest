from django.urls import path
from . import views

app_name = "communities"

urlpatterns = [
    path("", views.community_list, name="list"),

    path("create/", views.community_create, name="create"),  # ✅ ADD THIS

    path("<slug:slug>/", views.community_detail, name="detail"),
    path("<slug:slug>/join/", views.join_community, name="join"),
    path("<slug:slug>/leave/", views.leave_community, name="leave"),
    path("<slug:slug>/edit/", views.edit_community, name="edit"),
    path("<slug:slug>/delete/", views.delete_community, name="delete"),
    path("<slug:slug>/remove/<int:user_id>/", views.remove_member, name="remove_member"),
    path("<slug:slug>/transfer/<int:user_id>/", views.transfer_ownership, name="transfer_owner"),
    path("load-posts/<int:community_id>/", views.load_more_posts, name="load_posts"),
    path("<slug:slug>/resources/add/", views.add_resource, name="add_resource"),
]

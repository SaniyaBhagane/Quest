from django.contrib import admin
from .models import Community, Resource
from django.db.models import Count


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "member_count")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(member_count=Count("memberships"))

    def member_count(self, obj):
        return obj.member_count

    member_count.admin_order_field = "member_count"


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "resource_type", "created_at")


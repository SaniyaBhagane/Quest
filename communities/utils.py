from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from .models import Community

def owner_required(view_func):
    def wrapper(request, slug, *args, **kwargs):
        community = get_object_or_404(Community, slug=slug)
        if community.owner != request.user:
            return HttpResponseForbidden("Owner access only")
        return view_func(request, community, *args, **kwargs)
    return wrapper

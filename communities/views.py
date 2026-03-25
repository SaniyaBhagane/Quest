from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator

from .models import Community, CommunityMembership, Resource
from .forms import CommunityForm, ResourceForm
from posts.models import Post


# =========================
# COMMUNITY LIST / EXPLORE
# =========================
def community_list(request):
    search_query = request.GET.get("q", "")
    active_category = request.GET.get("category", "")

    communities = Community.objects.all()

    # 🔍 Search
    if search_query:
        communities = communities.filter(name__icontains=search_query)

    # 🧩 Category filter (FIXED: "all")
    if active_category and active_category != "all":
        communities = communities.filter(category=active_category)

    categories = Community.CATEGORY_CHOICES

    joined_ids = []
    if request.user.is_authenticated:
        joined_ids = CommunityMembership.objects.filter(
            user=request.user
        ).values_list("community_id", flat=True)

    # ➕ Create community
    if request.method == "POST" and request.user.is_authenticated:
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.owner = request.user
            community.save()

            CommunityMembership.objects.create(
                user=request.user,
                community=community,
                role="owner"
            )
            return redirect("communities:list")
    else:
        form = CommunityForm()

    return render(request, "communities/explore.html", {
        "communities": communities,
        "categories": categories,
        "active_category": active_category or "all",
        "search_query": search_query,
        "joined_ids": joined_ids,
        "form": form,
    })


# =========================
# JOIN / LEAVE COMMUNITY
# =========================
@login_required
def join_community(request, slug):
    if request.method != "POST":
        return redirect("communities:detail", slug=slug)

    community = get_object_or_404(Community, slug=slug)

    CommunityMembership.objects.get_or_create(
        user=request.user,
        community=community,
        defaults={"role": "member"},
    )

    return redirect(request.META.get("HTTP_REFERER", "communities:list"))


@login_required
def leave_community(request, slug):
    if request.method != "POST":
        return redirect("communities:detail", slug=slug)

    community = get_object_or_404(Community, slug=slug)

    # ❌ Owner cannot leave
    if community.owner == request.user:
        return redirect("communities:detail", slug=slug)

    CommunityMembership.objects.filter(
        user=request.user,
        community=community
    ).delete()

    return redirect("communities:list")


# =========================
# COMMUNITY DETAIL
# =========================
def community_detail(request, slug):
    community = get_object_or_404(Community, slug=slug)

    posts_qs = community.posts.select_related(
        "author"
    ).prefetch_related(
        "upvotes", "comments"
    ).order_by("-is_pinned", "-created_at")

    paginator = Paginator(posts_qs, 5)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    is_member = False
    is_owner = False

    if request.user.is_authenticated:
        is_owner = community.owner == request.user
        is_member = CommunityMembership.objects.filter(
            user=request.user,
            community=community
        ).exists()

    # AJAX: load more posts
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "posts/_posts_only.html", {
            "posts": page_obj,
        })

    return render(request, "communities/community_detail.html", {
        "community": community,
        "posts": page_obj,
        "is_member": is_member,
        "is_owner": is_owner,
    })


# =========================
# ADD RESOURCE
# =========================
@login_required
def add_resource(request, slug):
    community = get_object_or_404(Community, slug=slug)

    if not CommunityMembership.objects.filter(
        user=request.user,
        community=community
    ).exists():
        return redirect("communities:detail", slug=slug)

    if request.method == "POST":
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.community = community
            resource.created_by = request.user
            resource.save()
            return redirect("communities:detail", slug=slug)
    else:
        form = ResourceForm()

    return render(request, "communities/add_resource.html", {
        "form": form,
        "community": community
    })


# =========================
# LOAD MORE POSTS (AJAX)
# =========================
def load_more_posts(request, community_id):
    page = int(request.GET.get("page", 1))
    POSTS_PER_PAGE = 5
    offset = (page - 1) * POSTS_PER_PAGE

    community = get_object_or_404(Community, id=community_id)

    posts = Post.objects.filter(
        community=community
    ).order_by(
        "-is_pinned", "-created_at"
    )[offset:offset + POSTS_PER_PAGE]

    total_count = Post.objects.filter(community=community).count()
    has_more = total_count > offset + POSTS_PER_PAGE

    html = render_to_string(
        "posts/post_list.html",
        {"posts": posts, "request": request}
    )

    return JsonResponse({
        "html": html,
        "has_more": has_more
    })


# =========================
# EDIT COMMUNITY
# =========================
@login_required
def edit_community(request, slug):
    community = get_object_or_404(Community, slug=slug)

    if request.user != community.owner:
        return HttpResponseForbidden("You are not allowed to edit this community.")

    if request.method == "POST":
        form = CommunityForm(request.POST, request.FILES, instance=community)
        if form.is_valid():
            form.save()
            return redirect("communities:detail", slug=community.slug)
    else:
        form = CommunityForm(instance=community)

    return render(request, "communities/edit_community.html", {
        "form": form,
        "community": community,
    })


# =========================
# DELETE COMMUNITY (POST ONLY)
# =========================
@login_required
def delete_community(request, slug):
    community = get_object_or_404(Community, slug=slug)

    if request.user != community.owner:
        return HttpResponseForbidden("You are not allowed to delete this community.")

    if request.method == "POST":
        community.delete()
        return redirect("communities:list")

    return redirect("communities:detail", slug=slug)


# =========================
# REMOVE MEMBER
# =========================
@login_required
def remove_member(request, slug, user_id):
    community = get_object_or_404(Community, slug=slug)

    if request.user != community.owner:
        return HttpResponseForbidden("You are not allowed to remove members.")

    member = get_object_or_404(User, id=user_id)

    if member == community.owner:
        return redirect("communities:detail", slug=slug)

    CommunityMembership.objects.filter(
        user=member,
        community=community
    ).delete()

    return redirect("communities:detail", slug=slug)


# =========================
# TRANSFER OWNERSHIP
# =========================
@login_required
def transfer_ownership(request, slug, user_id):
    community = get_object_or_404(Community, slug=slug)

    if request.user != community.owner:
        return HttpResponseForbidden("You are not allowed to transfer ownership.")

    new_owner = get_object_or_404(User, id=user_id)

    if not CommunityMembership.objects.filter(
        user=new_owner,
        community=community
    ).exists():
        return redirect("communities:detail", slug=slug)

    community.owner = new_owner
    community.save()

    CommunityMembership.objects.filter(
        user=request.user,
        community=community
    ).update(role="member")

    CommunityMembership.objects.filter(
        user=new_owner,
        community=community
    ).update(role="owner")

    return redirect("communities:detail", slug=slug)


@login_required
def community_create(request):
    if request.method == "POST":
        form = CommunityForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.owner = request.user
            community.save()

            # auto-join as owner
            CommunityMembership.objects.create(
                user=request.user,
                community=community,
                role="owner"
            )

            # ✅ auto redirect to community page
            return redirect("communities:detail", slug=community.slug)
    else:
        form = CommunityForm()

    return render(request, "communities/create.html", {
        "form": form
    })

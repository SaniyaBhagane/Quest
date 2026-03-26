import json
import os

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Community, CommunityMembership
from .forms import CommunityForm
from posts.models import Post

# =========================
# GEMINI (NEW SDK SETUP)
# =========================
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-1.5-flash"


# =========================
# COMMUNITY LIST
# =========================
def community_list(request):
    search_query = request.GET.get("q", "")
    active_category = request.GET.get("category", "")

    communities = Community.objects.all()

    if search_query:
        communities = communities.filter(name__icontains=search_query)

    if active_category and active_category != "all":
        communities = communities.filter(category=active_category)

    categories = Community.CATEGORY_CHOICES

    joined_ids = []
    if request.user.is_authenticated:
        joined_ids = list(
            CommunityMembership.objects.filter(user=request.user)
            .values_list("community_id", flat=True)
        )

    return render(request, "communities/explore.html", {
        "communities": communities,
        "categories": categories,
        "active_category": active_category or "all",
        "search_query": search_query,
        "joined_ids": joined_ids,
    })


# =========================
# CREATE COMMUNITY
# =========================
@login_required
def community_create(request):
    if request.method == "POST":
        form = CommunityForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.owner = request.user
            community.save()

            CommunityMembership.objects.create(
                user=request.user,
                community=community,
                role="owner"
            )

            return redirect("communities:detail", slug=community.slug)
    else:
        form = CommunityForm()

    return render(request, "communities/create.html", {
        "form": form
    })


# =========================
# COMMUNITY DETAIL
# =========================
def community_detail(request, slug):
    community = get_object_or_404(Community, slug=slug)

    posts_qs = community.posts.select_related("author").prefetch_related(
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

    # AJAX infinite scroll
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
# JOIN COMMUNITY
# =========================
@login_required
def join_community(request, slug):
    if request.method != "POST":
        return redirect("communities:list")

    community = get_object_or_404(Community, slug=slug)

    CommunityMembership.objects.get_or_create(
        user=request.user,
        community=community,
        defaults={"role": "member"},
    )

    return redirect(request.META.get("HTTP_REFERER", "communities:list"))


# =========================
# LEAVE COMMUNITY
# =========================
@login_required
def leave_community(request, slug):
    if request.method != "POST":
        return redirect("communities:list")

    community = get_object_or_404(Community, slug=slug)

    if community.owner == request.user:
        return redirect("communities:detail", slug=slug)

    CommunityMembership.objects.filter(
        user=request.user,
        community=community
    ).delete()

    return redirect("communities:list")


# =========================
# EDIT COMMUNITY
# =========================
@login_required
def edit_community(request, slug):
    community = get_object_or_404(Community, slug=slug)

    if request.user != community.owner:
        return HttpResponseForbidden("Not allowed")

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
# DELETE COMMUNITY
# =========================
@login_required
def delete_community(request, slug):
    community = get_object_or_404(Community, slug=slug)

    if request.user != community.owner:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        community.delete()
        return redirect("communities:list")

    return redirect("communities:detail", slug=slug)


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
    ).order_by("-is_pinned", "-created_at")[offset:offset + POSTS_PER_PAGE]

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
# CHATBOT API (FIXED GEMINI)
# =========================
SYSTEM_PROMPT = """
You are Quest Assistant — a premium AI inside a modern platform.
- Be helpful, smart, and concise
- Guide users clearly
- Help with communities, posts, and learning
- Keep tone modern and friendly
"""


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_api(request):
    try:
        data = json.loads(request.body)
        messages = data.get("messages", [])

        if not messages:
            return JsonResponse({"error": "No messages"}, status=400)

        messages = messages[-10:]

        # Build conversation text
        conversation = SYSTEM_PROMPT + "\n\n"

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")

            if role == "user":
                conversation += f"User: {content}\n"
            else:
                conversation += f"Assistant: {content}\n"

        # Gemini request
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=conversation
        )

        reply = response.text if response.text else "No response generated."

        return JsonResponse({"reply": reply})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
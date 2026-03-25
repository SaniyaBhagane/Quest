from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from .models import Post
from .forms import PostForm
from communities.models import Community
from posts.models import Comment


# ==========================
# CREATE POST
# ==========================
@login_required
def create_post(request, community_id):
    community = get_object_or_404(Community, id=community_id)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.community = community
            post.save()

            messages.success(request, "Post created successfully")
            return redirect("posts:post_detail", post_id=post.id)

    else:
        form = PostForm()

    return render(request, "posts/create.html", {
        "form": form,
        "community": community
    })


# ==========================
# POST DETAIL + COMMENTS
# ==========================
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    comments = Comment.objects.filter(
        post=post,
        parent__isnull=True
    ).select_related("author")

    if request.method == "POST":
        content = request.POST.get("content")
        parent_id = request.POST.get("parent_id")

        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
                parent_id=parent_id if parent_id else None
            )

            # 🔥 IMPORTANT: redirect back to COMMUNITY page
            return redirect(
                "communities:detail",
                slug=post.community.slug
            )

    return render(request, "posts/detail.html", {
        "post": post,
        "comments": comments
    })


# ==========================
# EDIT POST
# ==========================
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated")
            return redirect("posts:post_detail", post_id=post.id)

    else:
        form = PostForm(instance=post)

    return render(request, "posts/edit.html", {
        "form": form,
        "post": post
    })


# ==========================
# DELETE POST
# ==========================
@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    community_slug = post.community.slug
    post.delete()

    messages.success(request, "Post deleted")
    return redirect("communities:detail", slug=community_slug)


# ==========================
# PIN / UNPIN
# ==========================
@login_required
@require_POST
def toggle_pin(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.community.owner:
        messages.error(request, "Only community owner can pin posts")
        return redirect("posts:post_detail", post_id=post.id)

    post.is_pinned = not post.is_pinned
    post.save()

    return redirect("communities:detail", slug=post.community.slug)


# ==========================
# UPVOTE
# ==========================
@login_required
@require_POST
def toggle_upvote(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.upvotes.all():
        post.upvotes.remove(request.user)
    else:
        post.upvotes.add(request.user)

    return redirect("posts:post_detail", post_id=post.id)


# ==========================
# AI SUMMARY
# ==========================
@login_required
def summarize_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # placeholder — integrate AI here
    post.ai_summary = "AI-generated summary will appear here."
    post.save()

    return redirect("posts:post_detail", post_id=post.id)

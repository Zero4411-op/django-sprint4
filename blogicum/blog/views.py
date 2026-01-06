from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, UserEditForm
from .models import Category, Comment, Post

User = get_user_model()

PER_PAGE = 10


def _paginate(request, qs):
    paginator = Paginator(qs, PER_PAGE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def _public_posts_qs():
    return (
        Post.objects.select_related("author", "category", "location")
        .annotate(comment_count=Count("comments"))
        .filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )
        .order_by("-pub_date")
    )


def index(request):
    page_obj = _paginate(request, _public_posts_qs())
    context = {
        "page_obj": page_obj,
        "post_list": page_obj,
    }
    return render(request, "blog/index.html", context)


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug, is_published=True)
    qs = _public_posts_qs().filter(category=category)
    page_obj = _paginate(request, qs)
    return render(
        request,
        "blog/category.html",
        {"category": category, "page_obj": page_obj},
    )


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    qs = (
        Post.objects.select_related("author", "category", "location")
        .annotate(comment_count=Count("comments"))
        .filter(author=profile_user)
        .order_by("-pub_date")
    )

    is_owner = request.user.is_authenticated and request.user == profile_user
    if not is_owner:
        qs = qs.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )

    page_obj = _paginate(request, qs)
    context = {
        "profile": profile_user,
        "profile_user": profile_user,
        "page_obj": page_obj,
    }
    return render(request, "blog/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("author", "category", "location"),
        id=post_id,
    )

    is_public = (
        post.is_published
        and post.pub_date <= timezone.now()
        and post.category.is_published
    )
    is_owner = (
        request.user.is_authenticated and post.author_id == request.user.id
    )

    if not (is_public or is_owner):
        raise Http404

    comments = (
        Comment.objects.select_related("author")
        .filter(post=post)
        .order_by("created_at")
    )

    form = CommentForm()
    return render(
        request,
        "blog/detail.html",
        {"post": post, "comments": comments, "form": form},
    )


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = PostForm()

    return render(request, "blog/create.html", {"form": form})


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if not request.user.is_authenticated or post.author_id != request.user.id:
        return redirect("blog:post_detail", post_id=post.id)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, "blog/create.html", {"form": form, "post": post})


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if not request.user.is_authenticated or post.author_id != request.user.id:
        return redirect("blog:post_detail", post_id=post.id)

    if request.method == "POST":
        post.delete()
        return redirect("blog:profile", username=request.user.username)

    return render(request, "blog/delete.html", {"post": post})


@login_required
def edit_profile(request, username=None):
    if username and username != request.user.username:
        return redirect("blog:profile", username=username)

    if request.method == "POST":
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = UserEditForm(instance=request.user)

    return render(
        request, "registration/registration_form.html", {"form": form}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("category"),
        id=post_id,
    )

    is_public = (
        post.is_published
        and post.pub_date <= timezone.now()
        and post.category.is_published
    )
    is_owner = post.author_id == request.user.id

    if not (is_public or is_owner):
        raise Http404

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

    return redirect("blog:post_detail", post_id=post.id)


def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if (
        not request.user.is_authenticated
        or comment.author_id != request.user.id
    ):
        return redirect("blog:post_detail", post_id=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(
        request, "blog/comment.html", {"form": form, "comment": comment}
    )


def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if (
        not request.user.is_authenticated
        or comment.author_id != request.user.id
    ):
        return redirect("blog:post_detail", post_id=post_id)

    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", post_id=post_id)

    return render(request, "blog/comment.html", {"comment": comment})

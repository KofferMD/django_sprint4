import datetime as dt
from typing import Any, Dict
from django.db.models.query import QuerySet
from django.db.models import Count
from django.forms.models import BaseModelForm
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from blog.models import Post, Category, Comment
from blog.models import User
from blog.form import PostForm, CommentForm


class PostListView(ListView):
    model = Post
    queryset = (
        Post.objects.prefetch_related("author", "category", "location")
        .filter(
            pub_date__lt=dt.datetime.now(),
            is_published=True,
            category__is_published=True,
        )
        .annotate(comment_count=Count("comment"))
        .all()
    )
    paginate_by = 10
    ordering = "-pub_date"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form: BaseModelForm):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse("blog:profile", kwargs={
            "username": self.request.user.username})


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm
        context["comments"] = self.object.comment.select_related("author")

        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs["pk"], author=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy("blog:post_list")

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs["pk"], author=request.user)
        return super().dispatch(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    post_object = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.post_object.pk})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ["text"]

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, pk=self.kwargs["comment_pk"],
                                 post_id=self.kwargs["post_pk"])

    def get_success_url(self):
        return reverse_lazy("blog:post_detail",
                            kwargs={"pk": self.kwargs["post_pk"]})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = "blog/comment_form.html"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment, pk=self.kwargs["comment_pk"],
            post_id=self.kwargs["post_pk"]
        )

    def get_success_url(self):
        return reverse_lazy("blog:post_detail",
                            kwargs={"pk": self.kwargs["post_pk"]})


class CategoryListView(ListView):
    model = Post
    template_name = "blog/category.html"
    context_object_name = "page_obj"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(Category,
                                          slug=self.kwargs['category_slug'],
                                          is_published=True)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        self.category = get_object_or_404(Category,
                                          slug=self.kwargs["category_slug"],
                                          is_published=True)
        return (
            Post.objects.filter(category=self.category,
                                pub_date__lt=dt.datetime.now(),
                                category__is_published=True,
                                is_published=True,
                                )
            .annotate(comment_count=Count("comment"))
            .all()
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class ProfileView(ListView):
    model = Post
    template_name = "blog/profile.html"
    context_object_name = "page_obj"
    paginate_by = 10
    ordering = "-pub_date"

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return (
            Post.objects.prefetch_related("author", "category", "location")
            .filter(
                author=self.author,
                pub_date__lt=dt.datetime.now(),
            )
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date")
            .all()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "blog/profile_update.html"
    fields = [
        "username",
        "first_name",
        "last_name",
        "email",
    ]

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(User, username=self.kwargs["username"])
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_success_url(self):
        return reverse("blog:profile",
                       kwargs={"username": self.object.username})

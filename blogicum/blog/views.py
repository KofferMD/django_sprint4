import datetime as dt
from typing import Any, Dict
from django.db.models.query import QuerySet

from django.shortcuts import render, get_object_or_404
from django.views.generic import (ListView, 
                                  CreateView, 
                                  UpdateView, 
                                  DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from blog.models import Post, Category
from blog.models import User


class PostListView(ListView):
    model = Post
    queryset = Post.objects.prefetch_related('author', 'category', 'location')
    paginate_by = 10


class PostCreateView(LoginRequiredMixin, CreateView):
    pass


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    pass


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'  # замените на имя вашего шаблона, если оно другое
    context_object_name = 'page_obj'  # замените на имя переменной, которое вы хотите использовать в шаблоне
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return Post.objects.filter(category=self.category)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'  # замените на имя вашего шаблона, если оно другое
    context_object_name = 'page_obj'  # замените на имя переменной, которое вы хотите использовать в шаблоне
    paginate_by = 10
    
    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(author=self.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context
    



















    

def category_posts(request, category_slug):
    template = 'blog/category.html'

    category = get_object_or_404(Category.objects.all().filter(
        slug=category_slug,
        is_published=True
    ))

    post_list = Post.objects.select_related('category').filter(
        category__slug=category_slug,
        is_published=True,
        pub_date__lt=dt.datetime.now(),
    )
    context = {
        'category': category,
        'post_list': post_list
    }
    return render(request, template, context)


def post_detail(request, pk):
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.select_related('category').filter(
            is_published=True,
            pub_date__lt=dt.datetime.now(),
            category__is_published=True
        ), pk=pk)
    context = {'post': post}

    return render(request, template, context)





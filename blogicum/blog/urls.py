from django.urls import path
from blog import views

app_name: str = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('edit_profile/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/create/', views.PostCreateView.as_view(), name='create_post'),
    path('category/<slug:category_slug>/',views.CategoryListView.as_view(), name='category_posts'),
    path('profile/<str:username>', views.ProfileView.as_view(), name='profile'),
]

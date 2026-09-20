# blog/urls.py

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_home, name='blog-home'),
    path('blog-home/', views.blog_home, name='blog-home'),
    path('blog-single/<slug:slug>/', views.blog_single, name='blog-single'),
    path('post/<slug:slug>/', views.post_detail, name='detail'),
    path('category/<slug:slug>/', views.category_posts, name='category'),
]
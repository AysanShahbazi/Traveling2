# blog/views.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import BlogPost, Category, Comment


def blog_home(request):
    """Blog homepage with all posts"""
    posts = BlogPost.objects.filter(is_active=True).order_by('-publish_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(posts, 5)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)
    
    # Get categories with post counts
    categories = Category.objects.all()
    for category in categories:
        category.post_count = BlogPost.objects.filter(category=category, is_active=True).count()
    
    # Popular posts for sidebar
    popular_posts = BlogPost.objects.filter(is_active=True).order_by('-views')[:5]
    
    context = {
        'posts': posts,
        'search_query': search_query,
        'categories': categories,
        'popular_posts': popular_posts,
    }
    return render(request, 'blog/blog-home.html', context)

def blog_single(request, slug):
    """Single blog post detail view"""
    post = get_object_or_404(BlogPost, slug=slug, is_active=True)
    
    # Increment view count
    post.views += 1
    post.save()
    
    # Handle comment submission
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        if name and email and message:
            Comment.objects.create(
                post=post,
                name=name,
                email=email,
                message=message
            )
            messages.success(request, 'Your comment has been posted!')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Get categories for sidebar
    categories = Category.objects.all()
    for category in categories:
        category.post_count = BlogPost.objects.filter(category=category, is_active=True).count()
    
    # Popular posts for sidebar
    popular_posts = BlogPost.objects.filter(is_active=True).exclude(id=post.id).order_by('-views')[:5]
    
    # Related posts
    related_posts = BlogPost.objects.filter(is_active=True).exclude(id=post.id).order_by('-publish_date')[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'comments': post.comments.filter(is_approved=True),
        'categories': categories,
        'popular_posts': popular_posts,
    }
    return render(request, 'blog/blog-single.html', context)

def post_detail(request, slug):
    """Alias for blog_single"""
    return blog_single(request, slug)

def category_posts(request, slug):
    """View posts by category"""
    category = get_object_or_404(Category, slug=slug)
    posts = BlogPost.objects.filter(category=category, is_active=True).order_by('-publish_date')
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'blog/category.html', context)
# pages/urls.py

from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    # Public pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('elements/', views.elements, name='elements'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Admin Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Banner Management
    path('dashboard/banners/', views.manage_banners, name='manage_banners'),
    path('dashboard/banners/add/', views.add_banner, name='add_banner'),
    path('dashboard/banners/edit/<int:pk>/', views.edit_banner, name='edit_banner'),
    path('dashboard/banners/delete/<int:pk>/', views.delete_banner, name='delete_banner'),
    
    # Service Management
    path('dashboard/services/', views.manage_services, name='manage_services'),
    path('dashboard/services/add/', views.add_service, name='add_service'),
    path('dashboard/services/edit/<int:pk>/', views.edit_service, name='edit_service'),
    path('dashboard/services/delete/<int:pk>/', views.delete_service, name='delete_service'),
    
    # About Section Management
    path('dashboard/about/', views.manage_about, name='manage_about'),
    path('dashboard/about/add/', views.add_about, name='add_about'),
    path('dashboard/about/edit/<int:pk>/', views.edit_about, name='edit_about'),
    path('dashboard/about/delete/<int:pk>/', views.delete_about, name='delete_about'),
    
    # Blog Management
    path('dashboard/blogs/', views.manage_blogs, name='manage_blogs'),
    path('dashboard/blogs/add/', views.add_blog, name='add_blog'),
    path('dashboard/blogs/edit/<int:pk>/', views.edit_blog, name='edit_blog'),
    path('dashboard/blogs/delete/<int:pk>/', views.delete_blog, name='delete_blog'),
    
    # User Management
    path('dashboard/users/', views.admin_users, name='admin_users'),
    path('dashboard/users/add/', views.admin_user_add, name='admin_user_add'),
    path('dashboard/users/edit/<int:user_id>/', views.admin_user_edit, name='admin_user_edit'),
    path('dashboard/users/delete/<int:user_id>/', views.admin_user_delete, name='admin_user_delete'),
    path('dashboard/users/toggle/<int:user_id>/', views.admin_user_toggle_status, name='admin_user_toggle_status'),
    
    # Booking Management
    path('dashboard/bookings/', views.manage_bookings, name='manage_bookings'),
    path('dashboard/bookings/add/', views.add_booking, name='add_booking'),
    path('dashboard/bookings/edit/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('dashboard/bookings/delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),
]
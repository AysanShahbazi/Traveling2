# pages/admin.py

from django.contrib import admin
from .models import Banner, Destination, Service, AboutSection, BlogPost, ContactMessage

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active']

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'price', 'is_active', 'order']
    list_filter = ['is_active']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order']
    list_filter = ['is_active']

@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active']
    list_filter = ['is_active']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'publish_date', 'is_active']
    list_filter = ['is_active', 'category']
    search_fields = ['title', 'content']
    # حذف خط prepopulated_fields چون فیلد slug وجود ندارد
    # prepopulated_fields = {'slug': ('title',)}

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
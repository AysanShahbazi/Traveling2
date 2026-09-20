# bookings/admin.py

from django.contrib import admin
from .models import Booking, CartItem
import json

class CartItemAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'item_type', 'quantity', 'price', 'created_at']
    list_filter = ['item_type', 'created_at']
    search_fields = ['item_name', 'session_key']

class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_ref', 'full_name', 'email', 'total', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['booking_ref', 'full_name', 'email', 'phone']
    readonly_fields = ['booking_ref', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_ref', 'user', 'status')
        }),
        ('Contact Details', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Passengers & Items', {
            'fields': ('passengers', 'items')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax', 'discount', 'total', 'payment_method')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user')

# ثبت مدل‌ها در ادمین
admin.site.register(Booking, BookingAdmin)

# بررسی اینکه CartItem قبلاً ثبت نشده باشد
if not admin.site.is_registered(CartItem):
    admin.site.register(CartItem, CartItemAdmin)
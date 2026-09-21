# payments/admin.py

from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id', 'booking', 'amount', 'method',
        'status', 'card_last4', 'created_at', 'paid_at'
    )
    list_filter = ('status', 'method', 'created_at')
    search_fields = (
        'transaction_id', 'booking__booking_ref',
        'booking__full_name', 'booking__email'
    )
    readonly_fields = ('transaction_id', 'created_at', 'paid_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('transaction_id', 'booking', 'amount', 'method', 'status')
        }),
        ('اطلاعات کارت', {
            'fields': ('card_last4', 'error_message'),
            'classes': ('collapse',)
        }),
        ('زمان‌ها', {
            'fields': ('created_at', 'paid_at'),
        }),
    )
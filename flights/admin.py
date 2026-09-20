# flights/admin.py

from django.contrib import admin
from .models import Airline, Airport, Flight, Seat

@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'city', 'country']
    search_fields = ['name', 'code', 'city']

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['flight_number', 'airline', 'origin', 'destination', 'departure_time', 'economy_price', 'is_active']
    list_filter = ['airline', 'origin', 'destination', 'is_active']
    search_fields = ['flight_number']
    date_hierarchy = 'departure_time'
    fieldsets = (
        ('اطلاعات پرواز', {
            'fields': ('airline', 'flight_number', 'aircraft_type')
        }),
        ('مسیر', {
            'fields': ('origin', 'destination')
        }),
        ('زمان', {
            'fields': ('departure_time', 'arrival_time')
        }),
        ('قیمت‌ها', {
            'fields': ('economy_price', 'business_price', 'first_class_price')
        }),
        ('ظرفیت', {
            'fields': ('economy_seats', 'business_seats', 'first_class_seats')
        }),
        ('امکانات', {
            'fields': ('baggage_allowance', 'hand_baggage', 'has_meal', 'has_entertainment')
        }),
        ('وضعیت', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['flight', 'seat_number', 'class_type', 'is_available']
    list_filter = ['class_type', 'is_available']
    
    

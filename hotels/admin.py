# hotels/admin.py

from django.contrib import admin
from .models import Hotel, Room, RoomType, Amenity, Review, HotelImage


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'star_rating', 'min_price', 'is_active']
    list_filter = ['star_rating', 'is_active', 'city']
    search_fields = ['name', 'city', 'address']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'room_type', 'price_per_night', 'is_available']
    list_filter = ['is_available', 'hotel']


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'capacity', 'size']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'is_approved']


@admin.register(HotelImage)
class HotelImageAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'title', 'is_main']
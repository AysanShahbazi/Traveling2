# flights/urls.py

from django.urls import path
from . import views

app_name = 'flights'

urlpatterns = [
    path('search/', views.search_flights, name='search'),
    path('results/', views.flight_results, name='results'),
    path('detail/<int:flight_id>/', views.flight_detail, name='detail'),
    path('all/', views.all_flights, name='all_flights'),
    path('add-to-cart/<int:flight_id>/', views.add_to_cart, name='add_to_cart'),
    path('passenger-info/<int:flight_id>/', views.passenger_info, name='passenger_info'),
    path('booking-review/<int:flight_id>/', views.booking_review, name='booking_review'),
    path('confirm-booking/<int:flight_id>/', views.confirm_booking, name='confirm_booking'),
    
    # Admin URLs
    path('admin/', views.admin_flights, name='admin_flights'),
    path('admin/add/', views.admin_flight_add, name='admin_flight_add'),
    path('admin/edit/<int:flight_id>/', views.admin_flight_edit, name='admin_flight_edit'),
    path('admin/delete/<int:flight_id>/', views.admin_flight_delete, name='admin_flight_delete'),
    
    # API URLs for seat status
    path('api/seat-status/<int:flight_id>/', views.api_seat_status, name='api_seat_status'),
    path('api/update-seat/', views.api_update_seat, name='api_update_seat'),
]
# bookings/urls.py

from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirm-booking/', views.confirm_booking, name='confirm_booking'),
    path('confirmation/<str:ref>/', views.confirmation, name='confirmation'),
]
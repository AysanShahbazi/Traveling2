# payments/urls.py

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<str:booking_ref>/', views.payment_process, name='process'),
    path('callback/', views.payment_callback, name='callback'),
    path('detail/<str:transaction_id>/', views.payment_detail, name='detail'),
]
# hotels/urls.py

from django.urls import path
from . import views

app_name = 'hotels'

urlpatterns = [
    path('search/', views.search_hotels, name='search'),
    path('detail/<int:hotel_id>/', views.hotel_detail, name='detail'),
    path('all/', views.all_hotels, name='all_hotels'),
    path('add-to-cart/<int:hotel_id>/', views.add_to_cart, name='add_to_cart'),
    
    # Admin URLs
    path('admin/', views.admin_hotels, name='admin_hotels'),
    path('admin/add/', views.admin_hotel_add, name='admin_hotel_add'),
    path('admin/edit/<int:hotel_id>/', views.admin_hotel_edit, name='admin_hotel_edit'),
    path('admin/delete/<int:hotel_id>/', views.admin_hotel_delete, name='admin_hotel_delete'),
]
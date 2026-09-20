# bookings/models.py

from django.db import models
from django.conf import settings

class CartItem(models.Model):
    """مدل سبد خرید - برای ذخیره موقت یا دائم"""
    session_key = models.CharField(max_length=100)
    item_type = models.CharField(max_length=20, choices=[('flight', 'Flight'), ('hotel', 'Hotel')])
    item_id = models.IntegerField()
    item_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.item_name} - {self.item_type}"

from django.db import models
from django.conf import settings

class Booking(models.Model):
    """مدل رزرو نهایی"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    booking_ref = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=100)
    
    # اطلاعات تماس
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # مسافران
    passengers = models.TextField()  # JSON string
    
    # اقلام خریداری شده
    items = models.TextField()  # JSON string
    
    # قیمت‌ها
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)
    tax = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=0)
    
    # روش پرداخت
    payment_method = models.CharField(max_length=50, default='credit_card')
    
    # وضعیت
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.booking_ref} - {self.full_name}"
    
    def get_items_list(self):
        """دریافت لیست آیتم‌ها از JSON"""
        import json
        try:
            return json.loads(self.items)
        except:
            return []
    
    def get_item_names(self):
        """دریافت نام آیتم‌ها به صورت لیست"""
        items = self.get_items_list()
        names = []
        for item in items:
            if item.get('type') == 'flight':
                names.append(f"Flight: {item.get('name', '')}")
            elif item.get('type') == 'hotel':
                names.append(f"Hotel: {item.get('name', '')}")
        return ', '.join(names)
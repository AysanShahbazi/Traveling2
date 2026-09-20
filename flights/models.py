# flights/models.py

from django.db import models
from django.utils import timezone
from django.urls import reverse

class Airline(models.Model):
    name = models.CharField(max_length=200, verbose_name="شرکت هواپیمایی")
    code = models.CharField(max_length=10, verbose_name="کد شرکت")
    logo = models.ImageField(upload_to='airlines/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "شرکت هواپیمایی"
        verbose_name_plural = "شرکت‌های هواپیمایی"

# flights/models.py

class Airport(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام فرودگاه")
    code = models.CharField(max_length=10, unique=True, verbose_name="کد فرودگاه")
    city = models.CharField(max_length=100, verbose_name="شهر", blank=True, null=True)  # این فیلد باید باشد
    country = models.CharField(max_length=100, verbose_name="کشور", blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Flight(models.Model):
    CLASS_CHOICES = (
        ('economy', 'اقتصادی'),
        ('business', 'بیزینس'),
        ('first', 'فرست کلاس'),
    )
    
    # Flight info
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name='flights')
    flight_number = models.CharField(max_length=20, verbose_name="شماره پرواز")
    aircraft_type = models.CharField(max_length=100, blank=True, verbose_name="نوع هواپیما")
    
    # Route
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departing_flights', verbose_name="مبدا")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arriving_flights', verbose_name="مقصد")
    
    # Times
    departure_time = models.DateTimeField(verbose_name="زمان پرواز")
    arrival_time = models.DateTimeField(verbose_name="زمان arrival")
    
    # Pricing
    economy_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="قیمت اقتصادی")
    business_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="قیمت بیزینس")
    first_class_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="قیمت فرست کلاس")
    
    # Capacity
    economy_seats = models.IntegerField(default=150, verbose_name="تعداد صندلی اقتصادی")
    business_seats = models.IntegerField(default=30, verbose_name="تعداد صندلی بیزینس")
    first_class_seats = models.IntegerField(default=10, verbose_name="تعداد صندلی فرست کلاس")
    
    # Amenities
    baggage_allowance = models.IntegerField(default=30, verbose_name="بار مجاز (کیلوگرم)")
    hand_baggage = models.IntegerField(default=7, verbose_name="بار دستی (کیلوگرم)")
    has_meal = models.BooleanField(default=True, verbose_name="وعده غذایی")
    has_entertainment = models.BooleanField(default=True, verbose_name="سرگرمی")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.airline.code} {self.flight_number} - {self.origin.code} → {self.destination.code}"
    
    def get_duration(self):
        delta = self.arrival_time - self.departure_time
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f"{hours} ساعت {minutes} دقیقه"
    
    def get_price(self, class_type='economy'):
        if class_type == 'economy':
            return self.economy_price
        elif class_type == 'business':
            return self.business_price
        else:
            return self.first_class_price
    
    def get_available_seats(self, class_type='economy'):
        from bookings.models import Booking
        booked = Booking.objects.filter(flight=self, class_type=class_type).count()
        if class_type == 'economy':
            return self.economy_seats - booked
        elif class_type == 'business':
            return self.business_seats - booked
        else:
            return self.first_class_seats - booked
    
    def get_absolute_url(self):
        return reverse('flights:detail', args=[self.id])
    
    class Meta:
        verbose_name = "پرواز"
        verbose_name_plural = "پروازها"
        ordering = ['departure_time']

class Seat(models.Model):
    CLASS_CHOICES = (
        ('economy', 'اقتصادی'),
        ('business', 'بیزینس'),
        ('first', 'فرست کلاس'),
    )
    
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=5)
    class_type = models.CharField(max_length=10, choices=CLASS_CHOICES, default='economy')
    is_available = models.BooleanField(default=True)
    is_emergency = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.flight.flight_number} - صندلی {self.seat_number}"
    
    class Meta:
        unique_together = ('flight', 'seat_number')
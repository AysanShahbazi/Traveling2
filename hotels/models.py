# hotels/models.py

from django.db import models
from django.conf import settings
from django.urls import reverse


class Amenity(models.Model):
    """امکانات هتل"""
    name = models.CharField(max_length=100, verbose_name="نام امکان")
    icon = models.CharField(max_length=50, blank=True, verbose_name="آیکون")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "امکان"
        verbose_name_plural = "امکانات"


class Hotel(models.Model):
    """مدل اصلی هتل"""
    name = models.CharField(max_length=200, verbose_name="نام هتل")
    english_name = models.CharField(max_length=200, blank=True, verbose_name="نام انگلیسی")
    description = models.TextField(verbose_name="توضیحات")
    address = models.TextField(verbose_name="آدرس")
    city = models.CharField(max_length=100, verbose_name="شهر")
    country = models.CharField(max_length=100, default="ایران", verbose_name="کشور")
    
    star_rating = models.IntegerField(
        choices=[(1, '1 ستاره'), (2, '2 ستاره'), (3, '3 ستاره'), (4, '4 ستاره'), (5, '5 ستاره')], 
        verbose_name="ستاره"
    )
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0, verbose_name="امتیاز")
    review_count = models.IntegerField(default=0, verbose_name="تعداد نظرات")
    
    min_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="حداقل قیمت")
    
    amenities = models.ManyToManyField(Amenity, blank=True, verbose_name="امکانات")
    
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_featured = models.BooleanField(default=False, verbose_name="ویژه")
    
    phone = models.CharField(max_length=20, blank=True, verbose_name="تلفن")
    email = models.EmailField(blank=True, verbose_name="ایمیل")
    website = models.URLField(blank=True, verbose_name="وبسایت")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    check_in_time = models.TimeField(default="14:00", verbose_name="ساعت تحویل اتاق")
    check_out_time = models.TimeField(default="12:00", verbose_name="ساعت تخلیه")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('hotels:detail', args=[self.id])
    
    def get_star_display(self):
        return "★" * self.star_rating
    
    class Meta:
        verbose_name = "هتل"
        verbose_name_plural = "هتل‌ها"
        ordering = ['-rating', 'min_price']


class HotelImage(models.Model):
    """تصاویر هتل"""
    hotel = models.ForeignKey(Hotel, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='hotels/', verbose_name="تصویر")
    title = models.CharField(max_length=100, blank=True, verbose_name="عنوان")
    is_main = models.BooleanField(default=False, verbose_name="تصویر اصلی")
    order = models.IntegerField(default=0, verbose_name="ترتیب")
    
    def __str__(self):
        return f"{self.hotel.name} - {self.title or 'تصویر'}"
    
    class Meta:
        verbose_name = "تصویر هتل"
        verbose_name_plural = "تصاویر هتل"
        ordering = ['order', '-is_main']

class RoomType(models.Model):
    """نوع اتاق"""
    name = models.CharField(max_length=100, verbose_name="نام اتاق")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    capacity = models.IntegerField(default=2, verbose_name="ظرفیت")
    bed_type = models.CharField(max_length=100, verbose_name="نوع تخت")
    size = models.IntegerField(verbose_name="مساحت (متر مربع)")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "نوع اتاق"
        verbose_name_plural = "انواع اتاق‌ها"


class Room(models.Model):
    """اتاق‌های هتل"""
    hotel = models.ForeignKey(Hotel, related_name='rooms', on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, verbose_name="نوع اتاق")
    room_number = models.CharField(max_length=10, blank=True, verbose_name="شماره اتاق")
    
    price_per_night = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت هر شب")
    
    amenities = models.ManyToManyField(Amenity, blank=True, verbose_name="امکانات اتاق")
    
    is_available = models.BooleanField(default=True, verbose_name="موجود")
    total_rooms = models.IntegerField(default=5, verbose_name="تعداد کل اتاق‌ها")
    available_rooms = models.IntegerField(default=5, verbose_name="تعداد اتاق‌های موجود")
    
    has_window = models.BooleanField(default=True, verbose_name="دارای پنجره")
    has_balcony = models.BooleanField(default=False, verbose_name="دارای بالکن")
    has_kitchen = models.BooleanField(default=False, verbose_name="دارای آشپزخانه")
    
    def __str__(self):
        return f"{self.hotel.name} - {self.room_type.name}"
    
    def get_price_with_tax(self):
        return self.price_per_night * 1.09
    
    class Meta:
        verbose_name = "اتاق"
        verbose_name_plural = "اتاق‌ها"


class Review(models.Model):
    """نظرات کاربران"""
    hotel = models.ForeignKey(Hotel, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], verbose_name="امتیاز")
    title = models.CharField(max_length=200, verbose_name="عنوان نظر")
    comment = models.TextField(verbose_name="متن نظر")
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True, verbose_name="تأیید شده")
    
    def __str__(self):
        return f"{self.user.username} - {self.hotel.name}"
    
    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        ordering = ['-created_at']


class RoomAvailability(models.Model):
    """موجودی اتاق برای تاریخ‌های خاص"""
    room = models.ForeignKey(Room, related_name='availabilities', on_delete=models.CASCADE)
    date = models.DateField(verbose_name="تاریخ")
    is_available = models.BooleanField(default=True, verbose_name="موجود")
    available_count = models.IntegerField(default=1, verbose_name="تعداد موجود")
    special_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name="قیمت ویژه")
    
    class Meta:
        unique_together = ['room', 'date']
        verbose_name = "موجودی اتاق"
        verbose_name_plural = "موجودی اتاق‌ها"
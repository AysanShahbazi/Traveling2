# payments/models.py

from django.db import models
from django.utils import timezone
import uuid


class Payment(models.Model):
    """مدل پرداخت - متصل به Booking"""

    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت'),
        ('success', 'موفق'),
        ('failed', 'ناموفق'),
        ('refunded', 'بازگشت داده شده'),
    )

    METHOD_CHOICES = (
        ('credit_card', 'کارت اعتباری'),
        ('debit_card', 'کارت نقدی'),
        ('paypal', 'پی‌پال'),
        ('cash', 'پرداخت در محل'),
    )

    # اتصال به رزرو
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name="رزرو"
    )

    # اطلاعات پرداخت
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="شناسه تراکنش"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ")
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default='credit_card',
        verbose_name="روش پرداخت"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="وضعیت"
    )

    # اطلاعات اضافی
    card_last4 = models.CharField(max_length=4, blank=True, verbose_name="۴ رقم آخر کارت")
    error_message = models.TextField(blank=True, verbose_name="پیام خطا")

    # زمان‌ها
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ پرداخت")

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_id} - {self.booking.booking_ref} - {self.get_status_display()}"

    def mark_as_success(self, card_last4=''):
        """علامت‌گذاری پرداخت موفق"""
        self.status = 'success'
        self.paid_at = timezone.now()
        if card_last4:
            self.card_last4 = card_last4
        self.save()

    def mark_as_failed(self, error=''):
        """علامت‌گذاری پرداخت ناموفق"""
        self.status = 'failed'
        self.error_message = error
        self.save()
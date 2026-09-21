# payments/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import random
import string

from .models import Payment
from bookings.models import Booking


@login_required
def payment_process(request, booking_ref):
    """
    صفحه‌ی شبیه‌سازی پرداخت.
    کاربر کارت می‌زند و روی 'پرداخت' کلیک می‌کند.
    """
    booking = get_object_or_404(Booking, booking_ref=booking_ref)

    # چک کن که این رزرو مال همین کاربر باشد (یا ادمین باشد)
    if booking.user != request.user and not request.user.is_superuser:
        messages.error(request, 'شما به این رزرو دسترسی ندارید.')
        return redirect('pages:index')

    # اگر قبلاً پرداخت موفق داشته، برو به تاییدیه
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': booking.total,
            'method': booking.payment_method,
            'status': 'pending',
        }
    )

    if payment.status == 'success':
        return redirect('bookings:confirmation', ref=booking.booking_ref)

    if request.method == 'POST':
        # شبیه‌سازی پرداخت
        card_number = request.POST.get('card_number', '').replace(' ', '')
        cvv = request.POST.get('cvv', '')
        expiry = request.POST.get('expiry', '')

        # اعتبارسنجی ساده
        if len(card_number) < 16 or len(cvv) < 3 or not expiry:
            messages.error(request, 'اطلاعات کارت ناقص یا اشتباه است.')
            return render(request, 'payments/process.html', {
                'booking': booking,
                'payment': payment,
            })

        # شبیه‌سازی: ۹۰٪ موفق، ۱۰٪ ناموفق
        success = random.random() < 0.9

        if success:
            card_last4 = card_number[-4:]
            payment.mark_as_success(card_last4=card_last4)
            messages.success(request, 'پرداخت با موفقیت انجام شد!')
            return redirect('bookings:confirmation', ref=booking.booking_ref)
        else:
            payment.mark_as_failed('پرداخت توسط بانک رد شد (شبیه‌سازی)')
            messages.error(request, 'پرداخت ناموفق بود. لطفاً دوباره تلاش کنید.')
            return render(request, 'payments/process.html', {
                'booking': booking,
                'payment': payment,
            })

    return render(request, 'payments/process.html', {
        'booking': booking,
        'payment': payment,
    })


def payment_callback(request):
    """
    این view برای وقتی است که درگاه پرداخت واقعی callback می‌زند.
    فعلاً فقط یک پیام برمی‌گرداند.
    """
    return render(request, 'payments/callback.html')


@login_required
def payment_detail(request, transaction_id):
    """نمایش جزئیات یک پرداخت"""
    payment = get_object_or_404(Payment, transaction_id=transaction_id)

    if payment.booking.user != request.user and not request.user.is_superuser:
        messages.error(request, 'شما به این پرداخت دسترسی ندارید.')
        return redirect('pages:index')

    return render(request, 'payments/detail.html', {'payment': payment})
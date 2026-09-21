# bookings/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import random
import string
import json

from .models import Booking
from flights.models import Flight
from hotels.models import Hotel

def get_cart_items(request):
    """دریافت آیتم‌های سبد خرید از سشن"""
    cart = request.session.get('cart', [])
    items = []
    total = 0
    
    for item in cart:
        if item.get('type') == 'flight':
            try:
                flight = Flight.objects.get(id=item.get('id'))
                item_data = {
                    'type': 'flight',
                    'id': flight.id,
                    'name': f"{flight.origin.code} → {flight.destination.code}",
                    'flight_number': flight.flight_number,
                    'airline': flight.airline.name,
                    'date': flight.departure_time.strftime('%Y-%m-%d'),
                    'departure_time': flight.departure_time.strftime('%H:%M'),
                    'arrival_time': flight.arrival_time.strftime('%H:%M'),
                    'class': item.get('class', 'economy'),
                    'seat': item.get('seat', 'Not selected'),
                    'passengers': item.get('passengers', 1),
                    'price': item.get('price', 0),
                    'total_price': item.get('total_price', item.get('price', 0)),
                }
                items.append(item_data)
                total += item.get('price', 0)
            except Flight.DoesNotExist:
                pass
                
        elif item.get('type') == 'hotel':
            try:
                hotel = Hotel.objects.get(id=item.get('id'))
                item_data = {
                    'type': 'hotel',
                    'id': hotel.id,
                    'name': hotel.name,
                    'room_type': item.get('room_type', 'Standard Room'),
                    'nights': item.get('nights', 1),
                    'rooms': item.get('rooms', 1),
                    'adults': item.get('adults', 2),
                    'children': item.get('children', 0),
                    'check_in': item.get('check_in', ''),
                    'check_out': item.get('check_out', ''),
                    'price_per_night': item.get('price_per_night', 0),
                    'total_price': item.get('total_price', 0),
                }
                items.append(item_data)
                total += item.get('total_price', 0)
            except Hotel.DoesNotExist:
                pass
    
    return items, total


def cart_view(request):
    """Display cart page"""
    cart = request.session.get('cart', [])
    items, total = get_cart_items(request)
    
    context = {
        'cart_items': items,
        'total': total,
        'total_amount': total,
    }
    return render(request, 'bookings/cart.html', context)


@login_required
def add_to_cart(request):
    """افزودن آیتم به سبد خرید"""
    if request.method == 'POST':
        item_type = request.POST.get('type')
        item_id = request.POST.get('id')
        price = request.POST.get('price')
        
        cart = request.session.get('cart', [])
        
        # بررسی تکراری نبودن
        exists = False
        for item in cart:
            if item.get('type') == item_type and item.get('id') == int(item_id):
                exists = True
                break
        
        if not exists:
            new_item = {
                'type': item_type,
                'id': int(item_id),
            }
            
            if item_type == 'flight':
                new_item.update({
                    'price': int(price),
                    'date': request.POST.get('date', ''),
                    'passengers': int(request.POST.get('passengers', 1)),
                    'class': request.POST.get('class', 'economy'),
                    'seat': request.POST.get('seat', ''),
                })
            else:  # hotel
                nights = int(request.POST.get('nights', 1))
                rooms = int(request.POST.get('rooms', 1))
                price_per_night = int(price)
                new_item.update({
                    'room_type': request.POST.get('room_type', 'Standard Room'),
                    'price_per_night': price_per_night,
                    'nights': nights,
                    'rooms': rooms,
                    'adults': int(request.POST.get('adults', 2)),
                    'children': int(request.POST.get('children', 0)),
                    'check_in': request.POST.get('check_in', ''),
                    'check_out': request.POST.get('check_out', ''),
                    'total_price': price_per_night * nights * rooms,
                })
            
            cart.append(new_item)
            request.session['cart'] = cart
            messages.success(request, 'Item added to cart!')
        else:
            messages.warning(request, 'Item already in cart!')
    
    return redirect(request.META.get('HTTP_REFERER', 'pages:index'))


def remove_from_cart(request):
    """Remove item from cart"""
    if request.method == 'POST':
        index = int(request.POST.get('index', -1))
        cart = request.session.get('cart', [])
        
        if 0 <= index < len(cart):
            cart.pop(index)
            request.session['cart'] = cart
            messages.success(request, 'Item removed from cart!')
    
    return redirect('bookings:cart')


@login_required
def checkout(request):
    """Checkout page"""
    cart = request.session.get('cart', [])
    items, total = get_cart_items(request)
    
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('bookings:cart')
    
    if request.method == 'POST':
        # Save checkout info to session
        request.session['checkout_info'] = {
            'full_name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'payment_method': request.POST.get('payment_method', 'credit_card'),
        }
        
        # Save passengers info
        passengers = []
        for i in range(1, 10):
            first_name = request.POST.get(f'first_name_{i}')
            last_name = request.POST.get(f'last_name_{i}')
            passport = request.POST.get(f'passport_{i}')
            if first_name and last_name:
                passengers.append({
                    'first_name': first_name,
                    'last_name': last_name,
                    'full_name': f"{first_name} {last_name}",
                    'passport': passport
                })
        
        request.session['checkout_info']['passengers'] = passengers
        
        return redirect('bookings:confirm_booking')
    
    context = {
        'cart_items': items,
        'total': total,
    }
    return render(request, 'bookings/checkout.html', context)


@login_required
def confirm_booking(request):
    """Confirm booking page"""
    cart = request.session.get('cart', [])
    checkout_info = request.session.get('checkout_info', {})
    items, total = get_cart_items(request)
    
    if not cart or not checkout_info:
        return redirect('bookings:cart')
    
    # Generate booking reference
    booking_ref = generate_booking_ref()
    
    # Save booking to database
    booking = Booking.objects.create(
        booking_ref=booking_ref,
        user=request.user,
        session_key=request.session.session_key,
        full_name=checkout_info.get('full_name', ''),
        email=checkout_info.get('email', ''),
        phone=checkout_info.get('phone', ''),
        passengers=json.dumps(checkout_info.get('passengers', [])),
        items=json.dumps(items),  # این شامل هتل و پرواز می‌شود
        subtotal=total,
        tax=int(total * 0.09),
        discount=0,
        total=int(total * 1.09),
        payment_method=checkout_info.get('payment_method', 'credit_card'),
        status='confirmed'
    )
    
    # Clear cart
    request.session['cart'] = []
    request.session['checkout_info'] = {}
    
        # هدایت به صفحه‌ی پرداخت
    return redirect('payments:process', booking_ref=booking_ref)


def generate_booking_ref():
    """Generate unique booking reference"""
    return 'TRV-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def confirmation(request, ref):
    """Confirmation page"""
    booking = get_object_or_404(Booking, booking_ref=ref)
    items = json.loads(booking.items)
    
    context = {
        'booking_ref': booking.booking_ref,
        'total': booking.total,
        'checkout_info': {
            'full_name': booking.full_name,
            'email': booking.email,
            'phone': booking.phone,
        },
        'cart_items': items,
    }
    return render(request, 'bookings/confirmation.html', context)
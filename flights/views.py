# flights/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Flight, Airport, Airline

# اضافه کردن این توابع به انتهای فایل flights/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def api_seat_status(request, flight_id):
    """API برای دریافت وضعیت صندلی‌های پرواز"""
    from bookings.models import Booking
    
    flight = get_object_or_404(Flight, id=flight_id)
    seat_status = {}
    
    # دریافت صندلی‌های خریداری شده (confirmed) از دیتابیس
    try:
        confirmed_bookings = Booking.objects.filter(status='confirmed')
        for booking in confirmed_bookings:
            if booking.items:
                try:
                    items = json.loads(booking.items)
                    for item in items:
                        if item.get('type') == 'flight' and item.get('id') == flight_id:
                            seats = item.get('seat', '')
                            if seats:
                                for seat in seats.split(','):
                                    seat = seat.strip()
                                    if seat:
                                        seat_status[seat] = {
                                            'status': 'purchased',
                                            'user': booking.user.username if booking.user and booking.user.username else 'User'
                                        }
                except:
                    pass
    except:
        pass
    
    # دریافت صندلی‌های در سبد خرید (pending) از session
    cart = request.session.get('cart', [])
    for item in cart:
        if item.get('type') == 'flight' and item.get('id') == flight_id:
            seats = item.get('seat', '')
            if seats:
                for seat in seats.split(','):
                    seat = seat.strip()
                    if seat and seat not in seat_status:
                        seat_status[seat] = {
                            'status': 'booked',
                            'user': request.user.username if request.user.is_authenticated else 'Guest'
                        }
    
    return JsonResponse(seat_status)


@csrf_exempt
def api_update_seat(request):
    """API برای به‌روزرسانی وضعیت صندلی"""
    if request.method == 'POST':
        flight_id = request.POST.get('flight_id')
        seat_number = request.POST.get('seat_number')
        action = request.POST.get('action')
        
        if not flight_id or not seat_number:
            return JsonResponse({'status': 'error', 'message': 'Missing parameters'}, status=400)
        
        flight_id = int(flight_id)
        cart = request.session.get('cart', [])
        found = False
        
        if action == 'booked':
            # اضافه کردن صندلی به سبد خرید
            for item in cart:
                if item.get('type') == 'flight' and item.get('id') == flight_id:
                    current_seats = item.get('seat', '')
                    seats_list = current_seats.split(',') if current_seats else []
                    if seat_number not in seats_list:
                        seats_list.append(seat_number)
                        item['seat'] = ','.join(filter(None, seats_list))
                    found = True
                    break
            
            if not found:
                # اگر پرواز در سبد خرید نیست، یک آیتم جدید ایجاد کن
                cart.append({
                    'type': 'flight',
                    'id': flight_id,
                    'seat': seat_number,
                    'passengers': 1
                })
        
        elif action == 'available':
            # حذف صندلی از سبد خرید
            for item in cart:
                if item.get('type') == 'flight' and item.get('id') == flight_id:
                    current_seats = item.get('seat', '')
                    seats_list = current_seats.split(',') if current_seats else []
                    if seat_number in seats_list:
                        seats_list.remove(seat_number)
                        item['seat'] = ','.join(filter(None, seats_list))
                    found = True
                    break
        
        request.session['cart'] = cart
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


def add_to_cart(request, flight_id):
    if request.method == 'POST':
        flight = get_object_or_404(Flight, id=flight_id)
        
        class_type = request.POST.get('class_type', 'economy')
        seat_number = request.POST.get('seat_number', '')
        passenger_count = int(request.POST.get('passenger_count', 1))
        
        if class_type == 'economy':
            price = int(flight.economy_price)
        elif class_type == 'business':
            price = int(flight.business_price)
        else:
            price = int(flight.first_class_price)
        
        total_price = price * passenger_count
        
        cart_item = {
            'type': 'flight',
            'id': flight.id,
            'name': f'{flight.origin.code} → {flight.destination.code}',
            'flight_number': flight.flight_number,
            'airline': flight.airline.name,
            'date': flight.departure_time.strftime('%Y-%m-%d'),
            'departure_time': flight.departure_time.strftime('%H:%M'),
            'arrival_time': flight.arrival_time.strftime('%H:%M'),
            'class': class_type,
            'seat': seat_number,
            'passengers': passenger_count,
            'price': price,
            'total_price': total_price,
        }
        
        cart = request.session.get('cart', [])
        cart.append(cart_item)
        request.session['cart'] = cart
        
        messages.success(request, f'Flight {flight.flight_number} added to cart!')
        return redirect('bookings:cart')
    
    return redirect('flights:detail', flight_id=flight_id)


def search_flights(request):
    """Flight search page with results"""
    airports = Airport.objects.all()
    flights = Flight.objects.filter(is_active=True)
    
    # دریافت پارامترهای جستجو
    origin_code = request.GET.get('origin', '')
    destination_code = request.GET.get('destination', '')
    departure_date = request.GET.get('departure_date', '')
    trip_type = request.GET.get('trip_type', 'one_way')
    return_date = request.GET.get('return_date', '')
    adults = int(request.GET.get('adults', 1))
    children = int(request.GET.get('children', 0))
    infants = int(request.GET.get('infants', 0))
    travel_class = request.GET.get('class', 'economy')
    sort_by = request.GET.get('sort', 'recommended')
    
    # اعمال فیلترها
    if origin_code:
        flights = flights.filter(origin__code__icontains=origin_code)
    if destination_code:
        flights = flights.filter(destination__code__icontains=destination_code)
    if departure_date:
        flights = flights.filter(departure_time__date=departure_date)
    
    # مرتب‌سازی
    if sort_by == 'price':
        flights = flights.order_by('economy_price')
    elif sort_by == 'duration':
        flights = sorted(flights, key=lambda f: (f.arrival_time - f.departure_time).seconds)
    else:  # recommended
        flights = flights.order_by('-departure_time')
    
    # Pagination - 5 نتیجه در هر صفحه
    paginator = Paginator(flights, 5)
    page_number = request.GET.get('page', 1)
    flights_page = paginator.get_page(page_number)
    
    total_passengers = adults + children + infants
    
    # محاسبه has_results برای نمایش نتایج
    has_results = len(flights) > 0 and (origin_code or destination_code or departure_date)
    
    context = {
        'flights': flights_page,  # صفحه‌بندی شده
        'airports': airports,
        'origin': origin_code,
        'destination': destination_code,
        'departure_date': departure_date,
        'trip_type': trip_type,
        'return_date': return_date,
        'adults': adults,
        'children': children,
        'infants': infants,
        'total_passengers': total_passengers,
        'travel_class': travel_class,
        'sort_by': sort_by,
        'has_results': has_results,  # اضافه شد
        'total_count': paginator.count,  # تعداد کل نتایج
    }
    return render(request, 'flights/search.html', context)


def flight_results(request):
    """Flight results page"""
    flights = Flight.objects.filter(is_active=True).order_by('departure_time')
    
    origin = request.GET.get('origin', '')
    destination = request.GET.get('destination', '')
    departure_date = request.GET.get('departure_date', '')
    adults = int(request.GET.get('adults', 2))
    
    if origin:
        flights = flights.filter(origin__code=origin)
    if destination:
        flights = flights.filter(destination__code=destination)
    if departure_date:
        flights = flights.filter(departure_time__date=departure_date)
    
    paginator = Paginator(flights, 10)
    page = request.GET.get('page', 1)
    flights = paginator.get_page(page)
    
    airlines = Airline.objects.filter(flights__is_active=True).distinct()
    
    context = {
        'flights': flights,
        'origin': origin,
        'destination': destination,
        'departure_date': departure_date,
        'adults': adults,
        'airlines': airlines,
        'total_count': paginator.count,
    }
    return render(request, 'flights/results.html', context)


def flight_detail(request, flight_id):
    """Flight detail page with seat selection"""
    flight = get_object_or_404(Flight, id=flight_id, is_active=True)
    
    economy_price = flight.economy_price if flight.economy_price else 0
    business_price = flight.business_price if flight.business_price else 0
    first_class_price = flight.first_class_price if flight.first_class_price else 0
    
    aircraft_type = flight.aircraft_type if flight.aircraft_type else "Boeing 737"
    has_meal = flight.has_meal if flight.has_meal is not None else False
    
    context = {
        'flight': flight,
        'economy_price': economy_price,
        'business_price': business_price,
        'first_class_price': first_class_price,
        'aircraft_type': aircraft_type,
        'has_meal': has_meal,
    }
    return render(request, 'flights/detail.html', context)


def all_flights(request):
    """Show all available flights with pagination"""
    flights = Flight.objects.filter(is_active=True).order_by('departure_time')
    
    origin_filter = request.GET.get('origin', '')
    if origin_filter:
        flights = flights.filter(origin__code__icontains=origin_filter)
    
    dest_filter = request.GET.get('destination', '')
    if dest_filter:
        flights = flights.filter(destination__code__icontains=dest_filter)
    
    paginator = Paginator(flights, 5)
    page_number = request.GET.get('page', 1)
    flights_page = paginator.get_page(page_number)
    
    context = {
        'flights': flights_page,
        'origin_filter': origin_filter,
        'dest_filter': dest_filter,
        'total_count': paginator.count,
    }
    return render(request, 'flights/all_flights.html', context)


def passenger_info(request, flight_id):
    """Passenger information page"""
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        class_type = request.POST.get('class_type')
        seat_number = request.POST.get('seat_number')
        passenger_count = int(request.POST.get('passenger_count', 1))
        
        if class_type == 'economy':
            unit_price = flight.economy_price or 0
        elif class_type == 'business':
            unit_price = flight.business_price or 0
        else:
            unit_price = flight.first_class_price or 0
        
        total_price = unit_price * passenger_count
        
        context = {
            'flight': flight,
            'class_type': class_type,
            'seat_number': seat_number,
            'passenger_count': passenger_count,
            'total_price': total_price,
            'passenger_range': range(1, passenger_count + 1),
        }
        return render(request, 'flights/passenger_info.html', context)
    
    return redirect('flights:detail', flight_id=flight_id)


def booking_review(request, flight_id):
    """Review booking page"""
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        class_type = request.POST.get('class_type')
        seat_number = request.POST.get('seat_number')
        passenger_count = int(request.POST.get('passenger_count'))
        total_price = int(request.POST.get('total_price'))
        
        passengers = []
        for i in range(1, passenger_count + 1):
            name = request.POST.get(f'full_name_{i}')
            id_number = request.POST.get(f'id_number_{i}')
            passengers.append({'name': name, 'id_number': id_number})
        
        if class_type == 'economy':
            unit_price = flight.economy_price or 0
        elif class_type == 'business':
            unit_price = flight.business_price or 0
        else:
            unit_price = flight.first_class_price or 0
        
        context = {
            'flight': flight,
            'class_type': class_type,
            'seat_number': seat_number,
            'passenger_count': passenger_count,
            'passengers': passengers,
            'total_price': total_price,
            'unit_price': unit_price,
        }
        return render(request, 'flights/booking_review.html', context)
    
    return redirect('flights:detail', flight_id=flight_id)


def confirm_booking(request, flight_id):
    """Confirm booking page"""
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        class_type = request.POST.get('class_type')
        seat_number = request.POST.get('seat_number')
        passenger_count = int(request.POST.get('passenger_count'))
        total_price = request.POST.get('total_price')
        
        import random
        import string
        booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        messages.success(request, f'Booking confirmed! Reference: {booking_ref}')
        
        context = {
            'booking_ref': booking_ref,
            'flight': flight,
        }
        return render(request, 'flights/booking_confirmation.html', context)
    
    return redirect('flights:all_flights')


@staff_member_required
def admin_flights(request):
    """Admin flight management page"""
    flights = Flight.objects.all().order_by('-departure_time')
    context = {
        'flights': flights,
        'total_count': flights.count(),
    }
    return render(request, 'admin/flights/list.html', context)


@staff_member_required
def admin_flight_add(request):
    """Add flight admin page"""
    if request.method == 'POST':
        try:
            flight = Flight(
                airline_id=request.POST.get('airline'),
                flight_number=request.POST.get('flight_number'),
                aircraft_type=request.POST.get('aircraft_type', ''),
                origin_id=request.POST.get('origin'),
                destination_id=request.POST.get('destination'),
                departure_time=request.POST.get('departure_time'),
                arrival_time=request.POST.get('arrival_time'),
                economy_price=request.POST.get('economy_price', 0),
                business_price=request.POST.get('business_price', 0),
                first_class_price=request.POST.get('first_class_price', 0),
                economy_seats=request.POST.get('economy_seats', 150),
                business_seats=request.POST.get('business_seats', 30),
                first_class_seats=request.POST.get('first_class_seats', 10),
                baggage_allowance=request.POST.get('baggage_allowance', 30),
                hand_baggage=request.POST.get('hand_baggage', 7),
                has_meal=request.POST.get('has_meal') == 'on',
                has_entertainment=request.POST.get('has_entertainment') == 'on',
                is_active=request.POST.get('is_active') == 'on',
            )
            flight.save()
            messages.success(request, 'پرواز با موفقیت اضافه شد!')
            return redirect('flights:admin_flights')
        except Exception as e:
            messages.error(request, f'خطا در افزودن پرواز: {str(e)}')
    
    airlines = Airline.objects.filter(is_active=True)
    airports = Airport.objects.all()
    context = {
        'airlines': airlines,
        'airports': airports,
        'action': 'Add',
        'flight': None,
    }
    return render(request, 'admin/flights/form.html', context)


@staff_member_required
def admin_flight_edit(request, flight_id):
    """Edit flight admin page"""
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        try:
            flight.airline_id = request.POST.get('airline')
            flight.flight_number = request.POST.get('flight_number')
            flight.aircraft_type = request.POST.get('aircraft_type', '')
            flight.origin_id = request.POST.get('origin')
            flight.destination_id = request.POST.get('destination')
            flight.departure_time = request.POST.get('departure_time')
            flight.arrival_time = request.POST.get('arrival_time')
            flight.economy_price = request.POST.get('economy_price', 0)
            flight.business_price = request.POST.get('business_price', 0)
            flight.first_class_price = request.POST.get('first_class_price', 0)
            flight.economy_seats = request.POST.get('economy_seats', 150)
            flight.business_seats = request.POST.get('business_seats', 30)
            flight.first_class_seats = request.POST.get('first_class_seats', 10)
            flight.baggage_allowance = request.POST.get('baggage_allowance', 30)
            flight.hand_baggage = request.POST.get('hand_baggage', 7)
            flight.has_meal = request.POST.get('has_meal') == 'on'
            flight.has_entertainment = request.POST.get('has_entertainment') == 'on'
            flight.is_active = request.POST.get('is_active') == 'on'
            flight.save()
            messages.success(request, 'پرواز با موفقیت ویرایش شد!')
            return redirect('flights:admin_flights')
        except Exception as e:
            messages.error(request, f'خطا در ویرایش پرواز: {str(e)}')
    
    airlines = Airline.objects.filter(is_active=True)
    airports = Airport.objects.all()
    context = {
        'flight': flight,
        'airlines': airlines,
        'airports': airports,
        'action': 'Edit',
    }
    return render(request, 'admin/flights/form.html', context)


@staff_member_required
def admin_flight_delete(request, flight_id):
    """Delete flight admin page"""
    flight = get_object_or_404(Flight, id=flight_id)
    flight.delete()
    messages.success(request, 'پرواز با موفقیت حذف شد!')
    return redirect('flights:admin_flights')
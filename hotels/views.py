# hotels/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Hotel, Room, RoomType, Amenity, Review, HotelImage



def search_hotels(request):
    """Search hotels page"""
    hotels = Hotel.objects.filter(is_active=True)
    
    # Get search parameters
    destination = request.GET.get('destination', '')
    check_in = request.GET.get('check_in', '')
    check_out = request.GET.get('check_out', '')
    guests = int(request.GET.get('guests', 2))
    
    # Filter by destination
    if destination:
        hotels = hotels.filter(
            Q(name__icontains=destination) | 
            Q(city__icontains=destination) | 
            Q(address__icontains=destination)
        )
    
    # Filter by star rating
    stars = request.GET.getlist('stars')
    if stars:
        hotels = hotels.filter(star_rating__in=stars)
    
    # Filter by amenities
    amenities = request.GET.getlist('amenities')
    if amenities:
        for amenity in amenities:
            hotels = hotels.filter(amenities__name__icontains=amenity)
    
    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        hotels = hotels.filter(min_price__gte=min_price)
    if max_price:
        hotels = hotels.filter(min_price__lte=max_price)
    
    # Sort
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'price_asc':
        hotels = hotels.order_by('min_price')
    elif sort_by == 'price_desc':
        hotels = hotels.order_by('-min_price')
    elif sort_by == 'rating_desc':
        hotels = hotels.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    
    # Pagination
    paginator = Paginator(hotels, 6)
    page = request.GET.get('page', 1)
    hotels_page = paginator.get_page(page)
    
    # Get all amenities for filter
    all_amenities = Amenity.objects.all()
    
    context = {
        'hotels': hotels_page,
        'destination': destination,
        'check_in': check_in,
        'check_out': check_out,
        'guests': guests,
        'total_count': paginator.count,
        'all_amenities': all_amenities,
        'selected_stars': stars,
        'selected_amenities': amenities,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    return render(request, 'hotels/search.html', context)

def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, is_active=True)

    # اتاق‌ها
    rooms = hotel.rooms.filter(is_available=True).select_related('room_type')

    # گرفتن room_typeهای یکتای این هتل
    room_types = RoomType.objects.filter(room__hotel=hotel).distinct()

    # نظرات تأییدشده
    approved_reviews = hotel.reviews.filter(is_approved=True).select_related('user')
    reviews = approved_reviews[:5]
    review_count = approved_reviews.count()

    # تصاویر
    images = hotel.images.all()

    # امکانات
    amenities = hotel.amenities.all()

    context = {
        'hotel': hotel,
        'rooms': rooms,
        'room_types': room_types,
        'reviews': reviews,
        'review_count': review_count,
        'images': images,
        'amenities': amenities,
    }
    return render(request, 'hotels/detail.html', context)

def add_to_cart(request, hotel_id):
    """Add hotel booking to cart"""
    if request.method == 'POST':
        hotel = get_object_or_404(Hotel, id=hotel_id)
        
        # دریافت اطلاعات از فرم
        room_type = request.POST.get('room_type')
        price_per_night = int(request.POST.get('price_per_night', 0))
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        adults = int(request.POST.get('adults', 2))
        children = int(request.POST.get('children', 0))
        rooms_count = int(request.POST.get('rooms', 1))
        
        # محاسبه تعداد شب‌ها
        from datetime import datetime
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
        nights = (check_out_date - check_in_date).days
        
        # محاسبه کل قیمت
        total_price = price_per_night * nights * rooms_count
        
        # ایجاد آیتم برای سبد خرید
        cart_item = {
            'type': 'hotel',
            'id': hotel.id,
            'name': hotel.name,
            'room_type': room_type,
            'price_per_night': price_per_night,
            'nights': nights,
            'rooms': rooms_count,
            'adults': adults,
            'children': children,
            'check_in': check_in,
            'check_out': check_out,
            'total_price': total_price,
            'image': hotel.images.first().image.url if hotel.images.first() else '/static/img/hotel-default.jpg'
        }
        
        # اضافه کردن به سشن (سبد خرید)
        cart = request.session.get('cart', [])
        cart.append(cart_item)
        request.session['cart'] = cart
        
        messages.success(request, f'{hotel.name} - {room_type} added to cart!')
        return redirect('bookings:cart')
    
    return redirect('hotels:detail', hotel_id=hotel_id)

def all_hotels(request):
    """Show all available hotels with pagination"""
    hotels = Hotel.objects.filter(is_active=True).order_by('-created_at')
    
    # Filter by city
    city_filter = request.GET.get('city', '')
    if city_filter:
        hotels = hotels.filter(city__icontains=city_filter)
    
    # Pagination
    paginator = Paginator(hotels, 6)
    page_number = request.GET.get('page', 1)
    hotels_page = paginator.get_page(page_number)
    
    context = {
        'hotels': hotels_page,
        'city_filter': city_filter,
        'total_count': paginator.count,
    }
    return render(request, 'hotels/all_hotels.html', context)


# Admin views
@staff_member_required
def admin_hotels(request):
    """Admin hotel management page"""
    hotels = Hotel.objects.all().order_by('-created_at')
    context = {
        'hotels': hotels,
        'total_count': hotels.count(),
    }
    return render(request, 'admin/hotels/list.html', context)

@staff_member_required
def admin_hotel_add(request):
    """Add hotel admin page"""
    if request.method == 'POST':
        try:
            is_active = request.POST.get('is_active') == 'on'
            
            hotel = Hotel(
                name=request.POST.get('name'),
                english_name=request.POST.get('english_name', ''),
                description=request.POST.get('description'),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                country=request.POST.get('country', 'Iran'),
                star_rating=request.POST.get('star_rating', 3),
                min_price=request.POST.get('min_price', 0),
                phone=request.POST.get('phone', ''),
                email=request.POST.get('email', ''),
                website=request.POST.get('website', ''),
                check_in_time=request.POST.get('check_in_time', '14:00'),
                check_out_time=request.POST.get('check_out_time', '12:00'),
                is_active=is_active,
            )
            hotel.save()
            
            # ذخیره تصاویر
            if 'main_image' in request.FILES:
                HotelImage.objects.create(
                    hotel=hotel,
                    image=request.FILES['main_image'],
                    title='Main Image',
                    is_main=True,
                    order=0
                )
            
            if 'additional_images' in request.FILES:
                images = request.FILES.getlist('additional_images')
                for i, img in enumerate(images):
                    HotelImage.objects.create(
                        hotel=hotel,
                        image=img,
                        title=f'Image {i+1}',
                        is_main=False,
                        order=i+1
                    )
            
            # ذخیره امکانات
            amenities_text = request.POST.get('amenities_text', '')
            if amenities_text:
                amenity_names = [a.strip() for a in amenities_text.split(',') if a.strip()]
                for name in amenity_names:
                    amenity, _ = Amenity.objects.get_or_create(name=name)
                    hotel.amenities.add(amenity)
            
            messages.success(request, 'Hotel added successfully!')
            return redirect('hotels:admin_hotels')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    context = {
        'action': 'Add',
        'hotel': None,
        'is_checked': 'checked',
        'amenities_text': '',
    }
    return render(request, 'admin/hotels/form.html', context)


@staff_member_required
def admin_hotel_edit(request, hotel_id):
    """Edit hotel admin page"""
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    if request.method == 'POST':
        try:
            is_active = request.POST.get('is_active') == 'on'
            
            hotel.name = request.POST.get('name')
            hotel.english_name = request.POST.get('english_name', '')
            hotel.description = request.POST.get('description')
            hotel.address = request.POST.get('address')
            hotel.city = request.POST.get('city')
            hotel.country = request.POST.get('country', 'Iran')
            hotel.star_rating = request.POST.get('star_rating', 3)
            hotel.min_price = request.POST.get('min_price', 0)
            hotel.phone = request.POST.get('phone', '')
            hotel.email = request.POST.get('email', '')
            hotel.website = request.POST.get('website', '')
            hotel.check_in_time = request.POST.get('check_in_time', '14:00')
            hotel.check_out_time = request.POST.get('check_out_time', '12:00')
            hotel.is_active = is_active
            hotel.save()
            
            # ذخیره تصاویر جدید
            if 'main_image' in request.FILES:
                hotel.images.filter(is_main=True).delete()
                HotelImage.objects.create(
                    hotel=hotel,
                    image=request.FILES['main_image'],
                    title='Main Image',
                    is_main=True,
                    order=0
                )
            
            if 'additional_images' in request.FILES:
                images = request.FILES.getlist('additional_images')
                current_count = hotel.images.filter(is_main=False).count()
                for i, img in enumerate(images):
                    HotelImage.objects.create(
                        hotel=hotel,
                        image=img,
                        title=f'Image {current_count + i + 1}',
                        is_main=False,
                        order=current_count + i + 1
                    )
            
            # به روز رسانی امکانات
            # حذف امکانات قبلی
            hotel.amenities.clear()
            amenities_text = request.POST.get('amenities_text', '')
            if amenities_text:
                amenity_names = [a.strip() for a in amenities_text.split(',') if a.strip()]
                for name in amenity_names:
                    amenity, _ = Amenity.objects.get_or_create(name=name)
                    hotel.amenities.add(amenity)
            
            messages.success(request, 'Hotel updated successfully!')
            return redirect('hotels:admin_hotels')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    # آماده سازی متن امکانات برای نمایش
    amenities_text = ', '.join([a.name for a in hotel.amenities.all()])
    is_checked = 'checked' if hotel.is_active else ''
    
    context = {
        'hotel': hotel,
        'action': 'Edit',
        'is_checked': is_checked,
        'amenities_text': amenities_text,
    }
    return render(request, 'admin/hotels/form.html', context)

@staff_member_required
def admin_hotel_edit(request, hotel_id):
    """Edit hotel admin page with image upload"""
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    if request.method == 'POST':
        try:
            hotel.name = request.POST.get('name')
            hotel.english_name = request.POST.get('english_name', '')
            hotel.description = request.POST.get('description')
            hotel.address = request.POST.get('address')
            hotel.city = request.POST.get('city')
            hotel.country = request.POST.get('country', 'Iran')
            hotel.star_rating = request.POST.get('star_rating', 3)
            hotel.min_price = request.POST.get('min_price', 0)
            hotel.phone = request.POST.get('phone', '')
            hotel.email = request.POST.get('email', '')
            hotel.website = request.POST.get('website', '')
            hotel.check_in_time = request.POST.get('check_in_time', '14:00')
            hotel.check_out_time = request.POST.get('check_out_time', '12:00')
            hotel.is_active = request.POST.get('is_active') == 'on'
            hotel.save()
            
            # ذخیره تصویر اصلی جدید
            if 'main_image' in request.FILES:
                # حذف تصویر اصلی قبلی
                hotel.images.filter(is_main=True).delete()
                HotelImage.objects.create(
                    hotel=hotel,
                    image=request.FILES['main_image'],
                    title='Main Image',
                    is_main=True,
                    order=0
                )
            
            # ذخیره تصاویر اضافی جدید
            if 'additional_images' in request.FILES:
                images = request.FILES.getlist('additional_images')
                current_count = hotel.images.filter(is_main=False).count()
                for i, img in enumerate(images):
                    HotelImage.objects.create(
                        hotel=hotel,
                        image=img,
                        title=f'Image {current_count + i + 1}',
                        is_main=False,
                        order=current_count + i + 1
                    )
            
            # ذخیره امکانات
            amenities_list = request.POST.getlist('amenities')
            if amenities_list:
                hotel.amenities.set(amenities_list)
            
            messages.success(request, 'Hotel updated successfully!')
            return redirect('hotels:admin_hotels')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    amenities = Amenity.objects.all()
    context = {
        'hotel': hotel,
        'amenities': amenities,
        'action': 'Edit',
    }
    return render(request, 'admin/hotels/form.html', context)

@staff_member_required
def admin_hotel_delete(request, hotel_id):
    """Delete hotel admin page"""
    hotel = get_object_or_404(Hotel, id=hotel_id)
    hotel_name = hotel.name
    hotel.delete()
    messages.success(request, f'Hotel "{hotel_name}" deleted successfully!')
    return redirect('hotels:admin_hotels')
# pages/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from datetime import datetime
import random
import string
import json

from .models import Banner, Destination, Service, AboutSection
from .decorators import admin_required
from blog.models import BlogPost, Category
from accounts.models import UserProfile
from django.contrib.auth.models import User
from bookings.models import Booking


def index(request):
    """Homepage view"""
    banner = Banner.objects.filter(is_active=True).first()
    destinations = Destination.objects.filter(is_active=True)[:3]
    services = Service.objects.filter(is_active=True)[:4]
    about = AboutSection.objects.filter(is_active=True).first()
    blog_posts = BlogPost.objects.filter(is_active=True)[:6]
    
    context = {
        'banner': banner,
        'destinations': destinations,
        'services': services,
        'about': about,
        'blog_posts': blog_posts,
    }
    return render(request, 'pages/index.html', context)


def about(request):
    """About page view"""
    from .models import AboutSection
    
    about_section = AboutSection.objects.filter(is_active=True).first()
    services = Service.objects.filter(is_active=True)[:4]
    
    context = {
        'about_section': about_section,
        'services': services,
    }
    return render(request, 'pages/about.html', context)

@admin_required
def manage_about(request):
    about_sections = AboutSection.objects.all()
    return render(request, 'admin/about/list.html', {'about_sections': about_sections})

@admin_required
def add_about(request):
    if request.method == 'POST':
        about = AboutSection(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            button_text=request.POST.get('button_text', ''),
            button_link=request.POST.get('button_link', ''),
            is_active=request.POST.get('is_active') == 'on'
        )
        if 'image' in request.FILES:
            about.image = request.FILES['image']
        about.save()
        messages.success(request, 'About section added!')
        return redirect('pages:manage_about')
    
    return render(request, 'admin/about/form.html', {
        'action': 'Add',
        'about': None,
    })

@admin_required
def edit_about(request, pk):
    about = get_object_or_404(AboutSection, pk=pk)
    if request.method == 'POST':
        about.title = request.POST.get('title')
        about.description = request.POST.get('description')
        about.button_text = request.POST.get('button_text', '')
        about.button_link = request.POST.get('button_link', '')
        about.is_active = request.POST.get('is_active') == 'on'
        if 'image' in request.FILES:
            about.image = request.FILES['image']
        about.save()
        messages.success(request, 'About section updated!')
        return redirect('pages:manage_about')
    
    return render(request, 'admin/about/form.html', {
        'about': about,
        'action': 'Edit',
    })

@admin_required
def delete_about(request, pk):
    about = get_object_or_404(AboutSection, pk=pk)
    about.delete()
    messages.success(request, 'About section deleted!')
    return redirect('pages:manage_about')


def contact(request):
    """Contact page view with email sending capability"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if not all([name, email, subject, message]):
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'pages/contact.html', {'form_data': request.POST})
        
        email_subject = f"Contact Form: {subject}"
        email_message = f"""
        Name: {name}
        Email: {email}
        
        Message:
        {message}
        """
        
        try:
            send_mail(
                email_subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
            return redirect('pages:contact')
        except Exception as e:
            messages.error(request, 'An error occurred while sending your message. Please try again later.')
            return render(request, 'pages/contact.html', {'form_data': request.POST})
    
    return render(request, 'pages/contact.html')


def elements(request):
    """Elements page view"""
    return render(request, 'pages/elements.html')


# ==================== ADMIN DASHBOARD ====================

@admin_required
def admin_dashboard(request):
    from bookings.models import Booking
    from flights.models import Flight
    from hotels.models import Hotel
    from django.contrib.auth.models import User
    
    context = {
        'banners_count': Banner.objects.count(),
        'destinations_count': Destination.objects.count(),
        'services_count': Service.objects.count(),
        'blog_posts_count': BlogPost.objects.count(),
        'about_count': AboutSection.objects.count(),
        'bookings_count': Booking.objects.count(),
        'flights_count': Flight.objects.count(),
        'hotels_count': Hotel.objects.count(),
        'users_count': User.objects.count(),
    }
    return render(request, 'admin/dashboard.html', context)


# ==================== BANNER MANAGEMENT ====================

@admin_required
def manage_banners(request):
    banners = Banner.objects.all().order_by('-created_at')
    return render(request, 'admin/banners/list.html', {'banners': banners})


@admin_required
def add_banner(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'
        
        banner = Banner(
            title=title,
            subtitle=subtitle,
            description=description,
            is_active=is_active
        )
        
        if 'background_image' in request.FILES:
            banner.background_image = request.FILES['background_image']
        
        banner.save()
        messages.success(request, 'Banner added successfully!')
        return redirect('pages:manage_banners')
    
    return render(request, 'admin/banners/form.html', {
        'action': 'Add',
        'banner': None,
        'is_checked': 'checked'
    })


@admin_required
def edit_banner(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        banner.title = request.POST.get('title')
        banner.subtitle = request.POST.get('subtitle')
        banner.description = request.POST.get('description')
        banner.is_active = request.POST.get('is_active') == 'on'
        
        if 'background_image' in request.FILES:
            banner.background_image = request.FILES['background_image']
        
        banner.save()
        messages.success(request, 'Banner updated successfully!')
        return redirect('pages:manage_banners')
    
    is_checked = 'checked' if banner.is_active else ''
    
    return render(request, 'admin/banners/form.html', {
        'banner': banner,
        'action': 'Edit',
        'is_checked': is_checked
    })


@admin_required
def delete_banner(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    banner.delete()
    messages.success(request, 'Banner deleted successfully!')
    return redirect('pages:manage_banners')


# ==================== DESTINATION MANAGEMENT ====================

@admin_required
def manage_destinations(request):
    destinations = Destination.objects.all().order_by('order')
    return render(request, 'admin/destinations/list.html', {'destinations': destinations})


@admin_required
def add_destination(request):
    if request.method == 'POST':
        destination = Destination(
            name=request.POST.get('name'),
            location=request.POST.get('location'),
            price=request.POST.get('price'),
            description=request.POST.get('description', ''),
            is_active=request.POST.get('is_active') == 'on',
            order=request.POST.get('order', 0)
        )
        
        if 'image' in request.FILES:
            destination.image = request.FILES['image']
        
        destination.save()
        messages.success(request, 'Destination added successfully!')
        return redirect('pages:manage_destinations')
    
    return render(request, 'admin/destinations/form.html', {
        'action': 'Add',
        'destination': None,
        'is_checked': 'checked'
    })


@admin_required
def edit_destination(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        destination.name = request.POST.get('name')
        destination.location = request.POST.get('location')
        destination.price = request.POST.get('price')
        destination.description = request.POST.get('description', '')
        destination.is_active = request.POST.get('is_active') == 'on'
        destination.order = request.POST.get('order', 0)
        
        if 'image' in request.FILES:
            destination.image = request.FILES['image']
        
        destination.save()
        messages.success(request, 'Destination updated successfully!')
        return redirect('pages:manage_destinations')
    
    is_checked = 'checked' if destination.is_active else ''
    
    return render(request, 'admin/destinations/form.html', {
        'destination': destination,
        'action': 'Edit',
        'is_checked': is_checked
    })


@admin_required
def delete_destination(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    destination.delete()
    messages.success(request, 'Destination deleted successfully!')
    return redirect('pages:manage_destinations')


# ==================== SERVICE MANAGEMENT ====================

@admin_required
def manage_services(request):
    """مدیریت خدمات"""
    services = Service.objects.all().order_by('order')
    return render(request, 'admin/services/list.html', {'services': services})


@admin_required
def add_service(request):
    """افزودن سرویس جدید"""
    if request.method == 'POST':
        try:
            service = Service(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                link=request.POST.get('link', ''),
                is_active=request.POST.get('is_active') == 'on',
                order=request.POST.get('order', 0)
            )
            if 'image' in request.FILES:
                service.image = request.FILES['image']
            service.save()
            messages.success(request, 'Service added successfully!')
            return redirect('pages:manage_services')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'admin/services/service_form.html', {
        'action': 'Add',
        'service': None,
    })


@admin_required
def edit_service(request, pk):
    """ویرایش سرویس"""
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        try:
            service.title = request.POST.get('title')
            service.description = request.POST.get('description')
            service.link = request.POST.get('link', '')
            service.is_active = request.POST.get('is_active') == 'on'
            service.order = request.POST.get('order', 0)
            if 'image' in request.FILES:
                service.image = request.FILES['image']
            service.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('pages:manage_services')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'admin/services/service_form.html', {
        'service': service,
        'action': 'Edit',
    })


@admin_required
def delete_service(request, pk):
    """حذف سرویس"""
    service = get_object_or_404(Service, pk=pk)
    service.delete()
    messages.success(request, 'Service deleted successfully!')
    return redirect('pages:manage_services')


# ==================== BOOKING MANAGEMENT ====================

@admin_required
def manage_bookings(request):
    """مدیریت رزروها - شامل پرواز و هتل"""
    from bookings.models import Booking
    import json
    
    bookings = Booking.objects.all().order_by('-created_at')
    
    # پردازش آیتم‌های هر رزرو برای نمایش بهتر
    for booking in bookings:
        try:
            items = json.loads(booking.items)
            item_types = []
            for item in items:
                if item.get('type') == 'flight':
                    item_types.append('✈️ Flight')
                elif item.get('type') == 'hotel':
                    item_types.append('🏨 Hotel')
            booking.item_types = ', '.join(item_types)
            booking.items_list = items
        except:
            booking.item_types = 'Unknown'
            booking.items_list = []
    
    context = {
        'bookings': bookings,
        'total_count': bookings.count(),
    }
    return render(request, 'admin/services/booking_list.html', context)

@admin_required
def add_booking(request):
    """افزودن رزرو جدید"""
    if request.method == 'POST':
        try:
            import random
            import string
            ref = 'TRV-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            
            booking = Booking.objects.create(
                booking_ref=ref,
                full_name=request.POST.get('full_name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone', ''),
                total=request.POST.get('total', 0),
                status=request.POST.get('status', 'pending'),
                payment_method=request.POST.get('payment_method', 'credit_card'),
                session_key=request.session.session_key or 'manual',
                items='[]',
                passengers='[]',
                subtotal=request.POST.get('total', 0),
                tax=0,
                discount=0,
            )
            messages.success(request, f'Booking {ref} created successfully!')
            return redirect('pages:manage_bookings')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'admin/services/booking_form.html', {
        'action': 'Add',
        'booking': None,
    })


@admin_required
def edit_booking(request, booking_id):
    """ویرایش رزرو"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        try:
            booking.full_name = request.POST.get('full_name', booking.full_name)
            booking.email = request.POST.get('email', booking.email)
            booking.phone = request.POST.get('phone', booking.phone)
            booking.status = request.POST.get('status', booking.status)
            booking.payment_method = request.POST.get('payment_method', booking.payment_method)
            booking.total = request.POST.get('total', booking.total)
            booking.save()
            messages.success(request, f'Booking {booking.booking_ref} updated successfully!')
            return redirect('pages:manage_bookings')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'admin/services/booking_form.html', {
        'booking': booking,
        'action': 'Edit',
    })


@admin_required
def delete_booking(request, booking_id):
    """حذف رزرو"""
    booking = get_object_or_404(Booking, id=booking_id)
    ref = booking.booking_ref
    booking.delete()
    messages.success(request, f'Booking {ref} deleted successfully!')
    return redirect('pages:manage_bookings')
# ==================== ABOUT SECTION MANAGEMENT ====================

@admin_required
def manage_about(request):
    about_sections = AboutSection.objects.all()
    return render(request, 'admin/about/list.html', {'about_sections': about_sections})


@admin_required
def add_about(request):
    if request.method == 'POST':
        about = AboutSection(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            button_text=request.POST.get('button_text', ''),
            button_link=request.POST.get('button_link', ''),
            is_active=request.POST.get('is_active') == 'on'
        )
        
        if 'image' in request.FILES:
            about.image = request.FILES['image']
        
        about.save()
        messages.success(request, 'About section added successfully!')
        return redirect('pages:manage_about')
    
    return render(request, 'admin/about/form.html', {
        'action': 'Add',
        'about': None,
        'is_checked': 'checked'
    })


@admin_required
def edit_about(request, pk):
    about = get_object_or_404(AboutSection, pk=pk)
    if request.method == 'POST':
        about.title = request.POST.get('title')
        about.description = request.POST.get('description')
        about.button_text = request.POST.get('button_text', '')
        about.button_link = request.POST.get('button_link', '')
        about.is_active = request.POST.get('is_active') == 'on'
        
        if 'image' in request.FILES:
            about.image = request.FILES['image']
        
        about.save()
        messages.success(request, 'About section updated successfully!')
        return redirect('pages:manage_about')
    
    is_checked = 'checked' if about.is_active else ''
    
    return render(request, 'admin/about/form.html', {
        'about': about,
        'action': 'Edit',
        'is_checked': is_checked
    })


@admin_required
def delete_about(request, pk):
    about = get_object_or_404(AboutSection, pk=pk)
    about.delete()
    messages.success(request, 'About section deleted successfully!')
    return redirect('pages:manage_about')


# ==================== BLOG MANAGEMENT ====================

@admin_required
def manage_blogs(request):
    blog_posts = BlogPost.objects.all().order_by('-publish_date')
    return render(request, 'admin/blogs/list.html', {'blog_posts': blog_posts})


@admin_required
def add_blog(request):
    """Add blog post admin page"""
    if request.method == 'POST':
        try:
            from blog.models import Category
            from django.utils.text import slugify
            
            category_name = request.POST.get('category', '').strip()
            category = None
            
            if category_name:
                # ایجاد slug از نام دسته‌بندی
                base_slug = slugify(category_name)
                slug = base_slug
                counter = 1
                
                # اطمینان از یکتایی slug
                while Category.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                # ایجاد یا دریافت دسته‌بندی با slug یکتا
                category, created = Category.objects.get_or_create(
                    slug=slug,
                    defaults={'name': category_name}
                )
                
                # اگر دسته‌بندی با این slug وجود داشت ولی نامش متفاوت بود، نام را به‌روز می‌کنیم
                if not created and category.name != category_name:
                    category.name = category_name
                    category.save()
            
            # ایجاد بلاگ پست
            blog = BlogPost(
                title=request.POST.get('title'),
                content=request.POST.get('content'),
                category=category,
                tags=request.POST.get('tags', ''),
                publish_date=request.POST.get('publish_date'),
                is_active=request.POST.get('is_active') == 'on'
            )
            
            # تنظیم excerpt از محتوا
            content = request.POST.get('content', '')
            blog.excerpt = content[:200] + '...' if len(content) > 200 else content
            
            if 'image' in request.FILES:
                blog.image = request.FILES['image']
            
            blog.save()
            messages.success(request, 'Blog post added successfully!')
            return redirect('pages:manage_blogs')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'admin/blogs/form.html', {
        'action': 'Add',
        'blog': None,
        'is_checked': 'checked'
    })


@admin_required
def edit_blog(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        category_name = request.POST.get('category', '').strip()
        category = None
        if category_name:
            slug = category_name.lower().replace(' ', '-')
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'slug': slug}
            )
        
        blog.title = request.POST.get('title')
        blog.content = request.POST.get('content')
        blog.category = category
        blog.tags = request.POST.get('tags', '')
        blog.publish_date = request.POST.get('publish_date')
        blog.is_active = request.POST.get('is_active') == 'on'
        
        if 'image' in request.FILES:
            blog.image = request.FILES['image']
        
        blog.save()
        messages.success(request, 'Blog post updated successfully!')
        return redirect('pages:manage_blogs')
    
    is_checked = 'checked' if blog.is_active else ''
    
    return render(request, 'admin/blogs/form.html', {
        'blog': blog,
        'action': 'Edit',
        'is_checked': is_checked
    })


@admin_required
def delete_blog(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)
    blog.delete()
    messages.success(request, 'Blog post deleted successfully!')
    return redirect('pages:manage_blogs')


# ==================== AUTHENTICATION VIEWS ====================

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                UserProfile.objects.create(user=user, user_type='user')
                login(request, user)
                messages.success(request, 'Registration successful!')
                return redirect('pages:index')
        else:
            messages.error(request, 'Passwords do not match')
    
    return render(request, 'registration/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if hasattr(user, 'userprofile') and user.userprofile.user_type == 'admin':
                return redirect('pages:admin_dashboard')
            return redirect('pages:index')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'registration/login.html')


def user_logout(request):
    logout(request)
    return redirect('pages:index')


# ==================== USER MANAGEMENT ====================

@admin_required
def admin_users(request):
    users = User.objects.all().select_related('userprofile').order_by('-date_joined')
    context = {
        'users': users,
        'total_count': users.count(),
        'active_count': User.objects.filter(is_active=True).count(),
        'admin_count': User.objects.filter(is_superuser=True).count(),
    }
    return render(request, 'admin/users/list.html', context)


@admin_required
def admin_user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = UserProfile.objects.filter(user=user).first()
    
    if request.method == 'POST':
        try:
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.is_active = request.POST.get('is_active') == 'on'
            
            new_password = request.POST.get('password')
            if new_password:
                user.password = make_password(new_password)
            
            user.save()
            
            if profile:
                profile.user_type = request.POST.get('user_type', 'user')
                profile.phone = request.POST.get('phone', '')
                profile.save()
            else:
                UserProfile.objects.create(
                    user=user,
                    user_type=request.POST.get('user_type', 'user'),
                    phone=request.POST.get('phone', ''),
                )
            
            messages.success(request, f'User "{user.username}" updated successfully!')
            return redirect('pages:admin_users')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    context = {
        'user': user,
        'profile': profile,
        'action': 'Edit',
    }
    return render(request, 'admin/users/form.html', context)


@admin_required
def admin_user_add(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            user_type = request.POST.get('user_type', 'user')
            is_active = request.POST.get('is_active') == 'on'
            
            if not password:
                messages.error(request, 'Password is required!')
                return redirect('pages:admin_user_add')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists!')
                return redirect('pages:admin_user_add')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists!')
                return redirect('pages:admin_user_add')
            
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                is_active=is_active,
            )
            
            UserProfile.objects.create(
                user=user,
                user_type=user_type,
                phone=request.POST.get('phone', ''),
            )
            
            messages.success(request, f'User "{username}" added successfully!')
            return redirect('pages:admin_users')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    context = {
        'action': 'Add',
        'user': None,
        'profile': None,
    }
    return render(request, 'admin/users/form.html', context)


@admin_required
def admin_user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if user.is_superuser:
        messages.error(request, 'Cannot delete superuser!')
        return redirect('pages:admin_users')
    
    username = user.username
    user.delete()
    messages.success(request, f'User "{username}" deleted successfully!')
    return redirect('pages:admin_users')


@admin_required
def admin_user_toggle_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if user.is_superuser:
        messages.error(request, 'Cannot change superuser status!')
        return redirect('pages:admin_users')
    
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User "{user.username}" {status}!')
    return redirect('pages:admin_users')


# ==================== SALES / SERVICES REPORT ====================

@admin_required
def admin_services(request):
    """Show all bookings in admin panel with sales statistics"""
    bookings = list(Booking.objects.all().order_by('-created_at'))
    
    total_count = len(bookings)
    total_revenue = sum([b.total for b in bookings]) if bookings else 0
    
    today = datetime.now().date()
    today_bookings = [b for b in bookings if b.created_at.date() == today]
    today_revenue = sum([b.total for b in today_bookings]) if today_bookings else 0
    today_count = len(today_bookings)
    
    confirmed_count = len([b for b in bookings if b.status == 'confirmed'])
    pending_count = len([b for b in bookings if b.status == 'pending'])
    cancelled_count = len([b for b in bookings if b.status == 'cancelled'])
    
    context = {
        'bookings': bookings,
        'total_count': total_count,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'today_count': today_count,
        'month_revenue': total_revenue,
        'month_count': total_count,
        'confirmed_count': confirmed_count,
        'pending_count': pending_count,
        'cancelled_count': cancelled_count,
    }
    
    return render(request, 'admin/services/sales_list.html', context)



@admin_required
def add_destination(request):
    """Add destination admin page"""
    if request.method == 'POST':
        try:
            destination = Destination(
                name=request.POST.get('name'),
                location=request.POST.get('location'),
                price=request.POST.get('price'),
                description=request.POST.get('description', ''),
                is_active=request.POST.get('is_active') == 'on',
                order=request.POST.get('order', 0)
            )
            
            if 'image' in request.FILES:
                destination.image = request.FILES['image']
            
            destination.save()
            messages.success(request, 'Destination added successfully!')
            return redirect('pages:manage_destinations')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'admin/destinations/form.html', {
        'action': 'Add',
        'destination': None,
        'is_checked': 'checked'
    })
# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile

def login_view(request):
    if request.user.is_authenticated:
        return redirect('pages:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # بررسی می‌کند که آیا کاربر با ایمیل وارد شده یا نام کاربری
        if '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                pass
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back {user.username}!')
            
            # بررسی نوع کاربر برای هدایت به صفحه مناسب
            if hasattr(user, 'userprofile') and user.userprofile.user_type == 'admin':
                return redirect('pages:admin_dashboard')
            return redirect('pages:index')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('pages:index')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('pages:index')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        birth_date = request.POST.get('birth_date')
        
        # اعتبارسنجی
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/signup.html')
        
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'accounts/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'accounts/signup.html')
        
        # ایجاد کاربر
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        
        # ایجاد پروفایل
        UserProfile.objects.create(
            user=user,
            user_type='customer',
            phone=phone,
            birth_date=birth_date if birth_date else None
        )
        
        # ورود خودکار بعد از ثبت‌نام
        login(request, user)
        messages.success(request, 'Account created successfully!')
        return redirect('pages:index')
    
    return render(request, 'accounts/signup.html')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    context = {
        'user': request.user,
        'profile': getattr(request.user, 'userprofile', None),
    }
    return render(request, 'accounts/profile.html', context)
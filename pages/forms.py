from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import (
    UserProfile, Banner, Destination, Service, 
    AboutSection, BlogPost
)

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=[('user', 'Regular User')],
        initial='user',
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class AdminRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    admin_code = forms.CharField(max_length=50)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'subtitle', 'description', 'background_image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ['name', 'location', 'price', 'image', 'description', 'is_active', 'order']

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'description', 'image', 'link', 'is_active', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class AboutSectionForm(forms.ModelForm):
    class Meta:
        model = AboutSection
        fields = ['title', 'description', 'button_text', 'button_link', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'image', 'category', 'tags', 'publish_date', 'is_active']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
            'publish_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
        
# pages/forms.py - اضافه کردن این فرم

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'common-input mb-20 form-control', 'placeholder': 'Enter your name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'common-input mb-20 form-control', 'placeholder': 'Enter email address'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'common-input mb-20 form-control', 'placeholder': 'Enter subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'common-textarea form-control', 'placeholder': 'Enter Message'}))
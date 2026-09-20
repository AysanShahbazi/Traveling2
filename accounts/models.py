# accounts/models.py

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('user', 'Regular User'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='user')
    phone = models.CharField(max_length=15, blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    address = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
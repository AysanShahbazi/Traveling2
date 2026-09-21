from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('staff', 'Staff'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='userprofile'
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPES,
        default='customer'
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    points = models.IntegerField(default=0)
    profile_pic = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

    @property
    def is_admin(self):
        return self.user_type == 'admin'

    @property
    def is_customer(self):
        return self.user_type == 'customer'

    @property
    def is_staff_member(self):
        return self.user_type == 'staff'
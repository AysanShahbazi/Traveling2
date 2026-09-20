# pages/management/commands/create_admin_profile.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pages.models import UserProfile

class Command(BaseCommand):
    help = 'Create admin profile for existing superuser'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        
        if admin_user:
            profile, created = UserProfile.objects.get_or_create(
                user=admin_user,
                defaults={'user_type': 'admin'}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Admin profile created for {admin_user.username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Admin profile already exists for {admin_user.username}')
                )
        else:
            self.stdout.write(
                self.style.ERROR('No superuser found! Create one with: python manage.py createsuperuser')
            )
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    def check_admin(user):
        if not user.is_authenticated:
            return False
        return hasattr(user, 'userprofile') and user.userprofile.user_type == 'admin'
    
    return user_passes_test(check_admin, login_url='login')(view_func)
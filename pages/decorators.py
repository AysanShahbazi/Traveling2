from django.contrib.auth.decorators import user_passes_test


def admin_required(view_func):
    def check_admin(user):
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if not hasattr(user, 'userprofile'):
            return False
        return user.userprofile.user_type == 'admin'

    return user_passes_test(check_admin, login_url='accounts:login')(view_func)
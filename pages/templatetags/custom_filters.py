# pages/templatetags/custom_filters.py

from django import template
from django.conf import settings

register = template.Library()

@register.filter
def get_image_url(obj, field_name):
    """
    دریافت آدرس تصویر با بررسی وجود فایل
    اگر تصویر وجود نداشت، تصویر پیش‌فرض برمی‌گرداند
    """
    if not obj:
        return f'{settings.STATIC_URL}img/hero-bg.jpg'
    
    # دریافت فیلد مورد نظر
    field = getattr(obj, field_name, None)
    
    # بررسی وجود فایل
    if field and hasattr(field, 'url') and field.name:
        try:
            return field.url
        except (ValueError, OSError):
            pass
    
    # تعریف تصاویر پیش‌فرض برای فیلدهای مختلف
    default_images = {
        'background_image': f'{settings.STATIC_URL}img/hero-bg.jpg',
        'image': f'{settings.STATIC_URL}img/about-img.jpg',
    }
    
    return default_images.get(field_name, f'{settings.STATIC_URL}img/default.jpg')
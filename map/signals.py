# signals.py أو داخل دالة حفظ الإشعار في views.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
def send_live_notification(notification_obj):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{notification_obj.user.id}", 
        {
            "type": "send_notification",
            "message": notification_obj.message,
            "id": notification_obj.id,
            
            "created_at": notification_obj.created_at.strftime("%H:%M")
        }
    )

@receiver(user_logged_in)
def apply_remember_me(sender, request, user, **kwargs):
    # نطبّق الخيار بس على تسجيل الدخول من الفورم (POST)
    if request is None or request.method != 'POST':
        return

    # نتجاهل صفحة الأدمن، وأي مسار مش اسمه login
    match = getattr(request, 'resolver_match', None)
    if match is None or match.url_name != 'login' or 'admin' in match.namespaces:
        return

    if request.POST.get('remember_me'):
        # يبقى مسجّل دخول أسبوعين
        request.session.set_expiry(60 * 60 * 24 * 14)
    else:
        # الجلسة بتنتهي أول ما يسكّر المتصفح
        request.session.set_expiry(0)
    # نطبّق الخيار بس على صفحة الدخول تبعنا (مش على صفحة الأدمن مثلاً)
    if request is None or request.method != 'POST':
        return

    match = getattr(request, 'resolver_match', None)
    if match is None or match.view_name != 'login':
        return

    if request.POST.get('remember_me'):
        # يبقى مسجّل دخول أسبوعين
        request.session.set_expiry(60 * 60 * 24 * 14)
    else:
        # الجلسة بتنتهي أول ما يسكّر المتصفح
        request.session.set_expiry(0)
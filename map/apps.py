
from django.apps import AppConfig

class MapConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'map'

    def ready(self):
        import map.signals
        
        
        

 
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

print(">>> signals loaded")  # مؤقت للتأكد، امسحه بعدين


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
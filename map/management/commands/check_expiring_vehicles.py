from django.core.management.base import BaseCommand
from datetime import date, timedelta
from django.db.models import Q
from channels.layers import get_channel_layer
from map.models import Vehicle, UserAssignment  # استبدل your_app باسم تطبيقك
from map.views import dispatch_notification

class Command(BaseCommand):
    help = 'فحص تلقائي يومي للمركبات التي اقترب تاريخ انتهاء تأمينها أو ترخيصها'

    def handle(self, *args, **options):
        today = date.today()
        warning_period = today + timedelta(days=14)
        channel_layer = get_channel_layer()

        # جلب جميع المدراء المعنيين
        managers = UserAssignment.objects.filter(
            is_active=True,
            unit__name__icontains="النقل والصيانة"
        ).filter(role__name__icontains="مدير")

        # جلب جميع المركبات المنتهية أو القريبة من الانتهاء عالمياً
        expiring_vehicles = Vehicle.objects.filter(
            Q(insurance_expiry__lte=warning_period) | 
            Q(license_expiry__lte=warning_period)
        )

        count = 0
        for vehicle in expiring_vehicles:
            status_parts = []
            if vehicle.insurance_expiry and vehicle.insurance_expiry <= warning_period:
                status_parts.append(f"تأمين ينتهي في {vehicle.insurance_expiry}")
            if vehicle.license_expiry and vehicle.license_expiry <= warning_period:
                status_parts.append(f"ترخيص ينتهي في {vehicle.license_expiry}")

            if status_parts:
                message_text = f"⚠️ تنبيه لمركبة {vehicle.vehicle_number}: " + " و ".join(status_parts)
                for manager in managers:
                    dispatch_notification(manager.user, message_text, channel_layer)
                count += 1

        self.stdout.write(self.style.SUCCESS(f'تم فحص المركبات بنجاح وإرسال تنبيهات لـ {count} مركبة.'))
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from map.models import Operation, CenterApproval, AttendanceNotification 

class Command(BaseCommand):
    help = 'فحص الاعتمادات اليومية وإرسال إشعار لمدير المحافظة إذا لم يتم الاعتماد بحلول 12 ظهراً'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        
        # 1. جلب المراكز التي تم اعتمادها اليوم
        approved_operation_ids = CenterApproval.objects.filter(
            approved_at__date=today,
            is_revoked=False
        ).values_list('operation_id', flat=True)

        # 2. استبعاد المراكز المعتمدة للحصول على المراكز غير المعتمدة
        unapproved_operations = Operation.objects.exclude(id__in=approved_operation_ids)

        if not unapproved_operations.exists():
            self.stdout.write(self.style.SUCCESS("جميع المراكز قامت بالاعتماد اليوم."))
            return

        # 3. جلب المدراء (مثلاً المستخدمين الإداريين)
        managers = User.objects.filter(is_staff=True)

        # 4. إرسال الإشعارات
        for op in unapproved_operations:
            title = f"تنبيه عدم اعتماد: {op.center}"
            message = f"لم يتم اعتماد دوام اليوم لمركز ({op.center}) حتى الساعة 12:00 ظهراً. يرجى المتابعة والاعتماد."
            
            for manager in managers:
                exists = AttendanceNotification.objects.filter(
                    recipient=manager,
                    title=title,
                    created_at__date=today
                ).exists()

                if not exists:
                    AttendanceNotification.objects.create(
                        recipient=manager,
                        title=title,
                        message=message,
                        notification_type='pending_approval'
                    )

        self.stdout.write(self.style.SUCCESS("تم إرسال إشعارات التنبيه لمدير المحافظة بنجاح."))
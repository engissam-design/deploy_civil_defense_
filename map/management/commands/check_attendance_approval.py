import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from map.models import Operation, AttendanceApproval
from map.services import notify_pending_approval
from map.models import (
    Operation,
    AttendanceApproval,
    AttendanceSystemNotification,
)
logger = logging.getLogger(__name__)

class Command(BaseCommand):

    help = (
        "يفحص جميع العمليات (المراكز) ويرسل إشعاراً "
        "لمدير المحافظة إذا لم يتم اعتماد الدوام حتى الآن."
    )

    def handle(self, *args, **options):

        today = timezone.now().date()

        self.stdout.write(
            f"🔍 فحص اعتمادات الدوام لتاريخ {today} ..."
        )

        operations = Operation.objects.select_related(
            "center__governorate"
        ).all()

        checked_count = 0
        pending_count = 0
        skipped_count = 0

        for operation in operations:

            checked_count += 1

            approved = (
                AttendanceApproval.objects
                .filter(
                    operation=operation,
                    date=today,
                    approval_type="directorate",
                    approved=True,
                    is_active=True
                )
                .exists()
            )

            if approved:
                continue

            # =====================================================
            # منع تكرار الإشعار لنفس المركز في نفس اليوم
            # =====================================================

            already_notified_text = (
                f"({operation.center.name}) "
                f"حتى الساعة 12 ظهراً لليوم"
            )

            already_notified = (
                AttendanceSystemNotification.objects
                .filter(
                    message__icontains=already_notified_text,
                    created_at__date=today
                )
                .exists()
            )

            if already_notified:

                skipped_count += 1

                self.stdout.write(
                    f"⏭️ تم تخطي مركز ({operation.center.name}) "
                    f"— تم إرسال التنبيه له مسبقاً اليوم."
                )

                continue

            pending_count += 1

            try:
                notify_pending_approval(operation=operation)

            except Exception as e:
                logger.exception(
                    "Pending Approval Notification Error. "
                    "Operation=%s Error=%s",
                    operation.id,
                    e
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ تم الفحص: {checked_count} عملية، "
                f"{pending_count} تم إرسال تنبيه لها، "
                f"{skipped_count} تم تخطيها (تنبيه سابق)."
            )
        )
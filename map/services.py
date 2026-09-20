import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    AttendanceSystemNotification,
    UserAssignment,
)


logger = logging.getLogger(__name__)
User = get_user_model()
def notify_governorate_directors(
    operation,
    editor_name
):
    """
    إرسال إشعار إلى مدراء المحافظة
    المختصين بمحافظة العملية.

    شروط المستلم:

    1. المستخدم فعال.
    2. التعيين الوظيفي فعال.
    3. الدور = مدير المحافظة.
    4. لديه صلاحية الاعتماد.
    5. المحافظة مطابقة لمحافظة العملية.
    """

    print("")
    print("=" * 80)
    print("🔔 START NOTIFY GOVERNORATE DIRECTORS")
    print("=" * 80)

    # =========================================================
    # 1. المحافظة التابعة للعملية
    # =========================================================

    governorate = (
        operation.center.governorate
    )

    print(
        f"🏛️ محافظة العملية: {governorate}"
    )

    # =========================================================
    # 2. جلب التعيينات
    # =========================================================

    assignments = (
        UserAssignment.objects
        .filter(
            unit__linked_governorate=governorate,
            is_active=True
        )
        .select_related(
            "user",
            "role",
            "unit",
            "unit__linked_governorate",
            "unit__linked_center",
        )
    )

    print(
        f"📋 عدد التعيينات: "
        f"{assignments.count()}"
    )

    # =========================================================
    # 3. تجميع المدراء بدون تكرار
    # =========================================================

    directors = {}

    # =========================================================
    # 4. فحص التعيينات
    # =========================================================

    for assignment in assignments:

        user = assignment.user
        role = assignment.role
        unit = assignment.unit

        print("")
        print("-" * 60)

        # =====================================================
        # المستخدم
        # =====================================================

        if not user:

            print(
                "❌ لا يوجد مستخدم"
            )

            continue

        print(
            f"👤 المستخدم: "
            f"{user.username}"
        )

        # =====================================================
        # الحساب فعال
        # =====================================================

        if not user.is_active:

            print(
                "❌ الحساب غير فعال"
            )

            continue

        print(
            "✅ الحساب فعال"
        )

        # =====================================================
        # Role
        # =====================================================

        if not role:

            print(
                "❌ لا يوجد Role"
            )

            continue

        print(
            f"🎭 الدور: {role.name}"
        )

        # =====================================================
        # مدير المحافظة
        # =====================================================

        if role.name != "مدير المحافظة":

            print(
                "❌ الدور ليس مدير المحافظة"
            )

            continue

        print(
            "✅ الدور = مدير المحافظة"
        )

        # =====================================================
        # Permission
        # =====================================================

        permission_name = (
            "map.can_approve_directorate_attendance"
        )

        try:

            has_permission = (
                user.has_perm(
                    permission_name
                )
            )

        except Exception as permission_error:

            logger.exception(
                "Permission check failed "
                "for user=%s",
                user.username
            )

            print(
                f"❌ خطأ Permission: "
                f"{permission_error}"
            )

            continue

        print(
            f"🔐 Permission: "
            f"{permission_name}"
        )

        print(
            f"   النتيجة: "
            f"{has_permission}"
        )

        if not has_permission:

            print(
                "❌ لا يمتلك صلاحية الاعتماد"
            )

            continue

        print(
            "✅ يمتلك صلاحية الاعتماد"
        )

        # =====================================================
        # Unit
        # =====================================================

        if not unit:

            print(
                "❌ لا توجد وحدة تنظيمية"
            )

            continue

        print(
            f"🏢 الوحدة: {unit}"
        )

        # =====================================================
        # محافظة التعيين
        # =====================================================

        assignment_governorate = (
            unit.linked_governorate
        )

        print(
            f"🏛️ محافظة التعيين: "
            f"{assignment_governorate}"
        )

        print(
            f"🏛️ محافظة العملية: "
            f"{governorate}"
        )

        # =====================================================
        # مطابقة المحافظة
        # =====================================================

        if assignment_governorate != governorate:

            print(
                "❌ المحافظة غير مطابقة"
            )

            continue

        print(
            "✅ المحافظة مطابقة"
        )

        # =====================================================
        # إضافة المدير
        # =====================================================

        directors[user.id] = user

        print(
            "🎯 تم اختيار المستخدم كمستلم"
        )

    # =========================================================
    # 5. النتيجة النهائية
    # =========================================================

    print("")
    print("=" * 80)
    print("📋 FINAL NOTIFICATION RECIPIENTS")
    print("=" * 80)

    if not directors:

        print(
            "❌ لا يوجد أي مدير محافظة "
            "مطابق للشروط."
        )

        print("=" * 80)

        return

    for director_id, director in directors.items():

        print(
            f"✅ {director.id} - "
            f"{director.username}"
        )

    print("=" * 80)

    # =========================================================
    # 6. تجهيز اسم المحرر
    # =========================================================

    safe_editor_name = (
        editor_name
        if editor_name
        and str(editor_name).strip()
        and str(editor_name).strip()
        != "None"
        else "غير محدد"
    )

    # =========================================================
    # 7. نص الإشعار
    # =========================================================

    message_text = (
        f"تم تعديل دوام الموظفين في مركز "
        f"({operation.center.name}) "
        f"بواسطة: {safe_editor_name}"
    )

    print(
        f"📝 Notification message: "
        f"{message_text}"
    )

    # =========================================================
    # 8. الحصول على Channel Layer
    # =========================================================

    try:

        print(
            "🔌 الحصول على Channel Layer..."
        )

        channel_layer = (
            get_channel_layer()
        )

        if channel_layer is None:

            print(
                "⚠️ Channel Layer = None"
            )

    except Exception as channel_error:

        logger.exception(
            "Could not get channel layer"
        )

        print(
            f"❌ Channel Layer Error: "
            f"{channel_error}"
        )

        channel_layer = None

    # =========================================================
    # 9. إرسال الإشعارات
    # =========================================================

    for director_id, director in directors.items():

        print("")
        print(
            f"📨 معالجة المدير: "
            f"{director.username}"
        )

        # =====================================================
        # إنشاء Notification في Database
        # =====================================================

        try:

            print(
                "💾 إنشاء Notification..."
            )

            notification = (
                AttendanceSystemNotification.objects.create(
                    user=director,
                    message=message_text
                )
            )

            print(
                f"✅ Notification created. "
                f"ID={notification.id}"
            )

        except Exception as notification_error:

            logger.exception(
                "Notification database creation "
                "failed for user=%s",
                director.username
            )

            print(
                f"❌ فشل إنشاء Notification: "
                f"{notification_error}"
            )

            continue

        # =====================================================
        # WebSocket
        # =====================================================

        if channel_layer is None:

            print(
                "⚠️ لا يوجد Channel Layer، "
                "سيتم تخطي WebSocket."
            )

            continue

        try:

            group_name = (
                f"user_{director.id}"
            )

            print(
                f"📡 WebSocket group: "
                f"{group_name}"
            )

            created_at = (
                timezone.localtime(
                    notification.created_at
                )
                .strftime(
                    "%Y-%m-%d, %H:%M"
                )
            )

            print(
                "📡 إرسال WebSocket..."
            )

            async_to_sync(
                channel_layer.group_send
            )(
                group_name,
                {
                    "type":
                        "send_notification",

                    "message":
                        notification.message,

                    "id":
                        notification.id,

                    "created_at":
                        created_at,
                }
            )

            print(
                "✅ WebSocket sent successfully"
            )

        except Exception as websocket_error:

            logger.exception(
                "WebSocket notification failed "
                "for user=%s",
                director.username
            )

            print(
                f"❌ WebSocket Error: "
                f"{websocket_error}"
            )

            # -------------------------------------------------
            # مهم جدًا:
            # لا نحذف Notification من Database
            # -------------------------------------------------

            print(
                "ℹ️ Notification بقي محفوظًا "
                "في Database رغم فشل WebSocket."
            )

    # =========================================================
    # 10. النهاية
    # =========================================================

    print("")
    print("=" * 80)
    print("✅ END NOTIFY GOVERNORATE DIRECTORS")
    print("=" * 80)


def notify_attendance_approval(operation, approved_by):
    """
    إرسال إشعار إلى المسؤولين عن دوام هذا المركز
    (من يملكون صلاحية can_manage_center_attendance
    على هذا المركز تحديداً) بأن اعتماد الدوام
    قد تم من قبل إدارة المديرية.
    """

    print("")
    print("=" * 80)
    print("🔔 START NOTIFY ATTENDANCE APPROVAL")
    print("=" * 80)

    governorate = operation.center.governorate

    # =========================================================
    # 1. جلب التعيينات المرتبطة بهذا المركز تحديداً
    # =========================================================

    assignments = (
        UserAssignment.objects
        .filter(
            unit__linked_center=operation.center,
            unit__linked_governorate=governorate,
            is_active=True
        )
        .select_related(
            "user",
            "unit",
            "unit__linked_center",
            "unit__linked_governorate",
        )
    )

    print(f"📋 عدد التعيينات: {assignments.count()}")

    recipients = {}

    for assignment in assignments:

        user = assignment.user

        if not user or not user.is_active:
            continue

        try:
            has_permission = user.has_perm(
                "map.can_manage_center_attendance"
            )
        except Exception:
            logger.exception(
                "Permission check failed for user=%s",
                user.username
            )
            continue

        if not has_permission:
            continue

        recipients[user.id] = user

    print(f"📋 عدد المستلمين: {len(recipients)}")

    if not recipients:
        print("❌ لا يوجد مستلمين مطابقين للشروط.")
        print("=" * 80)
        return

    # =========================================================
    # 2. نص الإشعار
    # =========================================================

    approver_name = (
        approved_by.get_full_name()
        or approved_by.username
    )

    message_text = (
        f"تم اعتماد دوام مركز "
        f"({operation.center.name}) "
        f"من قبل إدارة المديرية "
        f"بواسطة: {approver_name}"
    )

    print(f"📝 Notification message: {message_text}")

    # =========================================================
    # 3. Channel Layer
    # =========================================================

    try:
        channel_layer = get_channel_layer()
    except Exception:
        logger.exception("Could not get channel layer")
        channel_layer = None

    # =========================================================
    # 4. إرسال الإشعارات
    # =========================================================

    for user_id, user in recipients.items():

        try:
            notification = AttendanceSystemNotification.objects.create(
                user=user,
                message=message_text
            )
        except Exception:
            logger.exception(
                "Notification database creation failed for user=%s",
                user.username
            )
            continue

        if channel_layer is None:
            continue

        try:
            group_name = f"user_{user.id}"

            created_at = (
                timezone.localtime(notification.created_at)
                .strftime("%Y-%m-%d, %H:%M")
            )

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_notification",
                    "message": notification.message,
                    "id": notification.id,
                    "created_at": created_at,
                }
            )

        except Exception:
            logger.exception(
                "WebSocket notification failed for user=%s",
                user.username
            )

    print("=" * 80)
    print("✅ END NOTIFY ATTENDANCE APPROVAL")
    print("=" * 80)



def notify_pending_approval(operation):
    """
    إرسال إشعار إلى مدراء المحافظة المختصين
    بأن دوام هذا المركز لم يُعتمد بعد حتى الساعة 12.

    شروط المستلم: نفس شروط notify_governorate_directors
    (مدير محافظة + صلاحية الاعتماد + نفس المحافظة).
    """

    print("")
    print("=" * 80)
    print("🔔 START NOTIFY PENDING APPROVAL")
    print(f"Operation={operation.id}")
    print("=" * 80)

    governorate = operation.center.governorate

    # =========================================================
    # 1. جلب التعيينات
    # =========================================================

    assignments = (
        UserAssignment.objects
        .filter(
            unit__linked_governorate=governorate,
            is_active=True
        )
        .select_related(
            "user",
            "role",
            "unit",
            "unit__linked_governorate",
        )
    )

    directors = {}

    for assignment in assignments:

        user = assignment.user
        role = assignment.role
        unit = assignment.unit

        if not user or not user.is_active:
            continue

        if not role or role.name != "مدير المحافظة":
            continue

        try:
            has_permission = user.has_perm(
                "map.can_approve_directorate_attendance"
            )
        except Exception:
            logger.exception(
                "Permission check failed for user=%s",
                user.username
            )
            continue

        if not has_permission:
            continue

        if not unit or unit.linked_governorate != governorate:
            continue

        directors[user.id] = user

    print(f"📋 عدد المستلمين: {len(directors)}")

    if not directors:
        print("❌ لا يوجد أي مدير محافظة مطابق للشروط.")
        print("=" * 80)
        return

    # =========================================================
    # 2. نص الإشعار
    # =========================================================

    message_text = (
        f"تنبيه: لم يتم اعتماد دوام مركز "
        f"({operation.center.name}) "
        f"حتى الساعة 12 ظهراً لليوم."
    )

    print(f"📝 Notification message: {message_text}")

    # =========================================================
    # 3. Channel Layer
    # =========================================================

    try:
        channel_layer = get_channel_layer()
    except Exception:
        logger.exception("Could not get channel layer")
        channel_layer = None

    # =========================================================
    # 4. إرسال الإشعارات
    # =========================================================

    for user_id, user in directors.items():

        try:
            notification = AttendanceSystemNotification.objects.create(
                user=user,
                message=message_text
            )
        except Exception:
            logger.exception(
                "Notification database creation failed for user=%s",
                user.username
            )
            continue

        if channel_layer is None:
            continue

        try:
            group_name = f"user_{user.id}"

            created_at = (
                timezone.localtime(notification.created_at)
                .strftime("%Y-%m-%d, %H:%M")
            )

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_notification",
                    "message": notification.message,
                    "id": notification.id,
                    "created_at": created_at,
                }
            )

        except Exception:
            logger.exception(
                "WebSocket notification failed for user=%s",
                user.username
            )

    print("=" * 80)
    print("✅ END NOTIFY PENDING APPROVAL")
    print("=" * 80)
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import AttendanceSystemNotification
import json


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        # ==========================================
        # التأكد من تسجيل الدخول
        # ==========================================
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f"user_{self.user.id}"

        # ==========================================
        # إضافة المستخدم إلى مجموعة الإشعارات
        # ==========================================
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        # ==========================================
        # جلب الإشعارات غير المقروءة
        # ==========================================
        notifications = await self.get_unread_notifications()

        # ==========================================
        # إرسال الإشعارات الموجودة مسبقاً
        # ==========================================
        for notification in notifications:

            await self.send(
                text_data=json.dumps({
                    "type": "new_notification",
                    "message": notification["message"],
                    "id": notification["id"],
                    "created_at": notification["created_at"],
                    "unread_count": len(notifications)
                })
            )

        # ==========================================
        # إرسال العدد النهائي
        # ==========================================
        await self.send(
            text_data=json.dumps({
                "type": "unread_count_update",
                "unread_count": len(notifications)
            })
        )

    async def disconnect(self, close_code):

        if hasattr(self, "group_name"):

            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    # ==========================================
    # استقبال أوامر JavaScript
    # ==========================================
    async def receive(self, text_data):

        try:
            data = json.loads(text_data)

        except (json.JSONDecodeError, TypeError):
            return

        action = data.get("action")

        # ==========================================
        # تعليم إشعار واحد كمقروء
        # ==========================================

        if action == "mark_as_read":

            notification_id = data.get(
                "notification_id"
            )

            if notification_id:

                await self.mark_notification_as_read(
                    notification_id
                )

                unread_count = await self.get_unread_count()

                await self.send(
                    text_data=json.dumps({
                        "type": "unread_count_update",
                        "unread_count": unread_count
                    })
                )

        # ==========================================
        # تعليم جميع الإشعارات كمقروءة
        # ==========================================

        elif action == "mark_all_as_read":

            await self.mark_all_as_read()

            await self.send(
                text_data=json.dumps({
                    "type": "unread_count_update",
                    "unread_count": 0
                })
            )

    # ==========================================
    # استقبال إشعار جديد من group_send
    # ==========================================
    async def send_notification(self, event):

        unread_count = await self.get_unread_count()

        await self.send(
            text_data=json.dumps({
                "type": "new_notification",
                "message": event["message"],
                "id": event.get("id"),
                "created_at": event.get("created_at"),
                "unread_count": unread_count
            })
        )

    # ==========================================
    # جلب الإشعارات غير المقروءة
    # ==========================================
    @database_sync_to_async
    def get_unread_notifications(self):

        notifications = (
            AttendanceSystemNotification.objects
            .filter(
                user=self.user,
                is_read=False
            )
            .order_by("-created_at")
        )

        return [
            {
                "id": notification.id,
                "message": notification.message,

                # ======================================
                # تحويل UTC إلى توقيت فلسطين
                # ======================================
                "created_at": timezone.localtime(
                    notification.created_at
                ).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }

            for notification in notifications
        ]

    # ==========================================
    # جلب عدد الإشعارات غير المقروءة
    # ==========================================
    @database_sync_to_async
    def get_unread_count(self):

        return (
            AttendanceSystemNotification.objects
            .filter(
                user=self.user,
                is_read=False
            )
            .count()
        )

    # ==========================================
    # تعليم إشعار واحد كمقروء
    # ==========================================
    @database_sync_to_async
    def mark_notification_as_read(
        self,
        notification_id
    ):

        (
            AttendanceSystemNotification.objects
            .filter(
                id=notification_id,
                user=self.user,
                is_read=False
            )
            .update(
                is_read=True
            )
        )

    # ==========================================
    # تعليم جميع الإشعارات كمقروءة
    # ==========================================
    @database_sync_to_async
    def mark_all_as_read(self):

        (
            AttendanceSystemNotification.objects
            .filter(
                user=self.user,
                is_read=False
            )
            .update(
                is_read=True
            )
        )









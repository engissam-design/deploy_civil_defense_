# signals.py أو داخل دالة حفظ الإشعار في views.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

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


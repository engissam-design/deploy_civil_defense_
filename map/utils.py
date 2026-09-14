# map/utils.py

# تأكد من استيراد النماذج التي تحتاجها الدالة
from .models import VehiclesEquipment, StoreEquipment, CenterEquipment 
# قد تحتاج لاستيراد Operation أيضاً إذا كانت الدالة تستخدمها

def process_new_equipment(operation_instance, post_data, EquipmentModel, text_field_name):
    """
    تقوم هذه الدالة بمعالجة إدخال نصي متعدد الأسطر/الفاصلات
    لإضافة معدات جديدة وربطها بكائن العملية (Operation).
    """
    new_equipment_text = post_data.get(text_field_name)
    if not new_equipment_text:
        return

    # تقسيم النص إلى أسماء معدات
    # (يمكنك تعديل منطق الفصل هنا بناءً على كيف تتوقع الإدخال)
    names = [name.strip() for name in new_equipment_text.replace('\r\n', ',').split(',') if name.strip()]

    for name in names:
        # البحث عن المعدة أو إنشائها
        item, created = EquipmentModel.objects.get_or_create(name=name)
        
        # ربطها بكائن العملية
        # نفترض هنا أن EquipmentModel لها علاقة ManyToMany مع Operation
        if EquipmentModel.__name__ == 'VehiclesEquipment':
            operation_instance.vehicle_equipment.add(item)
        elif EquipmentModel.__name__ == 'StoreEquipment':
            operation_instance.store_equipment.add(item)
        elif EquipmentModel.__name__ == 'CenterEquipment':
            operation_instance.center_equipment.add(item)
        # يمكنك استخدام setattr أو اسم حقل العلاقة المناسب إذا كانت أسماء الحقول مختلفة
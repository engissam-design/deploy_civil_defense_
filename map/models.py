from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import AbstractUser

class Search(models.Model):

    address = models.CharField(
        max_length=200,
        null=True,
        verbose_name="العنوان / البحث"
    )

    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ البحث"
    )

    class Meta:
        verbose_name = "بحث"
        verbose_name_plural = "عمليات البحث"

    def __str__(self):
        return self.address or "بحث بدون عنوان"

from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.db import models

class LocationLog(models.Model):
    latitude = models.FloatField(verbose_name="خط العرض")
    longitude = models.FloatField(verbose_name="خط الطول")
    color = models.CharField(max_length=10, default='blue', verbose_name="اللون")

    class Meta:
        verbose_name = "سجل موقع"
        verbose_name_plural = "سجلات المواقع"

    def __str__(self):
        return f"{self.latitude}, {self.longitude}"

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Permission

class Governorate(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم المحافظة")

    class Meta:
        verbose_name = "محافظة"
        verbose_name_plural = "1- المحافظات"

    def __str__(self):
        return self.name


class Center(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم المركز / المديرية")
    governorate = models.ForeignKey(
        Governorate, 
        on_delete=models.CASCADE, 
        related_name='centers', 
        verbose_name="المحافظة"
    )

    class Meta:
        verbose_name = "مركز/مديرية"
        verbose_name_plural = "المراكز والمديريات"

    def __str__(self):
        return f"{self.name} - {self.governorate.name}"


class Department(models.Model):
    name = models.CharField(max_length=50, verbose_name="اسم القسم")

    class Meta:
        verbose_name = "قسم"
        verbose_name_plural = "الأقسام"

    def __str__(self):
        return self.name


class OrganizationUnit(models.Model):
    UNIT_TYPES = [
        ('hq', 'الإدارة العامة'),
        ('sector', 'قاطع'),                     
        ('gov', 'محافظة'),
        ('directorate', 'مديرية محافظة'),       
        ('dept_branch', 'إدارة داخل مديرية'),  
        ('dept_center', 'إدارة داخل مركز'),  
        ('center', 'مركز لهدف معين'),          
        ('support_center', 'مركز إسناد'),        
    ]

    # خيارات المناطق الإقليمية
    REGION_CHOICES = [
        ('north', 'منطقة الشمال'),
        ('center', 'منطقة الوسط'),
        ('south', 'منطقة الجنوب'),
    ]

    name = models.CharField(max_length=200, verbose_name="اسم الوحدة")
    unit_type = models.CharField(max_length=30, choices=UNIT_TYPES, db_index=True, verbose_name="نوع الوحدة")
    
    # العمود الجديد لتحديد الإقليم (للشمال أو الجنوب أو الوسط)
    region = models.CharField(
        max_length=20, 
        choices=REGION_CHOICES, 
        null=True, 
        blank=True, 
        verbose_name="المنطقة الإقليمية (القاطع/الإسناد)"
    )
    
    linked_governorate = models.ForeignKey(Governorate, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="المحافظة المرتبطة")
    linked_center = models.ForeignKey(Center, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="المركز/المديرية المرتبطة")

    class Meta:
        verbose_name = "وحدة تنظيمية"
        verbose_name_plural = "الوحدات التنظيمية -3"
        indexes = [
            models.Index(fields=['unit_type']),
        ]

    def __str__(self):
        region_str = f" - {self.get_region_display()}" if self.region else ""
        return f"{self.name} ({self.get_unit_type_display()}){region_str}"
    

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم الدور/الرتبة")
    level = models.PositiveIntegerField(default=100, db_index=True, verbose_name="المستوى الوظيفي")
    parent = models.ForeignKey(
        'self', null=True, blank=True, 
        on_delete=models.SET_NULL, 
        related_name='sub_roles', 
        verbose_name="الدور الأعلى"
    )
    permissions = models.ManyToManyField(
        Permission, blank=True, 
        related_name='roles', 
        verbose_name="الصلاحيات الممنوحة"
    )

    class Meta:
        verbose_name = "دور"
        verbose_name_plural = "2- الأدوار"
        ordering = ['level']

        permissions = [
        (
            "can_approve_directorate_attendance",
            "Can approve directorate attendance"
        ),
    ]

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    RANK_CHOICES = [
        ("soldier", "الجندي"),
        ("corporal", "العريف"),
        ("sergeant", "الرقيب"),
        ("first_sergeant", "الرقيب أول"),
        ("warrant", "المساعد"),
        ("first_warrant", "المساعد أول"),
        ("lieutenant", "الملازم"),
        ("first_lieutenant", "الملازم أول"),
        ("captain", "النقيب"),
        ("major", "الرائد"),
        ("lt_colonel", "المقدم"),
        ("colonel", "العقيد"),
        ("brigadier", "العميد"),
        ("major_general", "اللواء"),
    ]
   
    username = models.CharField(max_length=150, unique=True, verbose_name="اسم المستخدم")
    unique_number = models.CharField(
        max_length=20, unique=True, null=True, blank=True,
        verbose_name="الرقم الوظيفي"
    )
    rank = models.CharField(
        max_length=20, choices=RANK_CHOICES, blank=True, default="",
        verbose_name="الرتبة"
    )

    # save() و Meta زي ما هم
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # إذا ما انحط رقم يدوي، بنولّد واحد تلقائي من الـ id
        if not self.unique_number:
            self.unique_number = str(100000 + self.pk)
            super().save(update_fields=['unique_number'])

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون -4"



class UserAssignment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assignments', db_index=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, db_index=True)
    unit = models.ForeignKey(OrganizationUnit, on_delete=models.PROTECT, null=True, blank=True, verbose_name="الوحدة التنظيمية الحالية")
    manager = models.ForeignKey(CustomUser, null=True, blank=True, related_name='subordinates', on_delete=models.SET_NULL, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "تعيين وظيفي"
        verbose_name_plural = "التعيينات الوظيفية -5"

    def __str__(self):
        unit_name = self.unit.name if self.unit else "بدون وحدة"
        return f"{self.user.username} - {self.role.name} - {unit_name}"

    @property
    def assigned_governorate(self):
        if not self.unit:
            return None
        
        # إذا كانت الوحدة مرتبطة بمحافظة بشكل مباشر
        if self.unit.linked_governorate:
            return self.unit.linked_governorate.name
            
        # إذا كانت الوحدة قاطع أو مركز إسناد ولها إقليم محدد
        if self.unit.unit_type in ['sector', 'support_center'] and self.unit.region:
            return f"إقليمي ({self.unit.get_region_display()})"
            
        return "كافة المحافظات (نطاق مركزي/عام)"

    @property
    def assigned_directorate_or_center(self):
        if not self.unit:
            return None
        if self.unit.unit_type == 'directorate':
            return f"مقر المديرية: {self.unit.name}"
        if self.unit.unit_type == 'dept_branch':
            return f"إدارة فرعية داخل: {self.unit.name}"
        if self.unit.unit_type in ['center', 'support_center']:
            region_info = f" ({self.unit.get_region_display()})" if self.unit.region else ""
            return f"مركز: {self.unit.name}{region_info}"
        return f"وحدة: {self.unit.name}"

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Permission


class Incident(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان الحادث")
    description = models.TextField(verbose_name="وصف الحادث")
    
    department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        verbose_name="القسم"
    )
    
    governorate = models.ForeignKey(
        'Governorate',
        on_delete=models.CASCADE,
        verbose_name="المحافظة"
    )
    
    center = models.ForeignKey(
        'Center',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المركز"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "حادث"
        verbose_name_plural = "الحوادث"

    def __str__(self):
        return self.title

from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group




from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="المستخدم"
    )

    message = models.TextField(verbose_name="الرسالة")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    read = models.BooleanField(default=False, verbose_name="تمت القراءة")

    class Meta:
        verbose_name = "إشعار"
        verbose_name_plural = "الإشعارات"

    def __str__(self):
        return f"{self.user.username} - {self.message[:20]}"


from django.db import models
from django.conf import settings


from django.db import models
from django.conf import settings

class VehicleApproval(models.Model):
    vehicle = models.OneToOneField(
        'Vehicle', 
        on_delete=models.CASCADE, 
        related_name='approval', 
        verbose_name="المركبة"
    )
    
    # اعتماد مدير النقل والصيانة
    approved_by_transport_manager = models.BooleanField(
        default=False, 
        verbose_name="اعتماد مدير النقل والصيانة"
    )
    transport_manager_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, blank=True, 
        on_delete=models.SET_NULL, 
        related_name='transport_approvals',
        verbose_name="مدير النقل والصيانة المعتَمِد"
    )
    transport_approval_date = models.DateTimeField(
        null=True, blank=True, 
        verbose_name="تاريخ اعتماد النقل والصيانة"
    )

    # اعتماد مدير المحافظة
    approved_by_governorate_manager = models.BooleanField(
        default=False, 
        verbose_name="اعتماد مدير المحافظة"
    )
    governorate_manager_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, blank=True, 
        on_delete=models.SET_NULL, 
        related_name='governorate_approvals',
        verbose_name="مدير المحافظة المعتَمِد"
    )
    governorate_approval_date = models.DateTimeField(
        null=True, blank=True, 
        verbose_name="تاريخ اعتماد مدير المحافظة"
    )

    def __str__(self):
        return f"اعتماد المركبة: {self.vehicle.vehicle_number}"

    class Meta:
        verbose_name = "اعتماد مركبة"
        verbose_name_plural = "اعتمادات المركبات"


        
class BuildingInfo(models.Model):
    EVALUATION_CHOICES = [
        ('A', 'تقييم A'),
        ('B', 'تقييم B'),
        ('C', 'تقييم C'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buildings',
        verbose_name="المستخدم"
    )

    governorate = models.ForeignKey(
        'Governorate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المحافظة"
    )

    center = models.ForeignKey(
        'Center',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المركز"
    )

    disaster_governorate = models.CharField(
        max_length=100,
        default="غير محددة",
        verbose_name="محافظة الكارثة"
    )

    owner_name = models.CharField(max_length=100, verbose_name="اسم المالك")
    building_name = models.CharField(max_length=100, verbose_name="اسم المبنى")
    phone_number = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    floors = models.IntegerField(verbose_name="عدد الطوابق")
    has_parking = models.BooleanField(verbose_name="يوجد موقف سيارات")
    
    latitude = models.FloatField(default=0.0, verbose_name="خط العرض")
    longitude = models.FloatField(default=0.0, verbose_name="خط الطول")

    address = models.TextField(default="بدون عنوان", verbose_name="العنوان")

    evaluated = models.BooleanField(default=False, verbose_name="تم التقييم")
    
    evaluation = models.CharField(
        max_length=1,
        choices=EVALUATION_CHOICES,
        null=True,
        blank=True,
        verbose_name="التقييم"
    )

    status = models.CharField(max_length=100, default="لم يتم التقييم", verbose_name="الحالة")

    class Meta:
        verbose_name = "مبنى"
        verbose_name_plural = "المباني"

    def __str__(self):
        return f"{self.building_name} - {self.owner_name}"

class BuildingMedia(models.Model):
    building = models.ForeignKey(
        BuildingInfo,
        on_delete=models.CASCADE,
        related_name='media',
        verbose_name="المبنى"
    )
    
    image = models.ImageField(
        upload_to='disaster_images/',
        null=True,
        blank=True,
        verbose_name="صورة"
    )
    
    video = models.FileField(
        upload_to='disaster_videos/',
        null=True,
        blank=True,
        verbose_name="فيديو"
    )

    class Meta:
        verbose_name = "وسائط مبنى"
        verbose_name_plural = "وسائط المباني"

    def __str__(self):
        return f"ملف تابع لـ {self.building.building_name}"



INSURED_STATUS_CHOICES = [
    ('insured', 'مؤمن'),
    ('uninsured', 'غير مؤمن'),
]

from django.db import models
from django.conf import settings

class Investigation(models.Model):

    INSURED_STATUS_CHOICES = [
        ('insured', 'مؤمن'),
        ('uninsured', 'غير مؤمن'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="المستخدم"
    )

    governorate = models.ForeignKey(
        'Governorate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المحافظة"
    )

    center = models.ForeignKey(
        'Center',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المركز"
    )

    location = models.CharField(max_length=255, blank=True, null=True, verbose_name="الموقع")

    event_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الحادث")
    event_time = models.TimeField(blank=True, null=True, verbose_name="وقت الحادث")

    inspection_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الكشف")
    inspection_time = models.TimeField(blank=True, null=True, verbose_name="وقت الكشف")

    end_inspection_date = models.DateField(blank=True, null=True, verbose_name="تاريخ انتهاء الكشف")
    end_inspection_time = models.TimeField(blank=True, null=True, verbose_name="وقت انتهاء الكشف")

    owner_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="اسم المالك")
    occupation_type = models.CharField(max_length=100, blank=True, null=True, verbose_name="نوع المهنة")

    insured_status = models.CharField(
        max_length=100,
        choices=INSURED_STATUS_CHOICES,
        blank=True,
        null=True,
        verbose_name="حالة التأمين"
    )

    general_description = models.TextField(blank=True, null=True, verbose_name="وصف عام")
    technical_observations = models.TextField(blank=True, null=True, verbose_name="ملاحظات فنية")
    fire_start_area = models.TextField(blank=True, null=True, verbose_name="منطقة بداية الحريق")
    damages = models.TextField(blank=True, null=True, verbose_name="الأضرار")
    cause_of_incident = models.TextField(blank=True, null=True, verbose_name="سبب الحادث")
    technical_analysis = models.TextField(blank=True, null=True, verbose_name="التحليل الفني")

    committee_signature = models.CharField(max_length=100, blank=True, null=True, verbose_name="توقيع اللجنة")

    latitude = models.FloatField(blank=True, null=True, verbose_name="خط العرض")
    longitude = models.FloatField(blank=True, null=True, verbose_name="خط الطول")

    current_address = models.TextField(blank=True, null=True, verbose_name="العنوان الحالي")

    signature_image = models.ImageField(
        upload_to='investigations/signatures/',
        blank=True,
        null=True,
        verbose_name="صورة التوقيع"
    )

    class Meta:
        verbose_name = "تحقيق"
        verbose_name_plural = "التحقيقات"

    def __str__(self):
        return f"تحقيق {self.id} - {self.center or 'بدون مركز'}"

class InvestigationMedia(models.Model):
    investigation = models.ForeignKey(
        Investigation,
        on_delete=models.CASCADE,
        related_name='media',
        verbose_name="التحقيق"
    )

    image = models.ImageField(
        upload_to='investigations/images/',
        null=True,
        blank=True,
        verbose_name="صورة"
    )

    video = models.FileField(
        upload_to='investigations/videos/',
        null=True,
        blank=True,
        verbose_name="فيديو"
    )

    class Meta:
        verbose_name = "وسائط تحقيق"
        verbose_name_plural = "وسائط التحقيقات"

    def __str__(self):
        return f"ملف تابع للتحقيق رقم {self.investigation.id}"
# models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

# --- الجداول المرجعية للمعدات (Many-to-Many) ---

class VehiclesEquipment(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم المعدات")
    def __str__(self): return self.name
    class Meta: 
        verbose_name = "معدات المركبة"
        verbose_name_plural = "معدات المركبات"

class StoreEquipment(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم معدة المخزن")
    def __str__(self): return self.name
    class Meta: 
        verbose_name = "معدات المخزن"
        verbose_name_plural = "معدات المخازن"

class CenterEquipment(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم معدة المركز")
    def __str__(self): return self.name
    class Meta: 
        verbose_name = "معدات المركز"
        verbose_name_plural = "معدات المراكز"

class Operation(models.Model):
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, verbose_name="المحافظة")
    center = models.ForeignKey(Center, on_delete=models.CASCADE, verbose_name="المركز")

    # ➕ حقل صورة الترويسة الجديد
    header_image = models.ImageField(upload_to='operation_headers/', blank=True, null=True, verbose_name="صورة الترويسة")

    latitude = models.FloatField(verbose_name="خط العرض")
    longitude = models.FloatField(verbose_name="خط الطول")
    objective = models.TextField(blank=True, null=True, verbose_name="الهدف")
    services = models.TextField(blank=True, null=True, verbose_name="الخدمات")
    landline = models.CharField(max_length=20, blank=True, null=True, verbose_name="الهاتف الأرضي")
    emergency_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم الطوارئ")
    mobile = models.CharField(max_length=20, blank=True, null=True, verbose_name="الهاتف الخلوي")

    vehicle_equipment = models.ManyToManyField(VehiclesEquipment, blank=True, verbose_name="معدات المركبة")
    store_equipment = models.ManyToManyField(StoreEquipment, blank=True, verbose_name="معدات المخزن")
    center_equipment = models.ManyToManyField(CenterEquipment, blank=True, verbose_name="معدات المركز")

    def __str__(self):
        return f"{self.governorate.name} - {self.center.name}"

    class Meta:
        verbose_name = "مركز العمليات"
        verbose_name_plural = "مراكز العمليات"
class OperationImage(models.Model):
    # ✅ هذا هو related_name الصحيح الذي سنستخدمه: 'center_images'
    operation = models.ForeignKey(Operation, related_name='center_images', on_delete=models.CASCADE) 
    image = models.ImageField(upload_to='operation_images/', verbose_name="صورة")
    caption = models.CharField(max_length=255, blank=True, verbose_name="وصف الصورة")
    def __str__(self): return f"صورة لـ {self.operation.center}"
    class Meta: verbose_name = "صورة المركز"

class OperationVehicleEquipmentFile(models.Model):
    operation = models.ForeignKey(Operation, related_name='vehicle_files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='equipment_files/vehicle/', verbose_name="ملف معدات مركبة")
    caption = models.CharField(max_length=255, blank=True, verbose_name="وصف الملف")
    class Meta: verbose_name = "ملف معدات مركبة مرفق"

class OperationStoreEquipmentFile(models.Model):
    operation = models.ForeignKey(Operation, related_name='store_files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='equipment_files/store/', verbose_name="ملف معدات مخزن")
    caption = models.CharField(max_length=255, blank=True, verbose_name="وصف الملف")
    class Meta: verbose_name = "ملف معدات مخزن مرفق"

class OperationCenterEquipmentFile(models.Model):
    operation = models.ForeignKey(Operation, related_name='center_files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='equipment_files/center/', verbose_name="ملف معدات مركز")
    caption = models.CharField(max_length=255, blank=True, verbose_name="وصف الملف")
    class Meta: verbose_name = "ملف معدات مركز مرفق"


# models.py
from django.db import models

DAYS_OF_WEEK = [
    ("sat", "السبت"),
    ("sun", "الأحد"),
    ("mon", "الاثنين"),
    ("tue", "الثلاثاء"),
    ("wed", "الأربعاء"),
    ("thu", "الخميس"),
    ("fri", "الجمعة"),
]


class Employee(models.Model):

    operation = models.ForeignKey(
        'Operation',
        on_delete=models.CASCADE,
        related_name="employees",
        verbose_name="المركز"
    )

    name = models.CharField(max_length=200, verbose_name="اسم الموظف")

    mobile = models.CharField(max_length=20, verbose_name="رقم الجوال",
        blank=True,
        null=True)

    address = models.CharField(max_length=200, verbose_name="مكان السكن",
        blank=True,
        null=True)

    rank = models.CharField(
        max_length=100,
        verbose_name="رتبة الموظف",
        blank=True,
        null=True
    )

    rank_date = models.DateField(
        verbose_name="تاريخ الرتبة",
        blank=True,
        null=True
    )

    education_level = models.CharField(
        max_length=200,
        verbose_name="المستوى العلمي",
        blank=True,
        null=True
    )

    job_description = models.TextField(
        verbose_name="الوصف الوظيفي",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "موظف"
        verbose_name_plural = "الموظفين"

    def __str__(self):
        return self.name
from django.db import models
from django.db import models

class EmergencyTicker(models.Model):
    """موديل التنبيه العاجل للشريط المتحرك"""
    title = models.CharField(max_length=100, default="تنبيه عاجل", verbose_name="عنوان التنبيه")
    content = models.TextField(verbose_name="محتوى التنبيه")
    emergency_number = models.CharField(max_length=20, default="102", verbose_name="رقم الطوارئ")
    is_active = models.BooleanField(default=True, verbose_name="تفعيل التنبيه")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    class Meta:
        verbose_name = "تنبيه عاجل"
        verbose_name_plural = "التنبيهات العاجلة"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Announcement(models.Model):
    """موديل الإعلانات والأخبار"""
    CATEGORY_CHOICES = [
        ('weather', 'حالة الطقس'),
        ('volunteer', 'التطوع'),
        ('safety', 'السلامة العامة'),
        ('general', 'عام'),
    ]

    title = models.CharField(max_length=255, verbose_name="عنوان الخبر/الإعلان")
    content = models.TextField(verbose_name="المحتوى")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general', verbose_name="التصنيف")
    is_urgent = models.BooleanField(default=False, verbose_name="إعلان هام/عاجل")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ النشر")

    class Meta:
        verbose_name = "إعلان / خبر"
        verbose_name_plural = "الإعلانات والأخبار"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

from django.contrib.auth.models import User

class EmployeeAttendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'مداوم'),
        ('early_leave', 'مغادرة'),
        ('vacation', 'إجازة'),
        ('mission', 'مهمة رسمية'),
    ]
    REASON_CHOICES = [
        ('', 'اختر السبب...'),
        ('sick', 'مرض'),
        ('travel', 'سفر'),
        ('other', 'غير ذلك'),
    ]

    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    leave_reason = models.CharField(max_length=20, choices=REASON_CHOICES, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    # أضف هذا الحقل داخل موديل EmployeeAttendance
    updated_by = models.ForeignKey(
     CustomUser, 
     on_delete=models.SET_NULL, 
     null=True, 
     blank=True, 
     verbose_name="تعديل بواسطة"
    ) 
    duty_officer_name = models.CharField(
    max_length=150, 
    blank=True, 
    null=True, 
    verbose_name="اسم الضابط المناوب"
)

    class Meta:
        unique_together = ('employee', 'date')
        permissions = [
            ("can_manage_center_attendance", "يمكنه إدخال وتعديل دوام المركز (مدير مركز / ضابط مناوب)"),
            ("can_approve_directorate_attendance", "يمكنه اعتماد دوام المديرية (مدير مديرية / نائب مدير مديرية)"),
        ]

    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.get_status_display()}"

from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.conf import settings  # <--- 1. إضافة هذا الاستيراد

class AttendanceApproval(models.Model):
    operation = models.ForeignKey('Operation', on_delete=models.CASCADE)
    date = models.DateField()

    APPROVAL_TYPES = (
        ("director", "مدير المديرية"),
        ("department", "مدير الإدارة"),
    )

    approval_type = models.CharField(max_length=20, choices=APPROVAL_TYPES)
    approved = models.BooleanField(default=False)
    
    # <--- 2. تعديل الربط هنا ليصبح مع settings.AUTH_USER_MODEL
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    
    approved_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="اعتماد نشط")
    revoked_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الإلغاء")

    class Meta:
        ordering = ['-approved_at']
        permissions = [
            ("can_approve_as_director", "يمكنه الاعتماد بصلاحية مدير مديرية"),
            ("can_approve_as_department", "يمكنه الاعتماد بصلاحية مدير إدارة"),
        ]

    def __str__(self):
        status = "نشط" if self.is_active else "ملغى"
        return f"{self.get_approval_type_display()} - {self.operation} - {self.date} ({status})"

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AttendanceSystemNotification(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="attendance_notifications",
        verbose_name="المستخدم"
    )
    message = models.TextField(verbose_name="نص الإشعار")
    is_read = models.BooleanField(default=False, verbose_name="تمت القراءة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإشعار")

    class Meta:
        verbose_name = "إشعار حضور وانصراف"
        verbose_name_plural = "إشعارات الحضور والانصراف"
        ordering = ['-created_at']

    def __str__(self):
        return f"إشعار لـ {self.user.username}: {self.message[:30]}"


from django.db import models
from django.utils import timezone

class Certificate(models.Model):
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name="الموظف"
    )

    name = models.CharField(
        max_length=200,
        verbose_name="اسم الشهادة / الدورة"
    )

    date = models.DateField(
        verbose_name="تاريخ الحصول عليها",
        blank=True,
        null=True
    )

    file = models.FileField(
        upload_to='certificates/',
        verbose_name="ملف الشهادة",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "شهادة"
        verbose_name_plural = "الشهادات والدورات"

    def __str__(self):
        return f"{self.name} - {self.employee}"

from django.utils import timezone
import datetime

class WorkSchedule(models.Model):

    DAYS_OF_WEEK = [
        ("mon", "الاثنين"),
        ("tue", "الثلاثاء"),
        ("wed", "الأربعاء"),
        ("thu", "الخميس"),
        ("fri", "الجمعة"),
        ("sat", "السبت"),
        ("sun", "الأحد"),
    ]

    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name="schedules",
        verbose_name="الموظف"
    )

    day = models.CharField(
        max_length=10,
        choices=DAYS_OF_WEEK,
        verbose_name="اليوم"
    )

    start = models.TimeField(
        null=True,
        blank=True,
        verbose_name="وقت البداية"
    )

    end = models.TimeField(
        null=True,
        blank=True,
        verbose_name="وقت النهاية"
    )

    is_night_shift = models.BooleanField(
        default=False,
        verbose_name="شيفت ليلي"
    )

    is_off = models.BooleanField(
        default=False,
        verbose_name="يوم عطلة"
    )

    class Meta:
        verbose_name = "جدول دوام"
        verbose_name_plural = "جداول الدوام"
        unique_together = ("employee", "day")

    def __str__(self):
        return f"{self.employee} - {self.get_day_display()}"

from django.conf import settings
from django.db import models

class PublicSafety(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    governorate = models.ForeignKey(
        'Governorate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المحافظة"
    )

    center = models.ForeignKey(
        'Center',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المركز"
    )

    owner_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="اسم المالك")
    national_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم الهوية")
    whatsapp = models.CharField(max_length=20, blank=True, null=True, verbose_name="واتساب")

    business_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="اسم المنشأة")
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name="المدينة")

    map_address = models.TextField(blank=True, null=True, verbose_name="عنوان الخريطة")
    manual_address = models.TextField(blank=True, null=True, verbose_name="عنوان يدوي")

    is_ready = models.BooleanField(default=False, verbose_name="جاهز")

    area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="المساحة")

    receipt_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الإيصال")

    required_actions = models.TextField(blank=True, null=True, verbose_name="الإجراءات المطلوبة")
    actions_done = models.TextField(blank=True, null=True, verbose_name="الإجراءات المنفذة")

    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="المبلغ")

    start_date = models.DateField(blank=True, null=True, verbose_name="تاريخ البداية")
    end_date = models.DateField(blank=True, null=True, verbose_name="تاريخ النهاية")

    latitude = models.FloatField(blank=True, null=True, verbose_name="خط العرض")
    longitude = models.FloatField(blank=True, null=True, verbose_name="خط الطول")

    class Meta:
        verbose_name = "السلامة العامة"
        verbose_name_plural = "السلامة العامة"

    def __str__(self):
        return f"{self.owner_name or 'بدون اسم'}"
class PublicSafetyMedia(models.Model):

    public_safety = models.ForeignKey(
        PublicSafety,
        on_delete=models.CASCADE,
        related_name='media',
        verbose_name="السلامة العامة"
    )

    image = models.ImageField(upload_to='public_safety/images/', blank=True, null=True, verbose_name="صورة")
    video = models.FileField(upload_to='public_safety/videos/', blank=True, null=True, verbose_name="فيديو")

    class Meta:
        verbose_name = "ملف سلامة عامة"
        verbose_name_plural = "ملفات السلامة العامة"

    def __str__(self):
        return f"ملف #{self.public_safety.id}"
class ReceiptImage(models.Model):

    public_safety = models.ForeignKey(
        PublicSafety,
        on_delete=models.CASCADE,
        related_name='receipt_images',
        verbose_name="السلامة العامة"
    )

    image = models.ImageField(upload_to='public_safety/receipts/', verbose_name="صورة الإيصال")

    class Meta:
        verbose_name = "إيصال"
        verbose_name_plural = "الإيصالات"

    def __str__(self):
        return f"إيصال - {self.public_safety.owner_name}"
class RequiredDocumentsImage(models.Model):

    public_safety = models.ForeignKey(
        PublicSafety,
        on_delete=models.CASCADE,
        related_name='required_docs_images',
        verbose_name="السلامة العامة"
    )

    image = models.ImageField(upload_to='public_safety/documents/', verbose_name="الوثيقة")

    class Meta:
        verbose_name = "وثيقة مطلوبة"
        verbose_name_plural = "الوثائق المطلوبة"

    def __str__(self):
        return f"وثيقة - {self.public_safety.owner_name}"

from django.db import models

from django.db import models
from django.utils import timezone


class Driver(models.Model):

    name = models.CharField("اسم السائق", max_length=100)

    national_id = models.CharField(
        "رقم الهوية",
        max_length=20,
        unique=True
    )

    residence = models.CharField("مكان السكن", max_length=200)

    city_or_village = models.CharField("المدينة / القرية", max_length=100)

    license_info = models.CharField("معلومات رخصة القيادة", max_length=200)

    work_location = models.CharField("موقع العمل", max_length=200)

    id_card_image = models.ImageField(
        "صورة الهوية",
        upload_to="drivers/id_cards/",
        blank=True,
        null=True
    )

    personal_image = models.ImageField(
        "صورة شخصية",
        upload_to="drivers/photos/",
        blank=True,
        null=True
    )

    license_image = models.ImageField(
        "صورة الرخصة",
        upload_to="drivers/licenses/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    class Meta:
        verbose_name = "سائق"
        verbose_name_plural = "السائقين"

    def __str__(self):
        return self.name



VEHICLE_TYPE_CHOICES = [
    ("fire", "إطفاء"),
    ("rescue", "إنقاذ"),
    ("fire_and_rescue", "إطفاء وإنقاذ"),
    ("services", "خدمات"),
    ("tank", "تنك تزويد"),
]

FUEL_TYPE_CHOICES = [
    ("diesel", "ديزل"),
    ("petrol", "بنزين"),
]

VEHICLE_STATUS_CHOICES = [
    ("in_service", "داخل الخدمة"),
    ("out_service", "خارج الخدمة"),
]
class Vehicle(models.Model):

    vehicle_number = models.CharField(
        max_length=50,
        unique=False, # تغييرها إلى False,
        verbose_name="رقم المركبة"
    )

    work_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPE_CHOICES,
        verbose_name="نوع المهمة"
    )

    governorate = models.ForeignKey(
        'Governorate',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="المحافظة"
    )

    center = models.ForeignKey(
        'Center',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="المركز"
    )

    vehicle_type = models.CharField(max_length=100, verbose_name="نوع المركبة")
    model = models.CharField(max_length=100, verbose_name="الطراز")
    category = models.CharField(max_length=100, verbose_name="الصنف")

    fuel_type = models.CharField(
        max_length=20,
        choices=FUEL_TYPE_CHOICES,
        verbose_name="نوع الوقود"
    )

    engine_power = models.CharField(max_length=50, verbose_name="قدرة المحرك")
    chassis_number = models.CharField(max_length=100, verbose_name="رقم الشصي")

    status = models.CharField(
        max_length=20,
        choices=VEHICLE_STATUS_CHOICES,
        default="in_service",
        verbose_name="الحالة"
    )

    status_notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات الحالة")

    # في models.py
    production_year = models.PositiveIntegerField(
    verbose_name="سنة الإنتاج",
    null=True,   # للسماح بالقيمة الفارغة في قاعدة البيانات
    blank=True   # للسماح بالقيمة الفارغة في الـ Admin والـ Forms
    )
    insurance_expiry = models.DateField(blank=True, null=True, verbose_name="نهاية التأمين")
    license_expiry = models.DateField(blank=True, null=True, verbose_name="نهاية الترخيص")
    insurance_company = models.CharField(max_length=100, blank=True, null=True, verbose_name="شركة التأمين")

    insurance_image = models.ImageField(upload_to="vehicles/insurance/", blank=True, null=True, verbose_name="صورة التأمين")
    license_image = models.ImageField(upload_to="vehicles/license/", blank=True, null=True, verbose_name="صورة الترخيص")

    work_nature = models.CharField(max_length=200, blank=True, null=True, verbose_name="طبيعة العمل")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    drivers = models.ManyToManyField("Driver", blank=True, related_name="vehicles", verbose_name="السائقين")

    class Meta:
     verbose_name = "مركبة"
     verbose_name_plural = "المركبات"
     permissions = [
        ("change_vehicle_status", "Can change vehicle status"),
     ]

    def __str__(self):
        return f"{self.vehicle_number} - {self.vehicle_type}"



from django.db import models
from django.utils import timezone

class VehicleStatusHistory(models.Model):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="المركبة"
    )

    status = models.CharField(
        max_length=20,
        choices=VEHICLE_STATUS_CHOICES,
        verbose_name="الحالة"
    )

    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    changed_at = models.DateTimeField(default=timezone.now, verbose_name="وقت التغيير")

    class Meta:
        verbose_name = "تاريخ حالة المركبة"
        verbose_name_plural = "تاريخ حالات المركبات"

    def __str__(self):
        return f"{self.vehicle.vehicle_number} - {self.get_status_display()}"
from django.utils import timezone
from django.db import models
from django.conf import settings

class VehicleStatusNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_notifications", verbose_name="المستخدم المستلم")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="sent_notifications", verbose_name="قام بالتغيير")
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE, verbose_name="المركبة")
    message = models.TextField(verbose_name="نص الإشعار")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الإنشاء")
    read = models.BooleanField(default=False, verbose_name="هل تمت القراءة")

    class Meta:
        verbose_name = "إشعار حالة مركبة"
        verbose_name_plural = "إشعارات حالات المركبات"
        ordering = ['-created_at']

    def __str__(self):
        return f"إشعار لـ {self.user.username} بخصوص {self.vehicle.vehicle_number}"

from django.db import models
from django.utils import timezone

class Trip(models.Model):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="trips",
        verbose_name="المركبة"
    )

    destination = models.CharField(max_length=200, verbose_name="الوجهة")

    start_odometer = models.PositiveIntegerField(verbose_name="عداد البداية")
    start_odometer_image = models.ImageField(upload_to="odometer/start/", blank=True, null=True)

    end_odometer = models.PositiveIntegerField(verbose_name="عداد النهاية")
    end_odometer_image = models.ImageField(upload_to="odometer/end/", blank=True, null=True)

    date = models.DateField(default=timezone.now, verbose_name="تاريخ الرحلة")

    class Meta:
        verbose_name = "رحلة"
        verbose_name_plural = "الرحلات"

    def __str__(self):
        return f"{self.vehicle} → {self.destination}"

    @property
    def distance(self):
        return self.end_odometer - self.start_odometer
class VehicleImage(models.Model):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="المركبة"
    )

    image = models.ImageField(upload_to="vehicles/", verbose_name="الصورة")

    class Meta:
        verbose_name = "صورة مركبة"
        verbose_name_plural = "صور المركبات"

    def __str__(self):
        return f"صورة {self.vehicle.vehicle_number}"
from django.db import models
from django.utils import timezone
# تأكد من استيراد Vehicle, Driver إن لم يكونا في نفس الملف

from decimal import Decimal # لضمان دقة العمليات

from django.db import models
from django.utils import timezone
from decimal import Decimal


class FuelQuota(models.Model):

    vehicle = models.ForeignKey(
        'Vehicle',
        on_delete=models.CASCADE,
        related_name="fuel_quotas",
        verbose_name="المركبة"
    )

    month = models.DateField(
        default=timezone.now,
        verbose_name="الشهر"
    )

    allocated_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="المبلغ المخصص (شيكل)"
    )

    allocated_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="الكمية المخصصة (لتر)"
    )

    class Meta:
        verbose_name = "مخصص وقود"
        verbose_name_plural = "مخصصات الوقود"

    def __str__(self):
        return f"{self.vehicle} - {self.month.strftime('%m-%Y')}"

    @property
    def used_quantity(self):
        return sum(f.quantity for f in self.fillings.all())

    @property
    def used_amount(self):
        return sum(f.amount for f in self.fillings.all())

    @property
    def remaining_quantity(self):
        return self.allocated_quantity - self.used_quantity

    @property
    def remaining_amount(self):
        return self.allocated_amount - self.used_amount

    @property
    def extra_used_quantity(self):
        remaining = self.remaining_quantity
        return abs(remaining) if remaining < Decimal('0.00') else Decimal('0.00')

    @property
    def extra_used_amount(self):
        remaining = self.remaining_amount
        return abs(remaining) if remaining < Decimal('0.00') else Decimal('0.00')
class FuelFilling(models.Model):

    quota = models.ForeignKey(
        FuelQuota,
        on_delete=models.CASCADE,
        related_name="fillings",
        verbose_name="المخصص الشهري"
    )

    driver = models.ForeignKey(
        'Driver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="السائق"
    )

    date = models.DateField(
        default=timezone.now,
        verbose_name="تاريخ التعبئة"
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="الكمية (لتر)"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="المبلغ (شيكل)"
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="ملاحظات"
    )

    receipt_image = models.ImageField(
        upload_to='fuel_receipts/',
        blank=True,
        null=True,
        verbose_name="صورة الوصل"
    )

    class Meta:
        verbose_name = "تعبئة وقود"
        verbose_name_plural = "تعبئات الوقود"

    def __str__(self):
        return f"{self.quantity} لتر - {self.date}"
from django.utils import timezone
from django.db import models
from django.utils import timezone
import uuid
from django.db import models
from django.utils import timezone
class Maintenance(models.Model):

    maintenance_number = models.CharField(
        max_length=6,
        unique=True,
        editable=False,
        verbose_name="رقم الصيانة"
    )

    vehicle = models.ForeignKey(
        'Vehicle',
        on_delete=models.CASCADE,
        related_name="maintenances",
        verbose_name="المركبة"
    )

    garage = models.CharField(max_length=200, verbose_name="اسم الكراج")

    date = models.DateField(default=timezone.now, verbose_name="تاريخ الصيانة")
    end_date = models.DateTimeField(blank=True, null=True, verbose_name="تاريخ الانتهاء")

    invoice_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الفاتورة")
    invoice_image = models.ImageField(upload_to="invoices/", blank=True, null=True, verbose_name="صورة الفاتورة")

    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="التكلفة الإجمالية"
    )

    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "صيانة"
        verbose_name_plural = "الصيانة"

    def save(self, *args, **kwargs):
        if not self.maintenance_number:
            last = Maintenance.objects.order_by('-id').first()
            next_number = (int(last.maintenance_number) if last and last.maintenance_number else 0) + 1
            self.maintenance_number = str(next_number).zfill(4)

        super().save(*args, **kwargs)

    @property
    def calculated_total_cost(self):
        return sum(item.cost for item in self.items.all())

    def __str__(self):
        return f"{self.vehicle} - {self.maintenance_number}"
class MaintenanceItem(models.Model):

    maintenance = models.ForeignKey(
        Maintenance,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="الصيانة"
    )

    description = models.CharField(max_length=200, verbose_name="الوصف")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="التكلفة")

    date = models.DateField(default=timezone.now, verbose_name="تاريخ العطل")

    image = models.ImageField(
        upload_to="maintenance/items/",
        blank=True,
        null=True,
        verbose_name="صورة العطل"
    )

    class Meta:
        verbose_name = "عنصر صيانة"
        verbose_name_plural = "عناصر الصيانة"

    def __str__(self):
        return f"{self.description} - {self.cost}"
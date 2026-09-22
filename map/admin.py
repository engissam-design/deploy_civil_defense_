from django.contrib import admin
from .models import Search
from .models import LocationLog,BuildingInfo,Investigation
from .models import Driver
from django.contrib import admin
from .models import LocationLog

@admin.register(LocationLog)
class LocationLogAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude', 'color')
    search_fields = ('color',)
    list_filter = ('color',)# Register your models here.


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):

    list_display = ("address", "date")

    search_fields = ("address",)

    list_filter = ("date",)


from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Governorate, Center

@admin.register(Governorate)
class GovernorateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    
from .models import Center
@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'governorate')
    search_fields = ('name',)
    list_filter = ('governorate',)
from django.contrib import admin
from .models import EmployeeAttendance
from django.contrib import admin
from .models import AttendanceApproval


from django.contrib import admin
from .models import AttendanceApproval
from django.contrib import admin
from .models import AttendanceSystemNotification
from django.contrib import admin
from .models import EmergencyTicker, Announcement
from django.contrib import admin
from .models import EmergencyTicker, Announcement


@admin.register(EmergencyTicker)
class EmergencyTickerAdmin(admin.ModelAdmin):
    # الأعمدة التي تظهر في جدول التنبيهات العاجلة
    list_display = ('title', 'emergency_number', 'is_active', 'created_at')
    
    # الأعمدة القابلة للتعديل المباشر من الجدول
    list_editable = ('is_active',)
    
    # شريط البحث
    search_fields = ('title', 'content')
    
    # الفلاتر الجانبية
    list_filter = ('is_active', 'created_at')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    # الأعمدة التي تظهر في جدول الأخبار والإعلانات
    list_display = ('title', 'category', 'is_urgent', 'created_at')
    
    # التعديل المباشر لحالة الإعلان الهام
    list_editable = ('is_urgent',)
    
    # شريط البحث في العنوان والمحتوى
    search_fields = ('title', 'content')
    
    # الفلاتر الجانبية حسب التصنيف، وهل هو عاجل، وتاريخ النشر
    list_filter = ('category', 'is_urgent', 'created_at')
@admin.register(AttendanceSystemNotification)
class AttendanceSystemNotificationAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'message',
        'is_read',
        'created_at',
    )

    list_filter = (
        'is_read',
        'created_at',
    )

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'message',
    )

    ordering = ('-created_at',)

@admin.register(AttendanceApproval)
class AttendanceApprovalAdmin(admin.ModelAdmin):
    list_display = (
        "operation",
        "date",
        "approval_type",
        "approved",
        "approved_by",
        "approved_at",
        "is_active",     # تمت الإضافة
        "revoked_at",    # تمت الإضافة
    )

    list_filter = (
        "approval_type",
        "approved",
        "is_active",     # تمت الإضافة للتصفية حسب حالة الاعتماد
        "date",
    )

    search_fields = (
        "operation__center__name",
        "approved_by__username",
    )

    readonly_fields = ("approved_at", "revoked_at") # اختياري: لجعل تواريخ النظام للعرض فقط عند تعديل السجل

@admin.register(EmployeeAttendance)
class EmployeeAttendanceAdmin(admin.ModelAdmin):
    # إضافة الحقول الجديدة لعرضها في قائمة الأدمن
    list_display = ('employee', 'date', 'status', 'leave_reason', 'notes')
    
    list_editable = ('status',) # لتعديل الحالة مباشرة من القائمة
    
    list_filter = ('date', 'status', 'employee__operation')
    search_fields = ('employee__name', 'leave_reason')
    date_hierarchy = 'date'


from .models import CustomUser,UserAssignment
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'unique_number', 'rank', 'email', 'get_governorate', 'get_center', 'is_staff', 'is_active')
    list_filter = ('rank', 'is_staff', 'is_active')
    search_fields = ('username', 'unique_number', 'email')

    fieldsets = UserAdmin.fieldsets + (
        ("البيانات الوظيفية", {"fields": ("unique_number", "rank")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("البيانات الوظيفية", {"fields": ("unique_number", "rank")}),
    )

    def get_governorate(self, obj):
        assignment = obj.assignments.filter(is_active=True).first()
        if assignment and assignment.unit and assignment.unit.linked_governorate:
            return assignment.unit.linked_governorate.name
        return "غير محدد"
    get_governorate.short_description = "المحافظة"

    def get_center(self, obj):
        assignment = obj.assignments.filter(is_active=True).first()
        if assignment and assignment.unit and assignment.unit.linked_center:
            return assignment.unit.linked_center.name
        return "غير محدد"
    get_center.short_description = "المركز/المديرية"
from django.contrib import admin
from .models import Role

from django.contrib import admin
from .models import Role, OrganizationUnit  # تأكد من استيراد الموديلات بشكل صحيح
from django.contrib import admin
from .models import Role, OrganizationUnit  # تأكد من استيراد الموديلات بشكل صحيح

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'level',
        'parent'
    )

    list_filter = (
        'level',
    )

    search_fields = (
        'name',
    )

    ordering = ('level',)

    # 👈 إضافة أداة اختيار الصلاحيات بشكل أفقي مريح وسهل البحث
    filter_horizontal = ('permissions',)

    fieldsets = (
        ('معلومات الدور', {
            'fields': ('name', 'level', 'parent')
        }),
        # 👈 إضافة قسم خاص بالصلاحيات الممنوحة ليعرض الحقل الجديد
        ('الصلاحيات والأمان', {
            'fields': ('permissions',),
            'description': 'اختر الصلاحيات المتاحة لهذا الدور الوظيفي في النظام.'
        }),
        
    )

from .models import OrganizationUnit
@admin.register(OrganizationUnit)
class OrganizationUnitAdmin(admin.ModelAdmin):
    # إضافة 'region' للعرض في الجدول الرئيسي للوحة التحكم
    list_display = ['name', 'unit_type', 'region', 'linked_governorate', 'linked_center'] 
    
    # إضافة 'region' للفلاتر الجانبية لتصفية القواطع ومراكز الإسناد حسب الإقليم
    list_filter = ['unit_type', 'region', 'linked_governorate'] 
    
    search_fields = ['name']

    # تحسين اختياري: إظهار حقل المنطقة فقط عندما تكون الوحدة قاطع أو مركز إسناد (عبر الـ Fieldsets)
    fieldsets = [
        (None, {
            'fields': ('name', 'unit_type')
        }),
        ('التوزيع الجغرافي والإقليمي', {
            'fields': ('region', 'linked_governorate', 'linked_center'),
            'description': 'اختر المنطقة الإقليمية في حال كان "قاطع" أو "مركز إسناد"، أو المحافظة/المركز للوحدات المحلية.'
        }),
    ]

@admin.register(UserAssignment)
class UserAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'role',
        'display_unit',
        'manager',
        'is_active',
        'created_at'
    )

    list_filter = (
        'role',
        'unit__unit_type',
        'unit__linked_governorate',
        'unit__linked_center',
        'is_active'
    )

    search_fields = (
        'user__username',
        'role__name',
        'unit__name',
        'unit__linked_governorate__name',
        'unit__linked_center__name',
    )

    @admin.display(
        description="الوحدة التنظيمية الحالية"
    )
    def display_unit(self, obj):

        if not obj.unit:
            return "-"

        unit = obj.unit

        result = unit.name

        # إضافة المحافظة
        if unit.linked_governorate:
            result += f" - {unit.linked_governorate.name}"

        # إضافة المركز
        if unit.linked_center:
            result += f" - {unit.linked_center.name}"

        return result

from django.contrib import admin
from .models import UserAssignment



from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    
from .models import Governorate

from .models import Notification  
from .models import Incident

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'governorate', 'center', 'created_at')
    list_filter = ('department', 'governorate', 'center')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)


from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'message',
        'created_at',
        'read'
    )

    list_filter = (
        'read',
        'created_at'
    )

    search_fields = (
        'user__username',
        'message'
    )

    ordering = ('-created_at',)

    list_editable = ('read',)

    
from django.contrib import admin
from .models import VehicleStatusNotification

@admin.register(VehicleStatusNotification)
class VehicleStatusNotificationAdmin(admin.ModelAdmin):
    # عرض الحقول في جدول الإدارة
    list_display = ('user', 'vehicle', 'created_at', 'read')
    
    # إضافة فلاتر جانبية للبحث السريع
    list_filter = ('read', 'created_at')
    
    # إمكانية البحث عن مستخدم أو مركبة
    search_fields = ('user__username', 'vehicle__vehicle_number', 'message')
    
    # جعل الحقول للقراءة فقط (اختياري)
    readonly_fields = ('created_at',)
from .models import Investigation, InvestigationMedia
from django.utils.html import format_html

class InvestigationMediaInline(admin.TabularInline):
    model = InvestigationMedia
    extra = 1
    readonly_fields = ('image_preview', 'video_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "معاينة الصورة"

    def video_preview(self, obj):
        if obj.video:
            return format_html(
                '<video width="200" controls><source src="{}" type="video/mp4"></video>',
                obj.video.url
            )
        return "-"
    video_preview.short_description = "معاينة الفيديو"


@admin.register(Investigation)
class InvestigationAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'center',
        'owner_name',
        'event_date',
        'insured_status'
    )

    list_filter = (
        'insured_status',
        'governorate',
        'center'
    )

    search_fields = (
        'owner_name',
        'location',
        'cause_of_incident'
    )

    inlines = [InvestigationMediaInline]


from django.contrib import admin
from .models import BuildingInfo, BuildingMedia

class BuildingMediaInline(admin.TabularInline):
    model = BuildingMedia
    extra = 1

@admin.register(BuildingInfo)
class BuildingInfoAdmin(admin.ModelAdmin):
    list_display = (
        'building_name',
        'owner_name',
        'governorate',
        'center',
        'evaluation',
        'status'
    )

    list_filter = (
        'evaluation',
        'governorate',
        'center',
        'has_parking'
    )

    search_fields = (
        'building_name',
        'owner_name',
        'phone_number'
    )

    inlines = [BuildingMediaInline]

from .models import PublicSafety, PublicSafetyMedia

class PublicSafetyMediaInline(admin.TabularInline):
    model = PublicSafetyMedia
    extra = 1
    fields = ("image", "video")


@admin.register(PublicSafety)
class PublicSafetyAdmin(admin.ModelAdmin):

    list_display = (
        'owner_name',
        'business_name',
        'city',
        'amount',
        'start_date',
        'end_date'
    )

    search_fields = (
        'owner_name',
        'business_name',
        'city',
        'national_id'
    )

    list_filter = (
        'city',
        'start_date',
        'end_date'
    )

    inlines = [PublicSafetyMediaInline]


from django.contrib import admin
from .models import Operation



from .models import VehiclesEquipment, StoreEquipment, CenterEquipment

# تسجيل نموذج معدات المركبات
@admin.register(VehiclesEquipment)
class VehiclesEquipmentAdmin(admin.ModelAdmin):
    list_display = ('name',) # لإظهار حقل "name" في قائمة الإدارة
    search_fields = ('name',) # لإضافة حقل بحث

# تسجيل نموذج معدات المخزن
@admin.register(StoreEquipment)
class StoreEquipmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# تسجيل نموذج معدات المركز
@admin.register(CenterEquipment)
class CenterEquipmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

from .models import Vehicle, VehicleImage


from django.contrib import admin
from .models import Vehicle, VehicleImage, VehicleApproval

# 1. إضافة الاعتماد كـ Inline داخل صفحة المركبة
class VehicleApprovalInline(admin.StackedInline):
    model = VehicleApproval
    can_delete = False
    verbose_name_plural = "حالة الاعتماد الرسمي"
    fk_name = "vehicle"
    extra = 0
    # الحقول التي يفضل أن تكون للعرض فقط لمنع التلاعب بالتواريخ والمسؤولين يدوياً
    readonly_fields = ("transport_approval_date", "governorate_approval_date")


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1
# 2. تعديل Admin المركبة لإضافة الـ Inline الخاص بالاعتماد
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle_number",
        "vehicle_type",
        "governorate",
        "center",
        "status",
        "production_year",
    )

    list_filter = (
        "status",
        "fuel_type",
        "work_type",
        "governorate",
    )

    search_fields = (
        "vehicle_number",
        "model",
        "insurance_company",
    )

    # إضافة VehicleApprovalInline إلى قائمة الـ inlines
    inlines = [VehicleApprovalInline, VehicleImageInline]

    # 3. تسجيل VehicleApproval كجدول مستقل في لوحة التحكم
@admin.register(VehicleApproval)
class VehicleApprovalAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle",
        "approved_by_transport_manager",
        "transport_manager_user",
        "transport_approval_date",
        "approved_by_governorate_manager",
        "governorate_manager_user",
        "governorate_approval_date",
    )

    list_filter = (
        "approved_by_transport_manager",
        "approved_by_governorate_manager",
    )

    search_fields = (
        "vehicle__vehicle_number",
        "transport_manager_user__username",
        "governorate_manager_user__username",
    )

    # حماية التواريخ من التعديل اليدوي المباشر
    readonly_fields = ("transport_approval_date", "governorate_approval_date")


@admin.register(VehicleImage)
class VehicleImageAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "image")
from .models import FuelQuota, FuelFilling

class FuelFillingInline(admin.TabularInline):
    model = FuelFilling
    extra = 1
    fields = ("date", "driver", "quantity", "amount", "notes")
    show_change_link = True

@admin.register(FuelQuota)
class FuelQuotaAdmin(admin.ModelAdmin):

    list_display = (
        "vehicle",
        "month",
        "allocated_quantity",
        "allocated_amount",
        "used_quantity",
        "used_amount",
        "remaining_quantity",
        "remaining_amount"
    )

    search_fields = ("vehicle__vehicle_number",)

    list_filter = (
        "month",
        "vehicle__governorate",
        "vehicle__center"
    )

    inlines = [FuelFillingInline]
@admin.register(FuelFilling)
class FuelFillingAdmin(admin.ModelAdmin):

    list_display = (
        "quota",
        "driver",
        "date",
        "quantity",
        "amount"
    )

    list_filter = (
        "date",
        "driver"
    )

    search_fields = (
        "quota__vehicle__vehicle_number",
        "driver__name"
    )
from .models import Driver
@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'national_id',
        'residence',
        'city_or_village',
        'work_location',
        'created_at'
    )

    search_fields = (
        'name',
        'national_id',
        'residence',
        'city_or_village',
        'work_location'
    )

    list_filter = (
        'city_or_village',
        'work_location'
    )

    ordering = ('-created_at',)


from django.contrib import admin
from .models import Operation, OperationImage

from .models import (
    Operation, OperationImage, 
    # ... باقي النماذج
)
# تأكد من استيراد جميع النماذج التي تحتاجها
from .models import (
    Operation, 
    OperationImage, 
    OperationVehicleEquipmentFile, 
    OperationStoreEquipmentFile, 
    OperationCenterEquipmentFile
)


class OperationImageInline(admin.TabularInline):
    model = OperationImage 
    extra = 1

class VehicleFileInline(admin.TabularInline):
    model = OperationVehicleEquipmentFile
    extra = 1
    verbose_name_plural = "ملفات معدات المركبة المرفقة" # لتظهر بوضوح في لوحة التحكم

class StoreFileInline(admin.TabularInline):
    model = OperationStoreEquipmentFile
    extra = 1
    verbose_name_plural = "ملفات معدات المخزن المرفقة"

class CenterFileInline(admin.TabularInline):
    model = OperationCenterEquipmentFile
    extra = 1
    verbose_name_plural = "ملفات معدات المركز المرفقة"



@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):

    inlines = [
        OperationImageInline,
        VehicleFileInline,
        StoreFileInline,
        CenterFileInline,
    ]

    # 1. إضافة header_image للعرض في قائمة الجداول (اختياري)
    list_display = ('center', 'governorate', 'header_image', 'latitude', 'longitude')
    search_fields = ('center__name', 'governorate__name')  # يفضل استخدام __name للبحث في الأسماء
    list_filter = ('governorate',)

    fieldsets = (
        (None, {
            'fields': (
                ('governorate', 'center'),
                'header_image',  # 2. إضافة حقل صورة الترويسة هنا
                ('latitude', 'longitude'),
            )
        }),
        ('التفاصيل والمعلومات', {
            'fields': (
                'objective',
                'services',
                'landline',
                'emergency_number',
                'mobile',
            )
        }),
        ('معدات المركز اليدوية (Many-to-Many)', {
            'fields': (
                'vehicle_equipment',
                'store_equipment',
                'center_equipment',
            )
        }),
    )
from django.contrib import admin
from .models import Employee


from django.contrib import admin
from django.utils import timezone
from .models import Employee, WorkSchedule

class WorkScheduleInline(admin.TabularInline):
    model = WorkSchedule
    extra = 0

    fields = (
        "day",
        "start",
        "end",
        "is_off",
        "is_night_shift"
    )

    ordering = ("day",)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "mobile",
        "operation",
        "is_off_today"
    )

    inlines = [WorkScheduleInline]

    def is_off_today(self, obj):
        today = timezone.now().date()

        weekday_map = {
            0: "mon",
            1: "tue",
            2: "wed",
            3: "thu",
            4: "fri",
            5: "sat",
            6: "sun",
        }

        weekday = weekday_map[today.weekday()]

        schedule = obj.schedules.filter(day=weekday).first()

        if schedule and schedule.is_off:
            return "✅ مجاز اليوم"

        return "❌ دوام"

    is_off_today.short_description = "حالة اليوم"

from django.contrib import admin
from .models import (
     Certificate,
    VehicleStatusHistory, Trip,
    Maintenance, MaintenanceItem,
    ReceiptImage, RequiredDocumentsImage
)




@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "name",
        "date"
    )

    search_fields = (
        "employee__name",
        "name"
    )

    list_filter = (
        "date",
    )

@admin.register(VehicleStatusHistory)
class VehicleStatusHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "vehicle",
        "status",
        "changed_at"
    )

    search_fields = (
        "vehicle__vehicle_number",
    )

    list_filter = (
        "status",
        "changed_at"
    )

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "destination", "date", "distance")
    search_fields = ("vehicle__vehicle_number", "destination")
    list_filter = ("date", "vehicle__governorate", "vehicle__center")


class MaintenanceItemInline(admin.TabularInline):
    model = MaintenanceItem
    extra = 1


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):

    list_display = (
        "vehicle",
        "garage",
        "date",
        "total_cost"
    )

    search_fields = (
        "vehicle__vehicle_number",
        "garage"
    )

    list_filter = (
        "date",
        "garage"
    )

    inlines = [MaintenanceItemInline]

@admin.register(ReceiptImage)
class ReceiptImageAdmin(admin.ModelAdmin):
    list_display = ("public_safety", "image")

@admin.register(RequiredDocumentsImage)
class RequiredDocumentsImageAdmin(admin.ModelAdmin):
    list_display = ("public_safety", "image")
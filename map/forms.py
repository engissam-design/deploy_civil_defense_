
from django import forms
from .models import Search
from .models import Investigation, Governorate, Center

from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label="البريد الإلكتروني",
        widget=forms.TextInput(attrs={
            "class": "input-field",
            "placeholder": "البريد الإلكتروني"
        })
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={
            "class": "input-field",
            "placeholder": "كلمة المرور"
        })
    )

class SearchForm(forms.ModelForm):
    address = forms.CharField(label='')

    class Meta:
        model = Search
        fields = ['address', ]


from django import forms
from .models import BuildingInfo
from django.core.exceptions import ValidationError

class BuildingForm(forms.ModelForm):
    class Meta:
        model = BuildingInfo
        fields = ['owner_name', 'building_name', 'phone_number', 'floors', 'has_parking', 'status', 'evaluation']
        labels = {
            'owner_name': 'اسم صاحب المبنى',
            'building_name': 'اسم المبنى',
            'phone_number': 'رقم الهاتف حسب مقدمة WhatsApp',
            'floors': 'عدد الطوابق',
            'has_parking': 'هل يوجد موقف سيارات؟',
            'status': 'حالة المبنى',
            'evaluation': 'تقييم المبنى',
        }
        widgets = {
            'owner_name': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
            'building_name': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
            'floors': forms.NumberInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
            'has_parking': forms.CheckboxInput(attrs={'class': 'form-check-input ml-2'}),
            'status': forms.TextInput(attrs={'class': 'form-control text-right', 'readonly': True, 'dir': 'rtl'}),
            'evaluation': forms.Select(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone.startswith('+970') and not phone.startswith('+972'):
            raise ValidationError("رقم الهاتف يجب أن يبدأ بـ +970 أو +972 فقط.")
        return phone
    
    
from django import forms
from .models import BuildingInfo

from django import forms
from .models import BuildingInfo
from django import forms
from django.core.exceptions import ValidationError
from .models import BuildingInfo

# forms.py

from django import forms
from django.core.exceptions import ValidationError
from .models import BuildingInfo, BuildingMedia

class BuildingInfoForm(forms.ModelForm):
    class Meta:
        model = BuildingInfo
        fields = [
            'owner_name', 'building_name', 'phone_number', 'floors',
            'has_parking', 'governorate', 'center'
        ]
        labels = {
            'owner_name': 'اسم صاحب المبنى',
            'building_name': 'اسم المبنى',
            'phone_number': 'رقم الهاتف حسب مقدمة WhatsApp',
            'floors': 'عدد الطوابق',
            'has_parking': 'هل يوجد موقف سيارات؟',
            'governorate': 'المحافظة',
            'center': 'المركز',
        }
        widgets = {
            'owner_name': forms.TextInput(attrs={
                'class': 'form-control text-right', 'dir': 'rtl'
            }),
            'building_name': forms.TextInput(attrs={
                'class': 'form-control text-right', 'dir': 'rtl'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control text-right', 'dir': 'rtl'
            }),
            'floors': forms.NumberInput(attrs={
                'class': 'form-control text-right', 'dir': 'rtl'
            }),
            'has_parking': forms.CheckboxInput(attrs={
                'class': 'form-check-input ml-2'
            }),
            'governorate': forms.Select(attrs={
                'class': 'form-select text-right', 'dir': 'rtl'
            }),
            'center': forms.Select(attrs={
                'class': 'form-select text-right', 'dir': 'rtl'
            }),
        }


    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone.startswith('+970') and not phone.startswith('+972'):
            raise ValidationError("رقم الهاتف يجب أن يبدأ بـ +970 أو +972 فقط.")
        return phone


class BuildingMediaForm(forms.ModelForm):
    class Meta:
        model = BuildingMedia
        fields = ['image', 'video']


# forms.py

from django import forms

from .models import Investigation
from .models import Investigation, Governorate, Center

# class InvestigationForm(forms.ModelForm):
#     committee_signature_text = forms.CharField(
#         required=False,
#         label='توقيع اللجنة (نص)',
#         widget=forms.TextInput(attrs={
#             'class': 'form-control text-right',
#             'dir': 'rtl',
#             'placeholder': 'اكتب توقيع اللجنة كنص'
#         })
#     )

#     governorate = forms.ModelChoiceField(
#         queryset=Governorate.objects.all(),
#         required=False,
#         label='المحافظة',
#         widget=forms.Select(attrs={'class': 'form-control text-right'})
#     )

#     center = forms.ModelChoiceField(
#         queryset=Center.objects.all(),
#         required=False,
#         label='المركز',
#         widget=forms.Select(attrs={'class': 'form-control text-right'})
#     )

#     class Meta:
#         model = Investigation
#         fields = [
#             'governorate', 'center', 'location', 'event_date', 'event_time',
#             'inspection_date', 'inspection_time', 'end_inspection_date', 'end_inspection_time',
#             'owner_name', 'occupation_type', 'insured_status',
#             'general_description', 'technical_observations', 'fire_start_area',
#             'damages', 'cause_of_incident', 'technical_analysis',
#             'signature_image', 'current_address',
#         ]
#         labels = {
#             'governorate': 'المحافظة',
#             'center': 'المركز',
#             'location': 'مكان وقوع الحادث بالتفصيل',
#             'event_date': 'تاريخ الحادث',
#             'event_time': 'وقت الحادث',
#             'inspection_date': 'تاريخ الكشف على موقع الحادث',
#             'inspection_time': 'وقت الكشف على موقع الحادث',
#             'end_inspection_date': 'تاريخ انتهاء الكشف على الموقع',
#             'end_inspection_time': 'وقت انتهاء الكشف على الموقع',
#             'owner_name': 'اسم المالك أو المستأجر',
#             'occupation_type': 'طبيعة الأشغال',
#             'insured_status': 'مكان الحادث (مؤمن / غير مؤمن)',
#             'general_description': 'الوصف العام للموقع',
#             'technical_observations': 'الملاحظات والمشاهدات الفنية',
#             'fire_start_area': 'منطقة بداية الحريق',
#             'damages': 'الأضرار',
#             'cause_of_incident': 'سبب الحريق',
#             'technical_analysis': 'التحليل الفني لعملية التحقيق',
#             'signature_image': 'صورة توقيع اللجنة',
#             'current_address': 'العنوان الحالي',
#         }
#         widgets = {
#             'location': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
#             'event_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control text-right'}),
#             'event_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control text-right'}),
#             'inspection_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control text-right'}),
#             'inspection_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control text-right'}),
#             'end_inspection_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control text-right'}),
#             'end_inspection_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control text-right'}),
#             'owner_name': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
#             'occupation_type': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
#             'insured_status': forms.Select(attrs={'class': 'form-control text-right'}),
#             'general_description': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 3, 'dir': 'rtl'}),
#             'technical_observations': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 3, 'dir': 'rtl'}),
#             'fire_start_area': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 2, 'dir': 'rtl'}),
#             'damages': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 2, 'dir': 'rtl'}),
#             'cause_of_incident': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 2, 'dir': 'rtl'}),
#             'technical_analysis': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 3, 'dir': 'rtl'}),
#             'current_address': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 2, 'dir': 'rtl', 'readonly': True}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # جعل جميع الحقول اختيارية
#         for field in self.fields.values():
#             field.required = False
from django import forms
from .models import Investigation

class InvestigationForm(forms.ModelForm):
    committee_signature_text = forms.CharField(
        required=False,
        label='توقيع اللجنة (نص)',
        widget=forms.TextInput(attrs={
            'class': 'form-control text-right',
            'dir': 'rtl',
            'placeholder': 'اكتب توقيع اللجنة كنص'
        })
    )

    class Meta:
        model = Investigation
        fields = [
            'location', 'event_date', 'event_time',
            'inspection_date', 'inspection_time', 'end_inspection_date', 'end_inspection_time',
            'owner_name', 'occupation_type', 'insured_status',
            'general_description', 'technical_observations', 'fire_start_area',
            'damages', 'cause_of_incident', 'technical_analysis',
            'signature_image', 'current_address',
        ]
        labels = {
            'location': 'مكان وقوع الحادث بالتفصيل',
            'event_date': 'تاريخ الحادث',
            'event_time': 'وقت الحادث',
            'inspection_date': 'تاريخ الكشف على موقع الحادث',
            'inspection_time': 'وقت الكشف على موقع الحادث',
            'end_inspection_date': 'تاريخ انتهاء الكشف على الموقع',
            'end_inspection_time': 'وقت انتهاء الكشف على الموقع',
            'owner_name': 'اسم المالك أو المستأجر',
            'occupation_type': 'طبيعة الأشغال',
            'insured_status': 'مكان الحادث (مؤمن / غير مؤمن)',
            'general_description': 'الوصف العام للموقع',
            'technical_observations': 'الملاحظات والمشاهدات الفنية',
            'fire_start_area': 'منطقة بداية الحريق',
            'damages': 'الأضرار',
            'cause_of_incident': 'سبب الحريق',
            'technical_analysis': 'التحليل الفني لعملية التحقيق',
            'signature_image': 'صورة توقيع اللجنة',
            'current_address': 'العنوان الحالي',
        }
        widgets = {
            'location': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
            'event_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control text-right'}),
            'event_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control text-right'}),
            'inspection_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control text-right'}),
            'inspection_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control text-right'}),
            'end_inspection_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control text-right'}),
            'end_inspection_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control text-right'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
            'occupation_type': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
            'insured_status': forms.Select(attrs={'class': 'form-control text-right'}),
            'general_description': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 3, 'dir': 'rtl'}),
            'technical_observations': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 3, 'dir': 'rtl'}),
            'fire_start_area': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 2, 'dir': 'rtl'}),
            'damages': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 2, 'dir': 'rtl'}),
            'cause_of_incident': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 2, 'dir': 'rtl'}),
            'technical_analysis': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 3, 'dir': 'rtl'}),
            'current_address': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 2, 'dir': 'rtl', 'readonly': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # جعل جميع الحقول اختيارية
        for field in self.fields.values():
            field.required = False

from django import forms
from .models import PublicSafety
from .models import Driver, Vehicle, VehicleImage

class PublicSafetyForm(forms.ModelForm):
    class Meta:
        model = PublicSafety
        fields = [
            'owner_name', 'national_id', 'whatsapp', 'business_name',
            'city', 'manual_address', 'area', 'receipt_number',
            'required_actions', 'actions_done', 'amount',
            'latitude', 'longitude'
        ]
        # ... بقية الإعدادات كما هي

        labels = {
            'owner_name': 'اسم صاحب المحل',
            'national_id': 'رقم الهوية',
            'whatsapp': 'رقم الواتساب',
            'business_name': 'اسم الحرفة',
            'city': 'المدينة',
            'manual_address': 'العنوان بالتفصيل (يكتبه المستخدم)',
            'area': 'المساحة (م²)',
            'receipt_number': 'رقم الوصل',
            'required_actions': 'الإجراءات المطلوبة',
            'actions_done': 'الإجراءات المنفذة',
            'amount': 'المبلغ (شيكل)',
            'start_date': 'تاريخ الكشف',
            'end_date': 'تاريخ الانتهاء',
        }
        widgets = {
            'owner_name': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
            'business_name': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
            'city': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
            'manual_address': forms.Textarea(attrs={
                'class': 'form-control text-right', 'rows': 2, 'dir': 'rtl', 'placeholder': 'اكتب تفاصيل العنوان مثل اسم الشارع أو معلم قريب...'
            }),
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
            'receipt_number': forms.TextInput(attrs={'class': 'form-control text-right', 'dir': 'rtl'}),
            'required_actions': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 2, 'dir': 'rtl'}),
            'actions_done': forms.Textarea(attrs={'class': 'form-control text-right', 'rows': 2, 'dir': 'rtl'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
from django import forms
from .models import Vehicle, Driver

from django import forms
from .models import Vehicle, Driver

from django import forms
from .models import Vehicle, Driver

# قائمة أنواع المهمة
TASK_TYPES = [
    ("fire", "إطفاء"),
    ("rescue", "إنقاذ"),
    ("services", "خدمات"),
    ("tank", "خزان")
]
from django import forms
from .models import Vehicle, Driver, FUEL_TYPE_CHOICES, VEHICLE_TYPE_CHOICES, VEHICLE_STATUS_CHOICES

TASK_TYPES = VEHICLE_TYPE_CHOICES
# forms.py
from django import forms
from .models import Vehicle, Driver, Governorate, Center
from django import forms
from .models import Vehicle, Driver, Governorate, Center
from django import forms
from .models import Vehicle

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        # نضع جميع الحقول التي تريدها في الفورم
        fields = [
            'governorate', 'center', 'vehicle_number', 'chassis_number', 'engine_power',
            'drivers', 'work_type', 'vehicle_type', 'model', 'production_year',
            'fuel_type', 'insurance_expiry', 'license_expiry',
            'insurance_company', 'insurance_image', 'license_image',
            'work_nature', 'notes', 'status', 'status_notes',
        ]
        widgets = {
            'insurance_expiry': forms.DateInput(attrs={'type': 'date'}),
            'license_expiry': forms.DateInput(attrs={'type': 'date'}),
            'status_notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super(VehicleForm, self).__init__(*args, **kwargs)
        
        # 1. نجعل كل الحقول اختيارية افتراضياً
        for field_name in self.fields:
            self.fields[field_name].required = False
            
        # 2. نعيد التأكيد أن رقم المركبة هو الوحيد المطلوب
        self.fields['vehicle_number'].required = True
# هذا النموذج فقط لرفع صورة واحدة
class VehicleImageForm(forms.ModelForm):
    class Meta:
        model = VehicleImage
        fields = ['image']



class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = [
            "name",
            "national_id",
            "residence",
            "city_or_village",
            "license_info",
            "work_location",
            "id_card_image",
            "personal_image",
            "license_image",  # ✅ الجديد
        ]

from django import forms
from .models import Vehicle

class VehicleDriversForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['drivers']  # هذا السطر يجعل الفورم يركز فقط على السائقين
from django import forms
from .models import FuelFilling

# FuelFillingForm
class FuelFillingForm(forms.ModelForm):
    class Meta:
        model = FuelFilling
        # 🌟 إضافة 'receipt_image' إلى قائمة الحقول
        fields = ["date", "driver", "quantity", "amount", "receipt_image", "notes"] 
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "driver": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            # 💡 لا نحتاج إلى تغيير نوع widget لـ ImageField، سيتولى Django ذلك
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
# from django import forms
# from .models import FuelQuota

# class FuelQuotaForm(forms.ModelForm):
#     class Meta:
#         model = FuelQuota
#         fields = ["vehicle", "month", "allocated_quantity", "allocated_amount"]
#         widgets = {
#             "month": forms.DateInput(attrs={"type": "month"}),
#         }


from django import forms
from .models import FuelQuota
import datetime
from django import forms
from .models import FuelQuota
from decimal import Decimal

# النموذج الحالي FuelQuotaForm يبقى كما هو
class FuelQuotaForm(forms.ModelForm):
    month = forms.DateField(
        widget=forms.DateInput(attrs={"type": "month"}),
        input_formats=["%Y-%m"], 
    )

    class Meta:
        model = FuelQuota
        # يجب تعديل الأسماء هنا لتناسب التسميات الجديدة إذا تم تغييرها
        fields = ["vehicle", "month", "allocated_quantity", "allocated_amount"]


from django import forms
from .models import FuelQuota

# ... (FuelQuotaForm يبقى كما هو)

class FuelQuotaAdditionForm(forms.ModelForm):
    """نموذج لإضافة كمية ومبلغ إضافي لمخصص الوقود"""
    # 🌟 يمكننا إضافة حقول غير موجودة في النموذج مباشرةً
    new_added_quantity = forms.DecimalField(
        max_digits=10, decimal_places=2, label="الكمية الإضافية المراد إضافتها (لتر)", min_value=0.01
    )
    new_added_amount = forms.DecimalField(
        max_digits=10, decimal_places=2, label="المبلغ الإضافي المراد إضافته (شيكل)", min_value=0.01
    )
    
    class Meta:
        model = FuelQuota
        # لا نضع أي حقول هنا، فسنستخدم الحقول المضافة بالأعلى
        fields = []
        
        
        
from django import forms
from .models import Maintenance
from django import forms
from .models import Maintenance, MaintenanceItem

from django import forms
from .models import Maintenance
from django.utils import timezone

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        # هنا نستثني الحقول التي لا تريد عرضها في الفورم
        exclude = ['invoice_number', 'invoice_image', 'end_date', 'vehicle', 'total_cost']


# forms.py
from django import forms
from .models import Maintenance

from django import forms
from .models import Maintenance

class MaintenanceInvoiceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = ["invoice_number", "invoice_image", "end_date"]
        widgets = {
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


FILTER_CHOICES = [
    ("monthly", "شهري"),
    ("yearly", "سنوي"),
    ("range", "من فترة إلى فترة"),
]

class MaintenanceFilterForm(forms.Form):
    filter_type = forms.ChoiceField(
        choices=FILTER_CHOICES, 
        label="نوع الفلترة",
        # Keep the onchange to trigger the JavaScript showFields function
        widget=forms.Select(attrs={"onchange": "showFields(this.value)"}) 
    )
    # Changed 'required=False' to be explicit, which is correct for optional fields
    month = forms.IntegerField(min_value=1, max_value=12, required=False, label="الشهر") 
    year = forms.IntegerField(min_value=2000, max_value=2100, required=False, label="السنة")
    
    start_date = forms.DateField(
        required=False, 
        label="من تاريخ", 
        widget=forms.DateInput(attrs={"type": "date"})
    )
    end_date = forms.DateField(
        required=False, 
        label="إلى تاريخ", 
        widget=forms.DateInput(attrs={"type": "date"})
    )
    
    # You might want to add a clean method to enforce required fields based on filter_type, 
    # but the current logic in the view handles this by checking 'if month and year' etc.
from .models import MaintenanceItem



from django import forms
from .models import Maintenance


from django import forms
from .models import MaintenanceItem
from django import forms
from .models import MaintenanceItem

from django import forms
from .models import MaintenanceItem

class MaintenanceItemForm(forms.ModelForm):
    class Meta:
        model = MaintenanceItem
        fields = ["description", "cost", "date", "image"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

from django.forms import modelformset_factory
from django import forms
from .models import Operation, OperationImage

from django import forms



from django import forms
from .models import Operation, VehiclesEquipment, StoreEquipment, CenterEquipment
# forms.py

from django.forms import inlineformset_factory
from .models import (
    Operation, OperationImage, 
    VehiclesEquipment, StoreEquipment, CenterEquipment
)
# forms.py (الكود الكامل)

from django import forms
from django.forms import inlineformset_factory, modelformset_factory 
# تأكد من استيراد modelformset_factory و inlineformset_factory إذا كنت تستخدمهما
# و Models الخاصة بك
from .models import (
    Operation, OperationImage, 
    VehiclesEquipment, StoreEquipment, CenterEquipment
) 



from django.forms import inlineformset_factory
from .models import (
    Operation, OperationImage, OperationVehicleEquipmentFile, 
    OperationStoreEquipmentFile, OperationCenterEquipmentFile,
    VehiclesEquipment, StoreEquipment, CenterEquipment 
)
import pandas as pd # نحتاجها إذا كنت تستخدمها لتحقق الإكسل

from .models import (
    Operation, OperationImage, OperationVehicleEquipmentFile, 
 
)
from django import forms
from django.forms import inlineformset_factory
from django.core.validators import RegexValidator, ValidationError
from django.utils.translation import gettext_lazy as _
import re 
# يجب أن يكون لديك مكتبة pandas مثبتة (pip install pandas)
import pandas as pd 

from .models import (
    Operation, OperationImage, OperationVehicleEquipmentFile, 
    OperationStoreEquipmentFile, OperationCenterEquipmentFile,
    VehiclesEquipment, StoreEquipment, CenterEquipment 
)



def validate_text_only(value):
    if value is None:
        return
    
    clean_value = str(value).strip()
    if not clean_value:
        return # السماح بالفراغ إذا لم يكن الحقل required

    # التحقق من وجود رقم (يمنع الأرقام بشكل قاطع)
    if re.search(r'[0-9]', clean_value):
        raise ValidationError(
            _('لا يمكن أن يحتوي هذا الحقل على أرقام (يجب أن يكون نصاً فقط).'),
            params={'value': value},
        )
    
    # يمكن إضافة تعبير عادي للتحقق من الأحرف المسموح بها إذا لزم الأمر
    pass 

# مدقق لأرقام الهواتف (يسمح بالأرقام ورموز الهاتف مثل + - () مسافة)
PHONE_REGEX = RegexValidator(
    regex=r'^\+?[\d\s\-\(\)]+$',
    message=_("يجب أن يكون رقم هاتف صالحاً. يمكن أن يحتوي على أرقام ورموز هاتف (+ - ()).")
)


VehicleFileFormSet = inlineformset_factory(
    Operation, OperationVehicleEquipmentFile, 
    fields=['file', 'caption'], extra=0, can_delete=True
)

StoreFileFormSet = inlineformset_factory(
    Operation, OperationStoreEquipmentFile, 
    fields=['file', 'caption'], extra=0, can_delete=True
)

CenterFileFormSet = inlineformset_factory(
    Operation, OperationCenterEquipmentFile, 
    fields=['file', 'caption'], extra=0, can_delete=True
)


class OperationImageForm(forms.ModelForm):
    # حقل 'caption' هنا يمكن أن يحتوي على نص وأرقام، لذا لا نطبق عليه validate_text_only
    class Meta:
        model = OperationImage
        fields = ['image', 'caption'] 

OperationImageFormSet = inlineformset_factory(
    Operation, 
    OperationImage, 
    form=OperationImageForm, 
    extra=5, 
    max_num=10, 
    can_delete=True
)

class OperationForm(forms.ModelForm):
    # حقول إضافية لتمكين الإدخال المتعدد اليدوي للمعدات
    new_vehicle_equipment_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'اكتب كل معدة على سطر جديد أو افصل بفاصلة...'}),
        required=False,
        label="إضافة معدات مركبة يدوياً",
        # ⭐️ الشرط 1: هذا الحقل يجب أن يكون نصاً فقط ⭐️
        validators=[validate_text_only] 
    )

    new_store_equipment_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'اكتب كل معدة على سطر جديد أو افصل بفاصلة...'}),
        required=False,
        label="إضافة معدات مخزن يدوياً"
    )

    new_center_equipment_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'اكتب كل معدة على سطر جديد أو افصل بفاصلة...'}),
        required=False,
        label="إضافة معدات مركز يدوياً"
    )

    # حقل رفع ملف الإكسل
    excel_import_file = forms.FileField(
        label='رفع ملف إكسل لإنشاء المركز والربط',
        help_text='سيتم إنشاء مركز واحد من ملف الإكسل (صف واحد) بدلاً من الإدخال اليدوي.',
        required=False,
        widget=forms.FileInput(attrs={'accept': '.xls,.xlsx'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        is_excel_upload = False
        if 'files' in kwargs and kwargs['files'].get('excel_import_file'):
            is_excel_upload = True
        
        # الحقول التي يجب أن تكون إجبارية في حالة الإدخال اليدوي
        required_fields_manual = ['governorate', 'center',]
        
        # ⭐️ الشرط 2: تطبيق الإلزامية المشروطة ⭐️
        for field_name in required_fields_manual:
            if field_name in self.fields:
                self.fields[field_name].required = not is_excel_upload
        
        # بالنسبة لحقول الأرقام والـ M2M وباقي الحقول: تبقى اختيارية (False) كما هي في الموديل
        
        if is_excel_upload:
            # إضافة الخيار الفارغ للمحافظة في حال رفع الإكسل (لأن الحقل أصبح اختياري)
            if 'governorate' in self.fields and self.fields['governorate'].choices:
                current_choices = list(self.fields['governorate'].choices)
                if not current_choices or current_choices[0][0] != '':
                    self.fields['governorate'].choices = [('', '---------')] + current_choices
        
        # ⭐️ الشرط 3: تطبيق المدققات على الحقول ⭐️
        
        # حقول نصوص فقط (اسم المركز)
        if 'center' in self.fields:
            self.fields['center'].validators.append(validate_text_only)
            
        # حقول أرقام (الهواتف)
        for field_name in ['landline', 'emergency_number', 'mobile']:
            if field_name in self.fields:
                 self.fields[field_name].validators.append(PHONE_REGEX)
                 
        # حقول الهدف والخدمات والمعدات النصية (هي CharField/TextField)
        # ومسموح فيها بالنص والأرقام (عدا new_vehicle_equipment_text الذي طبقنا عليه المدقق)
        # لذا لا يلزم مدقق إضافي هنا
        
        # التأكد من أن حقول الإدخال اليدوي غير مطلوبة أبداً
        for field_name in ['new_vehicle_equipment_text', 'new_store_equipment_text', 'new_center_equipment_text']:
             if field_name in self.fields:
                 self.fields[field_name].required = False

    class Meta:
        model = Operation
        fields = [
            'governorate', 'center','header_image', 'latitude', 'longitude', 'objective', 
            'services', 'landline', 'emergency_number', 'mobile', 
            'vehicle_equipment',
            'store_equipment',
            'center_equipment',   

        ]
        # إخفاء حقلي الإحداثيات (سيتم تعبئتها عبر الجافاسكريبت أو الإكسل)
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
        


# FormSets لملفات المعدات المتعددة (extra=3 للسماح برفع 3 ملفات افتراضياً)
class BaseEquipmentFileForm(forms.ModelForm):
    class Meta:
        fields = ['file', 'caption']

VehicleFileFormSet = inlineformset_factory(
    Operation, OperationVehicleEquipmentFile, 
    fields=['file', 'caption'], extra=0, can_delete=True
)

StoreFileFormSet = inlineformset_factory(
    Operation, OperationStoreEquipmentFile, 
    fields=['file', 'caption'], extra=0, can_delete=True
)

CenterFileFormSet = inlineformset_factory(
    Operation, OperationCenterEquipmentFile, 
    fields=['file', 'caption'], extra=0, can_delete=True
)



from django.forms import inlineformset_factory

from .models import Employee, DAYS_OF_WEEK


from django.forms import modelformset_factory
import datetime
from .models import Employee, WorkSchedule,Certificate,Operation

class EmployeeForm(forms.ModelForm):
    rank_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    # 🌟 1. تعريف job_description كحقل نموذج (Form Field) لاستخدام Textarea
    # هذا الحقل سيحل محل حقل job_description الموجود في الموديل
    job_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'style': 'width: 90%;'}), # 👈 أضفنا تنسيق هنا لتجنب الحاجة لتنسيق CSS معقد
        required=False,
        label="الوصف الوظيفي"
    )

    class Meta:
        model = Employee
        fields = [
            "operation", "name", "mobile", "address",
            "rank", "rank_date", "education_level", "job_description"
        ]
        # ❌ قم بإزالة exclude = ('job_description',) و custom __init__
        # لأن job_description هنا هو حقل نموذج قياسي ويجب أن يكون في fields
        
    # ❌ لا تحتاج إلى دالة __init__ مخصصة هنا، حذفها يحل المشكلة:
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['job_description'] = self.job_description


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ["name", "date", "file"]


WorkScheduleFormSet = modelformset_factory(
    WorkSchedule,
    fields=("day", "start", "end", "is_off"),
    extra=7,  # عدد الأيام (الافضل 7 بدل 1)
    widgets={
        "day": forms.Select(),
        "start": forms.TimeInput(attrs={"type": "time"}),
        "end": forms.TimeInput(attrs={"type": "time"}),
    }
)




from django import forms
from .models import Trip

from django import forms
from .models import Trip

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ["vehicle", "destination", 
                  "start_odometer", "start_odometer_image",
                  "end_odometer", "end_odometer_image", 
                  "date"]

from django import forms

from django import forms

from django import forms

FILTER_CHOICES = [
    ("monthly", "شهري"),
    ("yearly", "سنوي"),
    ("range", "حسب فترة"),
]

from django import forms
from django.core.exceptions import ValidationError

from django import forms
from django.core.exceptions import ValidationError

FILTER_CHOICES = [
    ("monthly", "شهري"),
    ("yearly", "سنوي"),
    ("range", "حسب فترة"),
]

class TripFilterForm(forms.Form):
    filter_type = forms.ChoiceField(
        choices=FILTER_CHOICES,
        label="نوع الفلترة",
        widget=forms.Select(attrs={"onchange": "showFields(this.value)"})
    )
    month = forms.IntegerField(min_value=1, max_value=12, required=False, label="الشهر")
    year = forms.IntegerField(min_value=2000, max_value=2100, required=False, label="السنة")
    start_date = forms.DateField(required=False, label="من تاريخ", widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(required=False, label="إلى تاريخ", widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        cleaned_data = super().clean()
        filter_type = cleaned_data.get("filter_type")

        # ... (Validation logic is correct)
        if filter_type == "monthly":
            month = cleaned_data.get("month")
            year = cleaned_data.get("year")
            if not month:
                self.add_error("month", "هذا الحقل مطلوب عند اختيار الفلترة الشهرية")
            if not year:
                self.add_error("year", "هذا الحقل مطلوب عند اختيار الفلترة الشهرية")

        elif filter_type == "yearly":
            year = cleaned_data.get("year")
            if not year:
                self.add_error("year", "هذا الحقل مطلوب عند اختيار الفلترة السنوية")

        elif filter_type == "range":
            start_date = cleaned_data.get("start_date")
            end_date = cleaned_data.get("end_date")
            if not start_date:
                self.add_error("start_date", "هذا الحقل مطلوب عند اختيار الفلترة حسب فترة")
            if not end_date:
                self.add_error("end_date", "هذا الحقل مطلوب عند اختيار الفلترة حسب فترة")
            elif start_date and end_date and start_date > end_date:
                # Use add_error on non_field_errors to show it outside specific fields
                self.add_error(None, "تاريخ البداية يجب أن يكون أصغر من تاريخ النهاية") 
                
        return cleaned_data
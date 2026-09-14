from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .forms import SearchForm
from .models import Search
import folium
import requests
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout

from django.views.decorators.cache import never_cache


@never_cache
def logout_view(request):
    logout(request)
    request.session.flush()  # يمسح السيشن بالكامل
    return redirect('login')

from django.contrib.auth import authenticate, login
from .forms import LoginForm

def login_view(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)   # ⭐ هاي أهم سطر
                return redirect('after_login_redirect')

            else:
                form.add_error(None, "البريد الإلكتروني أو كلمة المرور غير صحيحة")

    return render(request, 'login.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


# @login_required
# def after_login_redirect(request):
#     user = request.user

#     if user.is_superuser:
#         if user.groups.filter(name='InvestigationSuper').exists():
#             return redirect('Investigation/investigations_admin')
#         elif user.groups.filter(name='CatastropheSuper').exists():
#             return redirect('Catastrophe/catastrophes_admin')
#         elif user.groups.filter(name='PublicSafetySuper').exists():
#             return redirect('public_safety_superuser')
#         else:
#             return redirect('main')  # صفحة سوبر يوزر عامة ✅

#     elif user.is_staff:
#         if user.groups.filter(name='CatastropheStaff').exists():
#             return redirect('Catastrophe/catastrophes_user')
#         elif user.groups.filter(name='InvestigationStaff').exists():
#             return redirect('Investigation/investigation_staff')
#         elif user.groups.filter(name='PublicSafetyStaff').exists():
#             return redirect('public_safety_staff')
#         else:
#             return redirect('main')  # ❗ بدل login

#     else:
#         return redirect('main')  # ❗ بدل login


from django.shortcuts import redirect

def after_login_redirect(request):
    user = request.user
    return redirect('main_page')

# @login_required
# def public_safety_redirect(request):
#     user = request.user

#     if user.role in ['super_admin', 'governorate_admin', 'center_admin']:
#         return redirect('public_safety_superuser')
#     elif user.role == 'user':
#         return redirect('PublicSafety/publicSafety_user')
#     else:
#         return redirect('home')  # fallback لأي دور غير معروف

# @login_required
# def catastrophes_redirect(request):
#     user = request.user

#     if user.role in ['super_admin', 'governorate_admin', 'center_admin']:
#         return redirect('Catastrophe/catastrophes_admin')
#     elif user.role == 'user':
#         return redirect('Catastrophe/catastrophes_user')
#     else:
#         return redirect('home')  # fallback لأي دور غير معروف


# @login_required
# def investigations_redirect(request):
#     user = request.user

#     if user.role in ['super_admin', 'governorate_admin', 'center_admin']:
#         return redirect('Investigation/investigations_admin')
#     elif user.role == 'user':
#         return redirect('Investigation/investigation_staff')
#     else:
#         return redirect('home')  # fallback لأي دور غير معروف



from .models import Operation

from .models import Maintenance

def maintenance_list(request):
    maintenances = Maintenance.objects.select_related("vehicle").all().order_by("-date")
    invoice_number = request.GET.get("invoice_number")
    if invoice_number:
        maintenances = maintenances.filter(invoice_number__icontains=invoice_number)
    return render(request, "Maintenance/maintenance_list.html", {"maintenances": maintenances})

from .models import Maintenance
from .forms import MaintenanceItemForm
from .models import Maintenance, MaintenanceItem


def maintenance_item_create(request, maintenance_id):
    maintenance = get_object_or_404(Maintenance, pk=maintenance_id)

    if request.method == "POST":
        form = MaintenanceItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.maintenance = maintenance
            item.save()
            return redirect("Maintenance/maintenance_detail", pk=maintenance.id)
    else:
        form = MaintenanceItemForm()

    return render(request, "Maintenance/maintenance_item_form.html", {
        "form": form,
        "maintenance": maintenance
    })
from .forms import MaintenanceInvoiceForm

from .forms import MaintenanceInvoiceForm
from .models import Maintenance

def maintenance_detail(request, pk):
    maintenance = get_object_or_404(Maintenance, pk=pk)
    items = maintenance.items.all()  # الأعطال المرتبطة

    if request.method == "POST":
        form = MaintenanceInvoiceForm(request.POST, request.FILES, instance=maintenance)
        if form.is_valid():
            form.save()
            return redirect("Maintenance/maintenance_detail", pk=maintenance.id)
    else:
        form = MaintenanceInvoiceForm(instance=maintenance)

    return render(request, "Maintenance/maintenance_detail.html", {
        "maintenance": maintenance,
        "items": items,
        "form": form
    })


def maintenance_list_by_vehicle(request, vehicle_id):
    مركبة = get_object_or_404(Vehicle, pk=vehicle_id)
    الصيانات = مركبة.maintenances.order_by("-date")
    عدد_الصيانات = الصيانات.count()
    return render(request, "Maintenance/maintenance_list_by_vehicle.html", {
        "vehicle": مركبة,
        "الصيانات": الصيانات,
        "عدد_الصيانات": عدد_الصيانات,
    })


from django.db.models import Sum
from django.http import HttpResponse
from django.conf import settings

from .models import Vehicle, Maintenance, MaintenanceItem
from .forms import MaintenanceFilterForm

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from bidi.algorithm import get_display
import arabic_reshaper
import os


def calculate_monthly_maintenance(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    total_cost = None
    maintenance_items = []
    
    # Initialize form based on request method
    if request.method == "POST":
        form = MaintenanceFilterForm(request.POST)
        if form.is_valid():
            filter_type = form.cleaned_data.get("filter_type")
            
            # Base QuerySet
            base_qs = Maintenance.objects.filter(vehicle=vehicle)

            if filter_type == "monthly":
                month = form.cleaned_data.get("month")
                year = form.cleaned_data.get("year")
                if month is not None and year is not None:
                    qs = base_qs.filter(
                        date__year=year,
                        date__month=month
                    ).prefetch_related('items')
                    maintenance_items = qs
                    total_cost = qs.aggregate(total=Sum("total_cost"))["total"] or 0
                
            elif filter_type == "yearly":
                year = form.cleaned_data.get("year")
                if year is not None:
                    qs = base_qs.filter(
                        date__year=year
                    ).prefetch_related('items')
                    maintenance_items = qs
                    total_cost = qs.aggregate(total=Sum("total_cost"))["total"] or 0
                
            elif filter_type == "range":
                start_date = form.cleaned_data.get("start_date")
                end_date = form.cleaned_data.get("end_date")
                if start_date and end_date:
                    qs = base_qs.filter(
                        date__range=[start_date, end_date]
                    ).prefetch_related('items')
                    maintenance_items = qs
                    total_cost = qs.aggregate(total=Sum("total_cost"))["total"] or 0
    else:
        form = MaintenanceFilterForm()
        

    return render(request, "Maintenance/calculate_monthly_maintenance.html", {
        "vehicle": vehicle,
        "form": form,
        "total_cost": total_cost,
        "maintenance_items": maintenance_items
    })
    
from io import BytesIO
from django.http import HttpResponse
from django.db.models import Sum
from datetime import datetime
import os

from .models import Vehicle, Maintenance, MaintenanceItem

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

import arabic_reshaper
from bidi.algorithm import get_display
def download_monthly_maintenance_pdf(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    filter_type = request.GET.get("filter_type")
    month = request.GET.get("month")
    year = request.GET.get("year")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    qs = Maintenance.objects.filter(vehicle=vehicle).prefetch_related('items')

    # تطبيق الفلترة
    if filter_type == "monthly" and month and year:
        qs = qs.filter(date__year=int(year), date__month=int(month))
    elif filter_type == "yearly" and year:
        qs = qs.filter(date__year=int(year))
    elif filter_type == "range" and start_date and end_date:
        qs = qs.filter(date__range=[start_date, end_date])

    total_cost = qs.aggregate(total=Sum("total_cost"))["total"] or 0
    maintenance_items = qs.order_by('-date')

    # إنشاء PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    font_path = os.path.join('static', 'fonts', 'Amiri-Regular.ttf')  # تأكد من مسار الخط
    pdfmetrics.registerFont(TTFont("Arabic", font_path))
    pdf.setFont("Arabic", 14)

    def write_arabic(text, x, y):
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        pdf.drawRightString(x, y, bidi_text)

    # بدء الكتابة على الصفحة
    y = 800
    write_arabic(f"تقرير صيانة المركبة: {vehicle.vehicle_number}", 550, y)
    y -= 30
    write_arabic(f"عدد الصيانات: {maintenance_items.count()}", 550, y)
    y -= 30
    write_arabic(f"💰 المجموع الكلي: {total_cost} شيكل", 550, y)
    y -= 40

    write_arabic("📋 تفاصيل الصيانة:", 550, y)
    y -= 30

    for maintenance in maintenance_items:
        # عنوان الصيانة
        write_arabic(f"{maintenance.garage} - {maintenance.date} - إجمالي: {maintenance.total_cost} شيكل", 550, y)
        y -= 25

        # البنود الفرعية
        for item in maintenance.items.all():
            write_arabic(f"   • {item.description}: {item.cost} شيكل", 550, y)
            y -= 20

            # إذا وصلنا لنهاية الصفحة، أضف صفحة جديدة
            if y < 100:
                pdf.showPage()
                pdf.setFont("Arabic", 14)
                y = 800
        y -= 10  # مسافة بين الصيانات

    pdf.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")


from .models import Vehicle, Maintenance
from .forms import MaintenanceForm
from django.urls import reverse


def maintenance_create(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method == "POST":
        form = MaintenanceForm(request.POST, request.FILES)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.vehicle = vehicle
            maintenance.save()
            return redirect("/vehicles/?source=maintenance")
    else:
        form = MaintenanceForm()

    return render(request, "Maintenance/maintenance_form.html", {"form": form, "vehicle": vehicle})


from django.shortcuts import render
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import permission_required
from django.core.cache import cache
from django.db.models import Count, Exists, OuterRef, Q
from django.utils import timezone

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from map.models import (
    UserAssignment,
    Governorate,
    Center,
    OrganizationUnit,
    Operation,
    Vehicle,
    Notification,
)


def clear_user_cache(user_id):
    cache.delete(f"user_operations_{user_id}")
    cache.delete(f"user_notifications_{user_id}")
    cache.delete(f"user_notifications_{user_id}_count")
def operations_map(request):
    user = request.user

    if not user.is_authenticated:
        return HttpResponseForbidden("خطأ: يجب تسجيل الدخول أولاً للوصول إلى هذه الصفحة.")

    # جلب التعيين الحالي للمستخدم
    assignment = UserAssignment.objects.filter(
        user=user,
        is_active=True
    ).select_related(
        'unit',
        'unit__linked_governorate',
        'unit__linked_center',
        'role'
    ).first()

    cache_key = f"user_operations_{user.id}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'Operation/operations_map.html', cached_data)

    # تحديد المسميات للعرض
    if user.is_superuser:
        role_name = "سيادة اللواء"
        unit_name = "المديرية العامة للدفاع المدني"
    else:
        role_name = assignment.role.name if assignment and assignment.role else ""
        unit_name = assignment.unit.name if assignment and assignment.unit else ""

    today = timezone.localdate()

    operations_queryset = Operation.objects.select_related(
        'center', 'governorate'
    ).annotate(
        # إحصائيات المركبات
        in_service_count=Count('center__vehicle', filter=Q(center__vehicle__status='in_service'), distinct=True),
        out_of_service_count=Count('center__vehicle', filter=~Q(center__vehicle__status='in_service'), distinct=True),
        total_vehicles=Count('center__vehicle', distinct=True),

        total_employees=Count('employees', distinct=True),
        present_employees=Count(
            'employees',
            filter=Q(
                employees__attendance_records__date=today,
                employees__attendance_records__status='present'
            ),
            distinct=True
        ),
        absent_employees=Count(
            'employees',
            filter=Q(
                employees__attendance_records__date=today
            ) & ~Q(
                employees__attendance_records__status='present'
            ),
            distinct=True
        )
    )

    # ===================================
    # تصفية العمليات حسب الصلاحيات
    # ===================================
    if user.is_superuser:
        pass # يظهر كل شيء

    elif assignment and assignment.unit:
        role_name_str = assignment.role.name if assignment.role else ""
        unit_name_str = assignment.unit.name if assignment.unit else ""

        # 1. مدير المحافظة
        if role_name_str == "مدير المحافظة" and assignment.unit.linked_governorate:
            operations_queryset = operations_queryset.filter(governorate=assignment.unit.linked_governorate)

        # 2. مدير إدارة الموارد البشرية (صلاحية شاملة للمديرية العامة)
        elif role_name_str == "مدير ادارة" and unit_name_str == "ادارة الموارد للبشرية/المديرية العامة":
            pass # يرى كل العمليات

        # 3. مدير إدارة الموارد البشرية في أماكن أخرى (صلاحية محدودة)
        elif role_name_str == "مدير ادارة" and "ادارة الموارد للبشرية" in unit_name_str:
            filters = Q()
            if assignment.unit.linked_governorate:
                filters |= Q(governorate=assignment.unit.linked_governorate)
            if assignment.unit.linked_center:
                filters |= Q(center=assignment.unit.linked_center)
            
            if filters:
                operations_queryset = operations_queryset.filter(filters)
            else:
                operations_queryset = operations_queryset.none()
        
        # 4. صلاحية "مدير مركز"
        elif role_name_str == "مدير المركز" and assignment.unit.linked_center:
            operations_queryset = operations_queryset.filter(center=assignment.unit.linked_center)

        # 5. الربط المباشر بمركز (لأي دور آخر)
        elif assignment.unit.linked_center:
            operations_queryset = operations_queryset.filter(center=assignment.unit.linked_center)

        # 6. الربط المباشر بمحافظة
        elif assignment.unit.linked_governorate:
            operations_queryset = operations_queryset.filter(governorate=assignment.unit.linked_governorate)

        else:
            operations_queryset = operations_queryset.none()
    else:
        operations_queryset = operations_queryset.none()

    operations = list(operations_queryset)

    context = {
        'operations': operations,
        'assignment': assignment,
        'role_name': role_name,
        'unit_name': unit_name,
    }

    cache.set(cache_key, context, timeout=20)
    
    return render(request, 'Operation/operations_map.html', context)

import os
from io import BytesIO

import arabic_reshaper
from bidi.algorithm import get_display

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .models import (
    AttendanceApproval,
    Employee,
    EmployeeAttendance,
    Notification,
    Operation,
)

@login_required
def print_attendance_pdf(request, operation_id):
    operation = get_object_or_404(Operation, id=operation_id)
    today = timezone.now().date()

    status_filter = request.GET.get('status', 'all')

    records = EmployeeAttendance.objects.filter(
        employee__operation=operation,
        date=today
    )

    if status_filter in ['present', 'vacation', 'mission', 'early_leave']:
        records = records.filter(status=status_filter)

    last_updated_record = records.order_by('-updated_at').first()
    last_update = last_updated_record.updated_at if last_updated_record else None

    duty_officer_name = getattr(last_updated_record, 'duty_officer_name', '') if last_updated_record else ''

    sorted_records = sorted(
        records,
        key=lambda x: {
            'present': 0,
            'mission': 1,
            'early_leave': 2,
            'vacation': 3
        }.get(x.status, 4)
    )

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    font_path = os.path.join('static', 'fonts', 'Amiri-Regular.ttf')
    pdfmetrics.registerFont(TTFont("Arabic", font_path))

    elements = []

    def r(text):
        return get_display(arabic_reshaper.reshape(str(text)))


    header_ar_style = ParagraphStyle(
        'HeaderAr',
        fontName='Arabic',
        fontSize=11,
        leading=15,
        alignment=2,  # محاذاة لليمين
        textColor=colors.HexColor('#0f172a')
    )

    header_en_style = ParagraphStyle(
        'HeaderEn',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=14,
        alignment=0,  # محاذاة لليسار
        textColor=colors.HexColor('#0f172a')
    )

    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Arabic',
        fontSize=15,
        leading=20,
        alignment=1,
        textColor=colors.HexColor('#1e293b')
    )

    meta_style = ParagraphStyle(
        'MetaText',
        fontName='Arabic',
        fontSize=9,
        leading=13,
        alignment=1,
        textColor=colors.HexColor('#475569')
    )

    th_style = ParagraphStyle(
        'TableHeader',
        fontName='Arabic',
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.whitesmoke
    )

    td_style = ParagraphStyle(
        'TableCell',
        fontName='Arabic',
        fontSize=9,
        leading=13,
        alignment=1,
        textColor=colors.HexColor('#334155')
    )

    sig_label_style = ParagraphStyle(
        'SigLabel',
        fontName='Arabic',
        fontSize=9.5,
        leading=14,
        alignment=2,
        textColor=colors.HexColor('#1e293b')
    )

    center_name_ar = getattr(operation, 'center', 'المركز')
    center_name_en = getattr(operation, 'center_en', 'AL-BIREH CENTER')

    # معالجة كل سطر عربي على حدة لتجنب تضارب وسوم <br/> مع مكتبة arabic_reshaper
    line1_ar = r("دولة فلسطين")
    line2_ar = r("وزارة الداخلية")
    line3_ar = r(f"{center_name_ar}")
    
    right_text = f"{line1_ar}<br/>{line2_ar}<br/>{line3_ar}"
    left_text = f"STATE OF PALESTINE<br/>MINISTRY OF INTERIOR<br/>{center_name_en}"

    # تحديد مسار صورة اللوجو المحدد media/logo.png
    logo_path = os.path.join(settings.BASE_DIR, 'media', 'logo.png')
    logo_cell = ""

    if os.path.exists(logo_path):
        img = Image(logo_path, width=75, height=75)
        img.hAlign = 'CENTER'
        logo_cell = img

    header_top_data = [
        [
            Paragraph(left_text, header_en_style),
            logo_cell,
            Paragraph(right_text, header_ar_style)
        ]
    ]

    header_top_table = Table(header_top_data, colWidths=[190, 140, 190])
    header_top_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))

    elements.append(header_top_table)
    elements.append(Spacer(1, 12))

    filter_titles = {
        'present': ' (الحاضرون فقط)',
        'early_leave': ' (المغادرون فقط)',
        'vacation': ' (الإجازات فقط)',
        'mission': ' (المهام فقط)'
    }

    subtitle_text = filter_titles.get(status_filter, '')
    last_up_str = last_update.strftime('%d/%m/%Y %H:%M') if last_update else '-'

    header_data = [
        [
            Paragraph(
                r(f"كشف دوام المرتب "),
                title_style
            )
        ],
        [Spacer(1, 3)],
        [
            Paragraph(
                r(f"التاريخ: {today.strftime('%d/%m/%Y')} "),
                meta_style
            )
        ]
    ]

    header_table = Table(header_data, colWidths=[520])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 15))

    # =========================
    # 3. جدول الدوام
    # =========================
    table_data = [
        [
            Paragraph(r("ملاحظات"), th_style),
            Paragraph(r("السبب"), th_style),
            Paragraph(r("الحالة"), th_style),
            Paragraph(r("اسم الموظف / المرتب"), th_style)
        ]
    ]

    status_map = {
        'present': r("حاضر"),
        'early_leave': r("مغادرة"),
        'vacation': r("إجازة"),
        'mission': r("مهمة")
    }

    reason_map = {
        'sick': r("مرضية"),
        'travel': r("سفر"),
        'other': r("غير ذلك"),
        'personal': r("شخصي")
    }

    for rec in sorted_records:
        table_data.append([
            Paragraph(r(rec.notes or "-"), td_style),
            Paragraph(reason_map.get(rec.leave_reason, r("-")), td_style),
            Paragraph(status_map.get(rec.status, r("-")), td_style),
            Paragraph(r(rec.employee.name), td_style)
        ])

    col_widths = [160, 90, 90, 180]
    main_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    ts = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]

    for i in range(1, len(table_data)):
        if i % 2 == 0:
            ts.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8fafc')))

    main_table.setStyle(TableStyle(ts))
    elements.append(main_table)
    elements.append(Spacer(1, 20))

    # =========================
    # 4. التوقيع
    # =========================
    print_time_str = timezone.now().strftime('%d/%m/%Y %H:%M')
    duty_officer_display = duty_officer_name.strip() if duty_officer_name else '......................'

    sig_contents = [
        [Paragraph(r(f"الضابط المناوب (إن وجد): {duty_officer_display}"), sig_label_style)],
        [Spacer(1, 6)],
        [Paragraph(r("التوقيع: ......................"), sig_label_style)]
    ]

    sig_inner_table = Table(sig_contents, colWidths=[240])
    sig_inner_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    wrapper_table = Table([[sig_inner_table]], colWidths=[260])
    wrapper_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
    ]))
    wrapper_table.hAlign = 'RIGHT'

    elements.append(wrapper_table)

    # =========================
    # بناء المستند وإرساله
    # =========================
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="attendance_{operation.id}.pdf"'
    response.write(pdf)

    return response
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Max
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import (
    AttendanceApproval,
    EmployeeAttendance,
    Operation,
    UserAssignment,
)
from .services import notify_governorate_directors

logger = logging.getLogger(__name__)
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Max
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import (
    Operation,
    UserAssignment,
    EmployeeAttendance,
    AttendanceApproval,
)

from .services import notify_governorate_directors


logger = logging.getLogger(__name__)

@login_required
def add_attendance(request, operation_id):

    # =========================================================
    # 1. جلب العملية
    # =========================================================

    operation = get_object_or_404(
        Operation.objects.select_related(
            "center__governorate"
        ),
        id=operation_id
    )

    employees = operation.employees.all()
    today = timezone.now().date()

    APP_NAME = "map"

    # =========================================================
    # 2. جلب التعيين الوظيفي النشط للمستخدم
    # =========================================================

    assignment = (
        UserAssignment.objects
        .select_related(
            "unit",
            "unit__linked_center",
            "unit__linked_governorate",
            "role",
        )
        .filter(
            user=request.user,
            is_active=True
        )
        .first()
    )

    # =========================================================
    # 3. التحقق من التعيين
    # =========================================================

    if not request.user.is_superuser:

        if not assignment or not assignment.unit:

            return HttpResponseForbidden(
                "لا يوجد لديك تعيين وظيفي نشط."
            )

    # =========================================================
    # 4. المحافظة التابعة للعملية
    # =========================================================

    operation_governorate = (
        operation.center.governorate
    )

    # =========================================================
    # 5. صلاحية تعديل الدوام
    # =========================================================

    can_edit_attendance = (
        request.user.is_superuser
        or (
            assignment
            and assignment.unit
            and request.user.has_perm(
                f"{APP_NAME}.can_manage_center_attendance"
            )
            and assignment.unit.linked_center
            == operation.center
            and assignment.unit.linked_governorate
            == operation_governorate
        )
    )

    # =========================================================
    # 6. صلاحية اعتماد الدوام
    # =========================================================

    can_approve_attendance_perm = (
        request.user.is_superuser
        or (
            assignment
            and assignment.unit
            and assignment.role
            and assignment.role.name
            == "مدير المحافظة"
            and request.user.has_perm(
                f"{APP_NAME}.can_approve_directorate_attendance"
            )
            and assignment.unit.linked_governorate
            == operation_governorate
        )
    )

    # =========================================================
    # 7. هل المستخدم مدير محافظة؟
    # =========================================================

    is_manager = bool(
        request.user.is_superuser
        or (
            assignment
            and assignment.role
            and assignment.role.name
            == "مدير المحافظة"
        )
    )

    # =========================================================
    # 8. هل المستخدم ضابط مناوب؟
    # =========================================================

    is_duty_officer = bool(
        can_edit_attendance
        and not is_manager
    )

    # =========================================================
    # 9. إنشاء سجلات الدوام لليوم إذا لم تكن موجودة
    # =========================================================

    existing_records = EmployeeAttendance.objects.filter(
        employee__operation=operation,
        date=today
    )

    if not existing_records.exists():

        attendance_list = [
            EmployeeAttendance(
                employee=emp,
                date=today,
                status="present",
                leave_reason="",
                notes="",
                duty_officer_name=""
            )
            for emp in employees
        ]

        EmployeeAttendance.objects.bulk_create(
            attendance_list
        )

    # =========================================================
    # 10. جلب الاعتماد الحالي
    # =========================================================

    center_approval = (
        AttendanceApproval.objects.filter(
            operation=operation,
            date=today,
            approval_type="directorate",
            approved=True,
            is_active=True
        )
        .first()
    )

    # =========================================================
    # 11. معالجة POST
    # =========================================================

    if request.method == "POST":

        action = request.POST.get("action")

        # =====================================================
        # A. اعتماد الدوام
        # =====================================================

        if action == "approve":

            if not can_approve_attendance_perm:

                messages.error(
                    request,
                    "ليس لديك صلاحية اعتماد الدوام "
                    "لمديرية هذه المحافظة."
                )

                return redirect(
                    "add_attendance",
                    operation_id=operation.id
                )

            # -----------------------------------------------
            # منع الاعتماد المكرر
            # -----------------------------------------------

            if center_approval:

                messages.warning(
                    request,
                    "تم اعتماد دوام هذا المركز "
                    "مسبقاً لليوم."
                )

                return redirect(
                    "add_attendance",
                    operation_id=operation.id
                )

            # -----------------------------------------------
            # إنشاء الاعتماد
            # -----------------------------------------------

            try:

                AttendanceApproval.objects.create(
                    operation=operation,
                    date=today,
                    approval_type="directorate",
                    approved=True,
                    approved_by=request.user,
                    approved_at=timezone.now(),
                    is_active=True
                )

                messages.success(
                    request,
                    "تم تسجيل اعتماد إدارة المديرية بنجاح."
                )

            except Exception as e:

                logger.exception(
                    "Attendance Approval Error: %s",
                    e
                )

                messages.error(
                    request,
                    "حدث خطأ أثناء اعتماد الدوام."
                )

            return redirect(
                "add_attendance",
                operation_id=operation.id
            )

        # =====================================================
        # B. التحقق من صلاحية التعديل
        # =====================================================

        if not can_edit_attendance:

            messages.error(
                request,
                "ليس لديك صلاحية تعديل بيانات الدوام "
                "لهذا المركز."
            )

            return redirect(
                "add_attendance",
                operation_id=operation.id
            )

        # =====================================================
        # C. اسم الضابط المناوب
        # =====================================================

        duty_officer_name = (
            request.POST
            .get("duty_officer_name", "")
            .strip()
        )

        # =====================================================
        # D. حفظ بيانات الدوام
        # =====================================================

        try:

            with transaction.atomic():

                for emp in employees:

                    # -----------------------------------------
                    # الحالة
                    # -----------------------------------------

                    status = request.POST.get(
                        f"status_{emp.id}"
                    )

                    # -----------------------------------------
                    # إذا لم تصل الحالة
                    # -----------------------------------------

                    if not status:

                        status = "present"

                    # -----------------------------------------
                    # سبب الإجازة
                    # -----------------------------------------

                    if status == "vacation":

                        reason = (
                            request.POST.get(
                                f"reason_{emp.id}",
                                ""
                            )
                            .strip()
                        )

                    else:

                        reason = ""

                    # -----------------------------------------
                    # الملاحظات
                    # -----------------------------------------

                    note = (
                        request.POST.get(
                            f"note_{emp.id}",
                            ""
                        )
                        .strip()
                    )

                    # -----------------------------------------
                    # البيانات الجديدة
                    # -----------------------------------------

                    update_fields = {
                        "status": status,
                        "leave_reason": reason,
                        "notes": note,
                        "duty_officer_name":
                            duty_officer_name,
                        "updated_by":
                            request.user,
                    }

                    # -----------------------------------------
                    # إنشاء أو تعديل السجل
                    # -----------------------------------------

                    EmployeeAttendance.objects.update_or_create(
                        employee=emp,
                        date=today,
                        defaults=update_fields
                    )

            logger.info(
                "Attendance saved successfully. "
                "Operation=%s User=%s",
                operation.id,
                request.user.username
            )

        except Exception as e:

            logger.exception(
                "Attendance Save Error: %s",
                e
            )

            messages.error(
                request,
                "حدث خطأ أثناء حفظ بيانات الدوام."
            )

            return redirect(
                "add_attendance",
                operation_id=operation.id
            )

        # =====================================================
        # E. إلغاء الاعتماد السابق
        # =====================================================

        if center_approval:

            try:

                center_approval.is_active = False
                center_approval.revoked_at = timezone.now()

                center_approval.save(
                    update_fields=[
                        "is_active",
                        "revoked_at"
                    ]
                )

                logger.info(
                    "Previous attendance approval revoked. "
                    "Operation=%s",
                    operation.id
                )

            except Exception as e:

                logger.exception(
                    "Approval revoke error: %s",
                    e
                )

        # =====================================================
        # F. إرسال الإشعار
        #
        # مهم:
        # فشل الإشعار لن يفشل حفظ الدوام
        # =====================================================

        try:

            editor_name = (
                duty_officer_name
                or request.user.get_full_name()
                or request.user.username
            )

            logger.info(
                "Starting attendance notification. "
                "Operation=%s Editor=%s",
                operation.id,
                editor_name
            )

            notify_governorate_directors(
                operation=operation,
                editor_name=editor_name
            )

            logger.info(
                "Attendance notification completed. "
                "Operation=%s",
                operation.id
            )

        except Exception as notify_err:

            logger.exception(
                "Notification Error. "
                "Operation=%s Error=%s",
                operation.id,
                notify_err
            )

        # =====================================================
        # G. رسالة النجاح
        # =====================================================

        if duty_officer_name:

            messages.success(
                request,
                "تم حفظ البيانات بنجاح بواسطة "
                f"الضابط المناوب: "
                f"{duty_officer_name}"
            )

        else:

            messages.success(
                request,
                "تم حفظ بيانات الدوام بنجاح."
            )

        # =====================================================
        # H. العودة للصفحة
        # =====================================================

        return redirect(
            "add_attendance",
            operation_id=operation.id
        )

    # =========================================================
    # 12. تجهيز سجلات الدوام
    # =========================================================

    records = {
        rec.employee_id: rec
        for rec in EmployeeAttendance.objects.filter(
            employee__operation=operation,
            date=today
        )
    }

    # =========================================================
    # 13. جميع الاعتمادات الفعالة
    # =========================================================

    all_approvals = (
        AttendanceApproval.objects.filter(
            operation=operation,
            date=today,
            is_active=True
        )
        .select_related(
            "approved_by"
        )
    )

    # =========================================================
    # 14. الاعتمادات الملغاة
    # =========================================================

    revoked_approvals = (
        AttendanceApproval.objects.filter(
            operation=operation,
            date=today,
            is_active=False
        )
        .select_related(
            "approved_by"
        )
    )

    # =========================================================
    # 15. آخر تعديل
    # =========================================================

    last_update = (
        EmployeeAttendance.objects
        .filter(
            employee__operation=operation,
            date=today
        )
        .aggregate(
            Max("updated_at")
        )
        ["updated_at__max"]
    )

    # =========================================================
    # 16. آخر سجل
    # =========================================================

    last_record = (
        EmployeeAttendance.objects
        .filter(
            employee__operation=operation,
            date=today
        )
        .order_by(
            "-updated_at"
        )
        .first()
    )

    # =========================================================
    # 17. آخر ضابط مناوب
    # =========================================================

    last_duty_officer = (
        getattr(
            last_record,
            "duty_officer_name",
            ""
        )
        if last_record
        else ""
    )

    # =========================================================
    # 18. Context
    # =========================================================

    context = {

        "operation": operation,

        "employees": employees,

        "records": records,

        "all_approvals": all_approvals,

        "revoked_approvals": revoked_approvals,

        "center_approval": center_approval,

        "can_edit_attendance":
            can_edit_attendance,

        "can_approve_attendance":
            (
                can_approve_attendance_perm
                and not center_approval
            ),

        "can_approve_attendance_perm":
            can_approve_attendance_perm,

        "last_update":
            last_update,

        "last_duty_officer":
            last_duty_officer,

        "is_manager":
            is_manager,

        "is_duty_officer":
            is_duty_officer,
    }

    # =========================================================
    # 19. Render
    # =========================================================

    return render(
        request,
        "Employees/add_attendance.html",
        context
    )



def mark_notification_as_read(request, noti_id):
    try:
        # التأكد أن الإشعار يخص المستخدم الحاليخ
        notification = get_object_or_404(Notification, id=noti_id, user=request.user)
        if not notification.read:
            notification.read = True
            notification.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

from django.views.decorators.http import require_POST
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Notification, VehicleStatusNotification

@login_required
@require_POST
def mark_all_notifications_as_read(request):
    try:
        # 1. تحديث الإشعارات العامة للمستخدم (مثل مواعيد الترخيص والتأمين)
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        
        # 2. تحديث إشعارات حالات المركبات
        # إذا كانت الإشعارات مرتبطة بالمستخدم مباشرة أو بالمركبات التابعة لنطاقه
        VehicleStatusNotification.objects.filter(read=False).update(read=True)

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

from django.contrib import messages
from django.db import transaction


import pandas as pd  # تأكد من تثبيت pandas و openpyxl

from .models import (
    Operation,
    OperationImage,
    OperationVehicleEquipmentFile,
    OperationStoreEquipmentFile,
    OperationCenterEquipmentFile,
    VehiclesEquipment,
    StoreEquipment,
    CenterEquipment
)


from .forms import (
    OperationForm,
    OperationImageFormSet,
    VehicleFileFormSet,
    StoreFileFormSet,
    CenterFileFormSet
)
# 🔹 دالة مساعدة لفصل النصوص للمعدات
def split_equips(equip_text):
    if not equip_text:
        return []
    return [e.strip() for e in equip_text.replace('\n', ',').split(',') if e.strip()]


# 🔹 دالة لمعالجة وإنشاء المعدات
def process_equipment(equip_text, EquipmentModel, operation, m2m_field_name):
    raw_equips = split_equips(equip_text)
    for equip_name in raw_equips:
        equip_obj, _ = EquipmentModel.objects.get_or_create(name=equip_name)
        getattr(operation, m2m_field_name).add(equip_obj)


import uuid
import pandas as pd

from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Operation, Notification, UserAssignment
from .forms import (
    OperationForm,
    OperationImageFormSet,
    VehicleFileFormSet,
    StoreFileFormSet,
    CenterFileFormSet,
)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
def send_notification(operation):
    try:
        channel_layer = get_channel_layer()
        governorate = operation.governorate

        managers = UserAssignment.objects.filter(
            level='governorate',
            governorate=governorate
        )

        for manager in managers:
            message_text = f"📢 تم إضافة مركز جديد: {operation.center} في محافظة {governorate.name}"

            # ✅ تخزين مرة واحدة فقط
            Notification.objects.create(
                user=manager.user,
                message=message_text
            )

            # ✅ إرسال WebSocket
            async_to_sync(channel_layer.group_send)(
                f"user_{manager.user.id}",
                {
                    "type": "send_notification",
                    "message": message_text
                }
            )

    except Exception as e:
        print("❌ خطأ:", e)


from django.contrib import messages
from django.shortcuts import render, redirect
import uuid

@transaction.atomic
def add_operation(request):
    # 1. التوكن لمنع الإرسال المكرر
    if request.method == "GET":
        request.session['operation_form_token'] = str(uuid.uuid4())

    # 2. تهيئة النماذج (في حالة POST نمرر البيانات، في GET نمرر None)
    if request.method == 'POST':
        form = OperationForm(request.POST, request.FILES)
        image_formset = OperationImageFormSet(request.POST, request.FILES, prefix='images')
        vehicle_files_formset = VehicleFileFormSet(request.POST, request.FILES, prefix='vehicle_files')
        store_files_formset = StoreFileFormSet(request.POST, request.FILES, prefix='store_files')
        center_files_formset = CenterFileFormSet(request.POST, request.FILES, prefix='center_files')

        # التحقق من التوكن
        form_token = request.POST.get("form_token")
        if form_token != request.session.get("operation_form_token"):
            messages.warning(request, "⚠️ تم إرسال النموذج مسبقاً.")
            return redirect('Operation/add_operation')

        # التحقق من صحة جميع النماذج
        if all([form.is_valid(), image_formset.is_valid(), vehicle_files_formset.is_valid(),
                store_files_formset.is_valid(), center_files_formset.is_valid()]):
            
            # تنفيذ الحفظ
            operation = form.save()
            image_formset.instance = operation
            image_formset.save()
            # ... (حفظ باقي الـ Formsets بنفس الطريقة) ...
            
            request.session.pop("operation_form_token", None)
            messages.success(request, "✅ تم إضافة المركز بنجاح!")
            return redirect('Operation/operation_detail', pk=operation.pk)
        else:
            # إذا فشل التحقق، نقوم بعرض رسالة خطأ شاملة
            messages.error(request, "❌ فشلت عملية الإضافة، يرجى مراجعة الحقول التي تحتوي على أخطاء.")
    else:
        # حالة GET
        form = OperationForm()
        image_formset = OperationImageFormSet(prefix='images')
        vehicle_files_formset = VehicleFileFormSet(prefix='vehicle_files')
        store_files_formset = StoreFileFormSet(prefix='store_files')
        center_files_formset = CenterFileFormSet(prefix='center_files')

    return render(request, 'Operation/add_operation.html', {
        'form': form,
        'image_formset': image_formset,
        'vehicle_files_formset': vehicle_files_formset,
        'store_files_formset': store_files_formset,
        'center_files_formset': center_files_formset,
    })  
    
def notifications_list(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    return render(request, 'notifications/list.html', {'notifications': notifications})


def operation_detail(request, pk):
    center = get_object_or_404(
        Operation.objects.prefetch_related(
            'vehicle_equipment',
            'store_equipment',
            'center_equipment',
            'center_images',
            'vehicle_files', 
            'store_files',   
            'center_files'  
        ), 
        pk=pk
    )
    
    context = {
        'center': center,
    }
    
    messages.success(request, "✅ تم إضافة المركز والمعدات بنجاح!")
    return render(request, 'Operation/operation_detail.html', context)





from .models import Operation, VehiclesEquipment, StoreEquipment, CenterEquipment
from .forms import OperationForm  



def process_new_equipment(operation_instance, form_data, model_class, field_name):
   
    equipment_text = form_data.get(field_name)
    if not equipment_text:
        return

    # 2. تقسيم النص (يفصل بالسطر الجديد أو الفاصلة)
    # يمكننا استبدال الفواصل والسطور الجديدة بفاصل موحد ثم تقسيمها
    equipment_list = []
    # استبدال الفواصل والأسطر الجديدة (أو أي فاصل آخر)
    raw_list = equipment_text.replace('\n', ',').replace('،', ',').split(',')
    
    for item in raw_list:
        clean_item = item.strip()
        if clean_item:
            equipment_list.append(clean_item)

    if not equipment_list:
        return

    # 3. إيجاد أو إنشاء المعدات وربطها
    related_set = getattr(operation_instance, field_name.replace('new_', '').replace('_text', ''))

    for equipment_name in equipment_list:
        # البحث عن الكائن، إذا لم يوجد يتم إنشاؤه
        equipment_obj, created = model_class.objects.get_or_create(
            name=equipment_name
        )
        # 4. ربط الكائن الجديد بالعملية (لن يضيفه مرتين إذا كان موجوداً بالفعل)
        related_set.add(equipment_obj)


from .models import (
    Operation, OperationImage,
    OperationVehicleEquipmentFile, OperationStoreEquipmentFile, OperationCenterEquipmentFile,
    VehiclesEquipment, StoreEquipment, CenterEquipment
)


from .forms import (
    OperationForm,
    OperationImageFormSet,
    VehicleFileFormSet,
    StoreFileFormSet,
    CenterFileFormSet
)


from .utils import process_new_equipment

def split_equips(equip_text):
    if not equip_text:
        return []
    return [e.strip() for e in equip_text.replace('\n', ',').split(',') if e.strip()]

def process_equipment(equip_text, EquipmentModel, operation, m2m_field_name):
    raw_equips = split_equips(equip_text)
    for equip_name in raw_equips:
        equip_obj, created = EquipmentModel.objects.get_or_create(name=equip_name)
        getattr(operation, m2m_field_name).add(equip_obj)

@transaction.atomic
def update_operation(request, pk):
    operation = get_object_or_404(Operation, pk=pk)
    
    if request.method == 'POST':
        form = OperationForm(request.POST, request.FILES, instance=operation)
        
        image_formset = OperationImageFormSet(request.POST, request.FILES, instance=operation, prefix='images')
        vehicle_files_formset = VehicleFileFormSet(request.POST, request.FILES, instance=operation, prefix='vehicle_files')
        store_files_formset = StoreFileFormSet(request.POST, request.FILES, instance=operation, prefix='store_files')
        center_files_formset = CenterFileFormSet(request.POST, request.FILES, instance=operation, prefix='center_files')
        
        if (form.is_valid() and image_formset.is_valid() and 
            vehicle_files_formset.is_valid() and store_files_formset.is_valid() and 
            center_files_formset.is_valid()):
            
            operation = form.save(commit=False)
            operation.save()
            form.save_m2m()  # حفظ علاقات ManyToMany للمعدات
            
            # معالجة المعدات اليدوية النصية (إضافة جديدة فقط، لا حذف للقديمة إلا إذا أردت)
            def process_manual_equipment(text_field_name, EquipmentModel, m2m_field):
                text_input = form.cleaned_data.get(text_field_name, '')
                process_equipment(text_input, EquipmentModel, operation, m2m_field)
            
            process_manual_equipment('new_vehicle_equipment_text', VehiclesEquipment, 'vehicle_equipment')
            process_manual_equipment('new_store_equipment_text', StoreEquipment, 'store_equipment')
            process_manual_equipment('new_center_equipment_text', CenterEquipment, 'center_equipment')
            
            # حفظ FormSets (الصور والملفات، مع دعم الحذف)
            image_formset.save()
            vehicle_files_formset.save()
            store_files_formset.save()
            center_files_formset.save()
            
            messages.success(request, "✅ تم تعديل المركز والمعدات بنجاح!")
            return redirect('Operation/operation_detail', pk=operation.pk)
        else:
            messages.error(request, "❌ يوجد خطأ في إدخال البيانات يرجى مراجعة الحقول المميزة بالخطأ.")
    
    else:
        # GET request: تحميل البيانات الموجودة
        form = OperationForm(instance=operation)
        
        # تحميل FormSets مع البيانات الموجودة
        image_formset = OperationImageFormSet(instance=operation, prefix='images')
        vehicle_files_formset = VehicleFileFormSet(instance=operation, prefix='vehicle_files')
        store_files_formset = StoreFileFormSet(instance=operation, prefix='store_files')
        center_files_formset = CenterFileFormSet(instance=operation, prefix='center_files')
    
    # تمرير النماذج إلى القالب
    return render(request, 'Operation/edit_operation.html', {
        'form': form,
        'image_formset': image_formset,
        'vehicle_files_formset': vehicle_files_formset,
        'store_files_formset': store_files_formset,
        'center_files_formset': center_files_formset,
    })
    

from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import (
    Operation, OperationImage,
    VehiclesEquipment, StoreEquipment, CenterEquipment,
    Vehicle,
    Employee, WorkSchedule,

)

from .forms import OperationForm, OperationImageForm, OperationImageFormSet

OperationImageFormSet = inlineformset_factory(
    Operation, OperationImage, form=OperationImageForm, extra=1, can_delete=True
)

from .models import Employee
from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee


def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

   
    if request.method == "POST":

        # إضافة شيفت ليلي
        if "add_overnight" in request.POST:
            start_dt = request.POST.get("overnight_start")
            end_dt = request.POST.get("overnight_end")
            notes = request.POST.get("overnight_notes")

           
            return redirect("Employees/employee_detail", pk=employee.pk)

       

    return render(request, "Employees/employee_detail.html", {
        "employee": employee,
       
    })


from .models import Operation, Employee, WorkSchedule


def employees_by_operation(request):
    op_id = request.GET.get("operation")
    operation = get_object_or_404(Operation, pk=op_id)
    today = timezone.now().date()
    weekday = timezone.now().strftime("%a").lower()

    employees = operation.employees.prefetch_related('schedules').all()
    working_today_count = 0  # عدد المداومين اليوم

    for emp in employees:
        schedule_today = emp.schedules.filter(day=weekday).first()
        if schedule_today:
            if schedule_today.is_off and schedule_today.off_date == today:
                emp.off_today = True
            else:
                emp.off_today = False
                working_today_count += 1
        else:
            emp.off_today = False
            working_today_count += 1

    return render(request, "Employees/employees_by_operation.html", {
        "operation": operation,
        "employees": employees,
        "working_today_count": working_today_count,
        "total_employees": employees.count()
    })
    
from django.contrib.auth.decorators import login_required
from .models import Operation, Employee 


@login_required
def employees_by_governorate(request):
    today = timezone.now().date()
    weekday = timezone.now().strftime("%a").lower()
    user_profile = getattr(request.user, "userprofile", None)

    if not user_profile:
        employees_queryset = Employee.objects.none()
    elif user_profile.role == "super_admin" or request.user.is_superuser:
        employees_queryset = Employee.objects.prefetch_related("schedules", "operation").all()
    elif user_profile.role == "governorate_admin":
        operations = Operation.objects.filter(governorate=user_profile.governorate)
        employees_queryset = Employee.objects.filter(operation__in=operations).prefetch_related("schedules", "operation")
    elif user_profile.role == "center_admin":
        operations = Operation.objects.filter(governorate=user_profile.governorate, center=user_profile.center)
        employees_queryset = Employee.objects.filter(operation__in=operations).prefetch_related("schedules", "operation")
    else:
        employees_queryset = Employee.objects.none()

    total_employees = employees_queryset.count()

    working_employees = []
    for emp in employees_queryset:
        schedule_today = emp.schedules.filter(day=weekday).first()
        if not schedule_today:
            continue

        has_leave = emp.leaves.filter(start_date__lte=today, end_date__gte=today).exists()
        has_departure = emp.departures.filter(date=today).exists()

        if getattr(schedule_today, 'is_off', False) and getattr(schedule_today, 'off_date', None) == today:
            continue

        if not has_leave and not has_departure:
            working_employees.append(emp)

    return render(request, "Employees/employees_by_governorate.html", {
        "employees": working_employees,
        "total_working": len(working_employees),
        "total_employees": total_employees,
    })




from .models import Operation, Employee, WorkSchedule
from .forms import EmployeeForm
from django.db.models import Q


from datetime import timedelta

def working_today_employees(request, operation_id):
    operation = get_object_or_404(Operation, pk=operation_id)
    today = timezone.localdate()
    weekday = today.strftime("%a").lower()

    employees = operation.employees.all()
    result = []

    for emp in employees:

        # 📌 جدول الدوام العادي
        schedule_today = emp.schedules.filter(day=weekday).first()

        # 📌 إجازة
        on_leave = emp.leaves.filter(
            start_date__lte=today,
            end_date__gte=today
        ).exists()

        # 📌 مغادرة
        has_departure = emp.departures.filter(date=today).exists()

        # 🌙 شيفت ليلي يغطي اليوم
        has_overnight_shift = emp.overnight_shifts.filter(
            start_datetime__date__lte=today,
            end_datetime__date__gte=today
        ).exists()



        # 🧠 تحديد الحالة بالأولوية
        if has_departure:
            status = "مغادرة"

        elif on_leave:
            status = "إجازة"

        elif has_overnight_shift:
            status = "مداوم (شيفت ليلي)"

        elif schedule_today and not schedule_today.is_off:
            status = "مداوم"

        else:
            status = "معطل"

        result.append({
            "employee": emp,
            "status": status
        })

    return render(request, "Employees/working_today_employees.html", {
        "operation": operation,
        "working_today": result,
        "working_today_count": sum(
            1 for r in result if "مداوم" in r["status"]
        ),
        "total_employees": employees.count(),
    })

from django.db.models import Sum, F
from .models import Vehicle, Trip
from .forms import TripForm

def trip_list(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    trips = vehicle.trips.order_by("-date")

    # تقرير شهري (تجميع بالكيلومترات)
    today = timezone.now()
    monthly_distance = trips.filter(
        date__year=today.year,
        date__month=today.month
    ).aggregate(
        total=Sum(F("end_odometer") - F("start_odometer"))
    )["total"] or 0

    return render(request, "Trip/trip_list.html", {
        "vehicle": vehicle,
        "trips": trips,
        "monthly_distance": monthly_distance,
    })


def add_trip(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    if request.method == "POST":
        form = TripForm(request.POST, request.FILES)  # مهم جداً إضافة request.FILES
        if form.is_valid():
            trip = form.save(commit=False)
            trip.vehicle = vehicle
            trip.save()
            return redirect("Trip/trip_list", vehicle_id=vehicle.id)
    else:
        form = TripForm(initial={"vehicle": vehicle})
    return render(request, "Trip/add_trip.html", {"form": form, "vehicle": vehicle})

from .models import Vehicle, Trip
from .forms import TripFilterForm


def trip_filter_view(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    trips = []
    total_distance = 0

    if request.method == "POST":
        form = TripFilterForm(request.POST)
        if form.is_valid():  # ✅ بس إذا الفورم صحيح
            filter_type = form.cleaned_data.get("filter_type")

            if filter_type == "monthly":
                month = form.cleaned_data.get("month")
                year = form.cleaned_data.get("year")
                trips = Trip.objects.filter(
                    vehicle=vehicle,
                    date__year=year,
                    date__month=month
                ).order_by("-date")

            elif filter_type == "yearly":
                year = form.cleaned_data.get("year")
                trips = Trip.objects.filter(
                    vehicle=vehicle,
                    date__year=year
                ).order_by("-date")

            elif filter_type == "range":
                start_date = form.cleaned_data.get("start_date")
                end_date = form.cleaned_data.get("end_date")
                trips = Trip.objects.filter(
                    vehicle=vehicle,
                    date__range=[start_date, end_date]
                ).order_by("-date")

            total_distance = sum([t.distance for t in trips])
    else:
        form = TripFilterForm()

    return render(request, "Trip/trip_filter.html", {
        "vehicle": vehicle,
        "trips": trips,
        "total_distance": total_distance,
        "form": form,
    })
    
    
from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from bidi.algorithm import get_display
import arabic_reshaper
import os
from .models import Vehicle, Trip 

def download_trips_pdf(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    filter_type = request.GET.get("filter_type")
    month = request.GET.get("month")
    year = request.GET.get("year")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    trips = Trip.objects.filter(vehicle=vehicle)

    # فلترة حسب النوع
    if filter_type == "monthly" and month and year:
        trips = trips.filter(date__year=year, date__month=month)
    elif filter_type == "yearly" and year:
        trips = trips.filter(date__year=year)
    elif filter_type == "range" and start_date and end_date:
        trips = trips.filter(date__gte=start_date, date__lte=end_date)

    total_distance = sum(trip.distance for trip in trips)
    trips_count = trips.count()  # عدد الرحلات

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    font_path = os.path.join('static', 'fonts', 'Amiri-Regular.ttf')  # ضع المسار الصحيح للخط
    pdfmetrics.registerFont(TTFont("Arabic", font_path))
    pdf.setFont("Arabic", 14)

    def write_arabic(text, x, y):
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        pdf.drawRightString(x, y, bidi_text)

    y = 800
    write_arabic(f"تقرير الرحلات للمركبة: {vehicle.vehicle_number}", 550, y)
    y -= 30
    write_arabic(f"عدد الرحلات: {trips_count} رحلة", 550, y)  # تم إضافة عدد الرحلات
    y -= 30
    write_arabic(f"إجمالي المسافات: {total_distance} كم", 550, y)
    y -= 40

    write_arabic("📋 تفاصيل الرحلات:", 550, y)
    y -= 30
    for trip in trips:
        line = f"{trip.date} - {trip.destination} - {trip.start_odometer} ➜ {trip.end_odometer} = {trip.distance} كم"
        write_arabic(line, 550, y)
        y -= 25
        if y < 100:
            pdf.showPage()
            pdf.setFont("Arabic", 14)
            y = 800

    pdf.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")

from .forms import EmployeeForm
from .models import DAYS_OF_WEEK

from .forms import EmployeeForm, WorkScheduleFormSet
from .models import Employee, WorkSchedule, Operation


DAYS_OF_WEEK = [
    ("sun", "الأحد"),
    ("mon", "الاثنين"),
    ("tue", "الثلاثاء"),
    ("wed", "الأربعاء"),
    ("thu", "الخميس"),
    ("fri", "الجمعة"),
    ("sat", "السبت"),
]

from .models import Employee, WorkSchedule, Certificate, Operation
from .forms import EmployeeForm
from django.shortcuts import render, redirect, get_object_or_404

from .models import Employee, Certificate, Operation
from .forms import EmployeeForm


def add_employee(request):

    initial = {}

    op_id = request.GET.get("operation")

    if op_id:
        initial["operation"] = get_object_or_404(Operation, pk=op_id)

    if request.method == "POST":

        form = EmployeeForm(request.POST, request.FILES)

        if form.is_valid():

            emp = form.save()

            cert_names = request.POST.getlist("certificate_name[]")
            cert_dates = request.POST.getlist("certificate_date[]")
            cert_files = request.FILES.getlist("certificate_file[]")

            for name, date, file in zip(cert_names, cert_dates, cert_files):

                if name.strip():

                    Certificate.objects.create(
                        employee=emp,
                        name=name,
                        date=date if date else None,
                        file=file if file else None,
                    )

            return redirect(f"/employees/?operation={emp.operation.id}")

    else:

        form = EmployeeForm(initial=initial)

    return render(
        request,
        "Employees/add_employee.html",
        {
            "form": form,
        },
    )
import logging
import re
from datetime import date, timedelta

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Vehicle, UserAssignment, Notification, Maintenance, Employee
from .forms import VehicleForm

logger = logging.getLogger(__name__)
def dispatch_notification(user, message_text, channel_layer):
    if not Notification.objects.filter(user=user, message=message_text).exists():
        noti = Notification.objects.create(user=user, message=message_text, read=False)
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"user_{user.id}",
                    {
                        "type": "send_notification",
                        "message": message_text,
                        "id": noti.id
                    }
                )
            except Exception as e:
                logger.error(f"Socket send error for user {user.id}: {e}")

from .models import UserAssignment, Notification, OrganizationUnit, Role
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.db.models import Q
from .models import UserAssignment, Notification
import logging

logger = logging.getLogger(__name__)
from django.db.models import Q
def send_vehicle_notification(vehicle, creator_user):
    channel_layer = get_channel_layer()
    creator_assignment = UserAssignment.objects.filter(user=creator_user, is_active=True).first()
    if not creator_assignment or not creator_assignment.unit or not creator_assignment.unit.linked_governorate:
        return 
    governorate_id = creator_assignment.unit.linked_governorate.id
    target_managers = UserAssignment.objects.filter(
        is_active=True,
        unit__linked_governorate_id=governorate_id,
        unit__name__icontains="النقل والصيانة"
    ).filter(Q(role__name__icontains="مدير"))
    
    msg = f"🚗 تم إضافة مركبة جديدة ({vehicle.vehicle_number}) من قبل {creator_user.username}"
    for manager_assignment in target_managers:
        dispatch_notification(manager_assignment.user, msg, channel_layer)
from datetime import date, timedelta
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Vehicle, UserAssignment  # تأكد من استيراد النماذج الصحيحة هنا
from datetime import date, timedelta
from django.utils import timezone
def check_expiring_vehicles_globally(specific_vehicle=None):
    today = date.today()
    warning_period = today + timedelta(days=14)
    channel_layer = get_channel_layer()
    managers = UserAssignment.objects.filter(is_active=True, unit__name__icontains="النقل والصيانة").filter(role__name__icontains="مدير")
    if specific_vehicle:
        expiring_vehicles = [specific_vehicle]
    else:
        expiring_vehicles = Vehicle.objects.filter(Q(insurance_expiry__lte=warning_period) | Q(license_expiry__lte=warning_period))
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
import re
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Vehicle, UserAssignment, Notification  # تأكد من استيراد النماذج بشكل صحيح


# تأكدي من استيراد الموديلات المطلوبة في أعلى الملف
from .models import Vehicle, UserAssignment, Notification, VehicleStatusNotification
# من المفترض أن تكون دالة التحقق موجودة في utils أو في نفس الملف
logger = logging.getLogger(__name__)

import re
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Vehicle, VehicleApproval, UserAssignment, Notification, VehicleStatusNotification

logger = logging.getLogger(__name__)

import re
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Vehicle, VehicleApproval, UserAssignment, Notification, VehicleStatusNotification

logger = logging.getLogger(__name__)

@login_required
def vehicle_list(request):
    user = request.user
    search_text = request.GET.get("بحث", "").strip()
    
    # 1. تحديد صلاحية إضافة مركبة مبدئياً
    can_add_vehicle = False
    
    # جلب التعيين الوظيفي النشط للمستخدم
    current_assignment = UserAssignment.objects.filter(
        user=user,
        is_active=True
    ).select_related('unit', 'role', 'unit__linked_governorate', 'unit__linked_center').first()

    # 2. التحقق من صلاحية إضافة مركبة (مدير إدارة النقل والصيانة أو الأدمن)
    if user.is_superuser:
        can_add_vehicle = True
    elif current_assignment and current_assignment.unit and current_assignment.role:
        role_name = current_assignment.role.name.strip()
        unit_name = current_assignment.unit.name.strip()
        if "مدير" in role_name and "النقل والصيانة" in unit_name:
            can_add_vehicle = True

    # 3. التحقق من الوصول للصفحة لغير السوبر يوزر
    if not user.is_superuser:
        if not current_assignment or not current_assignment.unit or not current_assignment.role:
            return HttpResponseForbidden("عذراً، لا يوجد تعيين وظيفي نشط لهذا الحساب.")

        clean_unit_name = current_assignment.unit.name.strip()
        clean_role_name = current_assignment.role.name.strip()

        is_allowed = (
            any(r in clean_role_name for r in ["مدير", "نائب", "مسؤول", "موظف"])
            or
            any(u in clean_unit_name for u in ["النقل والصيانة", "الاطفاء والانقاذ", "الإطفاء والإنقاذ", "العمليات"])
        )

        if not is_allowed and not user.has_perm("map.view_vehicle"):
            return HttpResponseForbidden("عذراً، لا تملك الصلاحية للوصول إلى صفحة المركبات.")

    # 4. تنفيذ فحص انتهاء الصلاحية
    try:
        check_expiring_vehicles_globally()
    except Exception as e:
        logger.error(f"Error running global vehicle expiry check: {e}")

    # 5. جلب المركبات حسب المحافظة والمركز المرتبط بالوحدة التنظيمية
    base_queryset = Vehicle.objects.prefetch_related("drivers").select_related("approval", "governorate", "center")

    if user.is_superuser:
        # السوبر يوزر يرى كافة المركبات
        vehicles = base_queryset.all()
    else:
        unit = current_assignment.unit

        # إذا كانت الوحدة تابعة للإدارة العامة (HQ) أو إدارة النقل المركزية، تظهر جميع المركبات
        if unit.unit_type == 'hq' or "النقل والصيانة" in unit.name:
            vehicles = base_queryset.all()
        else:
            filters = Q()

            # أ) التصفية بالمحافظة المرتبطة
            if unit.linked_governorate:
                filters &= Q(governorate=unit.linked_governorate)

            # ب) التصفية بالمركز/المديرية المرتبطة
            if unit.linked_center:
                filters &= Q(center=unit.linked_center)

            # ج) إذا لم تكن المفاتيح الأجنبية ممررة مباشرة، نلجأ للربط الضمني أو الاسم
            if not unit.linked_governorate and not unit.linked_center:
                extracted_name = unit.name.split("-")[-1].strip() if "-" in unit.name else unit.name.strip()
                filters &= (
                    Q(governorate__name__icontains=extracted_name) | 
                    Q(center__name__icontains=extracted_name)
                )

            vehicles = base_queryset.filter(filters)

    # 6. تطبيق البحث
    if search_text:
        search_text = re.sub(r"[^\w\s]", " ", search_text)
        for word in search_text.split():
            vehicles = vehicles.filter(
                Q(vehicle_number__icontains=word) |
                Q(center__name__icontains=word) |
                Q(governorate__name__icontains=word) |
                Q(model__icontains=word)
            )

    # 7. تصنيف المركبات
    categorized = {}
    work_types = {
        "fire": "إطفاء", 
        "rescue": "إنقاذ", 
        "fire_and_rescue": "إطفاء وإنقاذ", 
        "services": "خدمات", 
        "tank": "تنك تزويد"
    }
    for wt, ar in work_types.items():
        categorized[ar] = {
            "داخل": vehicles.filter(work_type=wt, status="in_service"),
            "خارج": vehicles.filter(work_type=wt, status="out_service"),
        }

    # 8. جلب الإشعارات
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    status_notifications = VehicleStatusNotification.objects.filter(
        vehicle__in=vehicles
    ).order_by('-created_at')

    unread_general = notifications.filter(read=False).count()
    unread_status = status_notifications.filter(read=False).count()
    total_unread_count = unread_general + unread_status

    context = {
        "مصنفة": categorized,
        "notifications": notifications,
        "status_notifications": status_notifications,
        "total_unread_count": total_unread_count,
        "نص_البحث": search_text,
        "source": request.GET.get("source"),
        "can_add_vehicle": can_add_vehicle,
    }

    return render(request, "Vehicle/vehicle_list.html", context)

from django.contrib.auth.decorators import login_required
from .decorators import transport_manager_required
from .decorators import vehicle_status_required

from .decorators import transport_manager_required # استورد الديكوريتور الخاص بالوحدة
from django.contrib.auth.decorators import login_required, permission_required
from .models import VehicleStatusNotification # تأكدي من الاستيراد
def notify_status_change(vehicle, sender_user, new_status, notes):
    try:
        from .models import VehicleStatusNotification
        status_text = "خارج الخدمة" if new_status == 'out_service' else "داخل الخدمة"
        msg = f"قام {sender_user.get_full_name() or sender_user.username} بتغيير حالة المركبة {vehicle.vehicle_number} إلى ({status_text})"
        
        # إنشاء الإشعار للمستخدم القائم بالتغيير أو إرساله للمستهدفين/المدراء
        VehicleStatusNotification.objects.create(
            user=sender_user, 
            sender=sender_user,
            vehicle=vehicle, 
            message=msg
        )
    except Exception as e:
        print(f"--- خطأ أثناء التخزين: {e} ---")
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import VehicleStatusNotification

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import VehicleStatusNotification

@login_required
@require_POST
def mark_status_read(request, id):
    # نتحقق من الإشعار بالإيد دون تقييد صارم بالـ user إن كان الإشعار موجه للعموم، 
    # أو نستخدم filter و first للتأكد من عدم رفع 404
    noti = VehicleStatusNotification.objects.filter(id=id).first()
    
    if noti:
        noti.read = True
        noti.save()
        return JsonResponse({"status": "success"})
    
    return JsonResponse({"status": "error", "message": "Notification not found"}, status=404)
from .decorators import vehicle_status_required




@login_required
@permission_required("map.add_vehicle", raise_exception=True)
def add_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "تم إضافة المركبة بنجاح")
            return redirect('Vehicle/vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'Vehicle/add_vehicle.html', {'form': form})



from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseNotAllowed

from .models import VehicleStatusHistory
from django.contrib.auth.decorators import login_required
from .decorators import vehicle_status_required


from django.contrib import messages # تأكدي من استيراد messages
from django.contrib.auth import get_user_model

@login_required
@vehicle_status_required
def toggle_vehicle_status(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    User = get_user_model()

    if request.method == "POST":
        new_notes = request.POST.get("status_notes", "")
        new_status = "out_service" if vehicle.status == "in_service" else "in_service"
        status_text = "داخل الخدمة" if new_status == "in_service" else "خارج الخدمة"
        
        # 1. تحديث وحفظ حالة المركبة
        vehicle.status = new_status
        vehicle.status_notes = new_notes
        vehicle.save()

        # 2. إضافة سجل في التاريخ
        VehicleStatusHistory.objects.create(
            vehicle=vehicle,
            status=new_status,
            notes=new_notes
        )
        
        # 3. إرسال إشعارات لمجموعة مستخدمين (مثلاً المدراء - حسب صلاحياتك)
        # يمكنك تعديل الفلتر لاختيار من يستلم الإشعار
        target_users = User.objects.filter(is_staff=True) 

        msg = f"تم تغيير حالة المركبة {vehicle.vehicle_number} إلى {status_text} بواسطة {request.user.username}."
        
        for target_user in target_users:
            VehicleStatusNotification.objects.create(
                user=target_user,      # المستلم
                sender=request.user,   # الشخص الذي قام بالتغيير (الحقل الجديد)
                vehicle=vehicle,
                message=msg,
                read=False
            )
        
        messages.success(request, f"تم تحديث حالة المركبة إلى {status_text}")
        return redirect("vehicle_status", vehicle_id=vehicle.id)

    return render(request, "Vehicle/vehicle_status.html", {"vehicle": vehicle})
def vehicle_status(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    return render(request, "Vehicle/vehicle_status.html", {"vehicle": vehicle})


from .forms import FuelQuotaForm

def fuel_quota_add(request):
    if request.method == "POST":
        form = FuelQuotaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("Fuel/fuel_quota_list")
    else:
        form = FuelQuotaForm()
    return render(request, "Fuel/fuel_quota_add.html", {"form": form})


from .models import FuelQuota, Vehicle  # تأكد أن عندك موديل Vehicle

def fuel_quota_list_by_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    quotas = FuelQuota.objects.filter(vehicle=vehicle).order_by("-month")
    return render(request, "Fuel/fuel_quota_list.html", {"quotas": quotas})

from .models import FuelQuota
from .forms import FuelFillingForm


def add_fuel_filling(request, quota_id):
    quota = get_object_or_404(FuelQuota, id=quota_id)

    if request.method == "POST":
        # 🌟 التعديل هنا: يجب تمرير request.FILES لاستقبال ملفات الصور
        form = FuelFillingForm(request.POST, request.FILES)
        
        if form.is_valid():
            filling = form.save(commit=False)
            filling.quota = quota
            filling.save()
            # إذا كان النموذج يحتوي على ImageField، فإن save() بعد commit=False ستقوم بحفظ بيانات الملف إذا تم تمرير request.FILES.
            return redirect("Fuel/fuel_quota_detail", quota_id=quota.id)
    else:
        form = FuelFillingForm()

    return render(request, "Fuel/fuel_filling_form.html", {"form": form, "quota": quota})

from .models import FuelQuota

# قائمة المخصصات
def fuel_quota_list(request):
    quotas = FuelQuota.objects.select_related("vehicle").all().order_by("-month")
    return render(request, "Fuel/fuel_quota_list.html", {"quotas": quotas})

from .models import FuelQuota
from decimal import Decimal 


def fuel_quota_detail(request, quota_id):
    quota = get_object_or_404(FuelQuota, id=quota_id)
    
    is_exhausted = (quota.remaining_quantity <= Decimal('0.00')) and \
                   (quota.remaining_amount <= Decimal('0.00'))

    fillings = quota.fillings.all().order_by('date')
    
    remaining_qty_tracker = quota.allocated_quantity
    remaining_amt_tracker = quota.allocated_amount
    
    processed_fillings = []
    
    for filling in fillings:
        was_remaining_qty_positive = remaining_qty_tracker > Decimal('0.00')
        was_remaining_amt_positive = remaining_amt_tracker > Decimal('0.00')

        remaining_qty_tracker -= filling.quantity
        remaining_amt_tracker -= filling.amount
        
        if (remaining_qty_tracker < Decimal('0.00') or remaining_amt_tracker < Decimal('0.00')):
            filling.is_over_quota = True
        else:
            filling.is_over_quota = False
            
        processed_fillings.append(filling)

    context = {
        "quota": quota,
        "is_exhausted": is_exhausted,
        "fillings": processed_fillings, # 👈 تمرير السجلات المعالجة
    }
    
    return render(request, "Fuel/fuel_quota_detail.html", context)

# views.py

from .models import FuelQuota
from decimal import Decimal
import os
from io import BytesIO
from django.http import HttpResponse
from django.conf import settings

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# استيرادات لمعالجة النص العربي
from arabic_reshaper import ArabicReshaper
from bidi.algorithm import get_display as reshape_arabic_text

def download_fuel_quota_pdf(request, quota_id):
    # 1. جلب المخصص: استخدام get_object_or_404 يضمن وجود الكائن أو إظهار خطأ 404
    quota = get_object_or_404(FuelQuota, id=quota_id)

    buffer = BytesIO()
    
    # 2. تسجيل الخط العربي
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Amiri-Regular.ttf')
    
    # تحقق وتسجيل الخط (لتجنب الخطأ في كل مرة)
    if "Arabic" not in pdfmetrics.getRegisteredFontNames():
        try:
            pdfmetrics.registerFont(TTFont("Arabic", font_path))
        except FileNotFoundError:
            return HttpResponse("خط 'Amiri-Regular.ttf' غير موجود. يرجى التأكد من مسار الخطوط.", status=500)

    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Arabic", 16)
    y = 800

    # 3. العنوان الرئيسي
    title = f"تقرير مخصص الوقود للمركبة: {quota.vehicle.vehicle_number}"
    p.drawRightString(550, y, reshape_arabic_text(title))
    y -= 30
    p.setFont("Arabic", 12)
    p.line(50, y, 550, y) # خط فاصل
    y -= 30

    # 4. بيانات المخصص والاستهلاك
    data = [
        ("المركبة", quota.vehicle.vehicle_number),
        ("الشهر", quota.month.strftime('%B %Y')),
        ("الكمية المخصصة", f"{quota.allocated_quantity} لتر"),
        ("المبلغ المخصص", f"{quota.allocated_amount} شيكل"),
        ("", ""),
        ("الكمية المستهلكة الكلية", f"{quota.used_quantity} لتر"),
        ("المبلغ المستهلك الكلي", f"{quota.used_amount} شيكل"),
        ("الكمية المتبقية", f"{quota.remaining_quantity} لتر"),
        ("المبلغ المتبقي", f"{quota.remaining_amount} شيكل"),
    ]

    for label, value in data:
        if y < 100:
            p.showPage()
            p.setFont("Arabic", 12)
            y = 800
        if label:
            line = reshape_arabic_text(f"🔹 {label}: {value}")
            p.drawRightString(550, y, line)
            y -= 25
        else: # سطر فارغ للفصل
            y -= 10
        
    y -= 20
    
    # 5. قسم الصرف الزائد (المديونية) والتنبيه
    extra_qty = quota.extra_used_quantity
    extra_amt = quota.extra_used_amount
    
    if extra_qty > Decimal('0.00') or extra_amt > Decimal('0.00'):
        p.setFont("Arabic", 14)
        debt_title = "⚠️ صرف وقود إضافي (مديونية) ⚠️"
        p.drawRightString(550, y, reshape_arabic_text(debt_title))
        y -= 25
        p.setFont("Arabic", 12)
        
        p.drawRightString(550, y, reshape_arabic_text(f"💰 الكمية المضافة (دين): {extra_qty} لتر"))
        y -= 20
        p.drawRightString(550, y, reshape_arabic_text(f"💵 المبلغ المضاف (دين): {extra_amt} شيكل"))
        y -= 20
        
        # إضافة الملاحظة المطلوبة بلون أحمر
        note = "ملاحظة: المركبة استهلكت كمية تفوق المخصص المحدد لها بهذا الشهر."
        p.setFillColorRGB(0.8, 0.2, 0.2) 
        p.drawRightString(550, y, reshape_arabic_text(note))
        p.setFillColorRGB(0, 0, 0) # العودة للون الأسود
        y -= 30
    
    # 6. جدول سجلات التعبئة
    p.setFont("Arabic", 14)
    p.drawRightString(550, y, reshape_arabic_text("📝 سجلات التعبئة"))
    y -= 20
    p.line(50, y, 550, y) 
    y -= 30
    
    fillings = quota.fillings.all().order_by('date')
    remaining_qty_tracker = quota.allocated_quantity
    remaining_amt_tracker = quota.allocated_amount
    
    # رأس الجدول
    p.setFont("Arabic", 10)
    col_x = [50, 130, 240, 330, 420, 550] # إحداثيات الأعمدة
    
    header = ["التجاوز", "المبلغ (شيكل)", "الكمية (لتر)", "السائق", "التاريخ"]
    for i, h in enumerate(header):
        p.drawString(col_x[i+1], y, reshape_arabic_text(h))
    y -= 20

    # بيانات الصفوف
    p.setFont("Arabic", 10)
    for filling in fillings:
        if y < 80: # صفحة جديدة عند نفاذ المساحة
            p.showPage()
            p.setFont("Arabic", 10)
            y = 800
            for i, h in enumerate(header):
                 p.drawString(col_x[i+1], y, reshape_arabic_text(h))
            y -= 20
            
        # منطق تحديد التجاوز
        is_over_quota = (remaining_qty_tracker < Decimal('0.00') or remaining_amt_tracker < Decimal('0.00'))
        
        # تحديث الرصيد للمتابعة
        remaining_qty_tracker -= filling.quantity
        remaining_amt_tracker -= filling.amount
        
        # ❌ عدم تطبيق التلوين هنا (حسب طلبك)
        p.setFillColorRGB(0, 0, 0)
        
        # محتوى الصف
        p.drawString(col_x[5], y, reshape_arabic_text(filling.date.strftime('%d-%m-%Y')))
        driver_name = filling.driver.name if filling.driver else "غير محدد"
        p.drawString(col_x[4], y, reshape_arabic_text(driver_name))
        p.drawString(col_x[3], y, str(filling.quantity))
        p.drawString(col_x[2], y, str(filling.amount))
        p.drawString(col_x[1], y, reshape_arabic_text("نعم" if is_over_quota else "لا"))
        
        y -= 20

    # 7. الحفظ والإرسال
    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"fuel_quota_report_{quota.month.strftime('%Y%m')}_{quota.vehicle.vehicle_number}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

from .forms import VehicleForm, VehicleImageForm
from .models import VehicleImage
from .models import Vehicle

def vehicle_drivers(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    # نفترض أن هناك علاقة many-to-many أو ForeignKey بين Vehicle و Driver
    drivers = vehicle.drivers.all()  # افترض أن Vehicle لديه related_name='drivers'
    return render(request, 'Driver/vehicle_drivers.html', {
        'vehicle': vehicle,
        'drivers': drivers
    })


from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .models import Vehicle, VehicleApproval, UserAssignment

@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    
    # جلب أو إنشاء سجل الاعتماد لهذه المركبة تلقائياً
    approval, _ = VehicleApproval.objects.get_or_create(vehicle=vehicle)

    # جلب التعيين الوظيفي النشط للمستخدم
    current_assignment = UserAssignment.objects.filter(
        user=request.user, 
        is_active=True
    ).select_related('unit', 'role').first()
    
    can_approve_transport = False
    can_approve_gov = False

    if request.user.is_superuser:
        can_approve_transport = True
        can_approve_gov = True
    elif current_assignment and current_assignment.role and current_assignment.unit:
        role_name = current_assignment.role.name.strip()
        unit_name = current_assignment.unit.name.strip()

        # 1. شرط اعتماد مدير النقل والصيانة: دور "مدير إدارة" ووحدة "إدارة النقل والصيانة"
        is_transport_role = "مدير" in role_name
        is_transport_unit = "النقل والصيانة" in unit_name
        
        if is_transport_role and is_transport_unit:
            can_approve_transport = True
            
        # 2. شرط اعتماد مدير المحافظة: دور "مدير المحافظة" أو "مدير مديرية"
        if "مدير المحافظة" in role_name or "مدير مديرية" in role_name:
            can_approve_gov = True

    context = {
        'vehicle': vehicle,
        'approval': approval,
        'can_approve_transport': can_approve_transport,
        'can_approve_gov': can_approve_gov,
    }
    return render(request, 'Vehicle/vehicle_detail.html', context)


@login_required
def approve_vehicle(request, pk, approval_type):
    """
    دالة تنفيذ عملية الاعتماد مع التحقق الآمن من الصلاحيات خلف الكواليس
    """
    vehicle = get_object_or_404(Vehicle, pk=pk)
    approval, _ = VehicleApproval.objects.get_or_create(vehicle=vehicle)

    current_assignment = UserAssignment.objects.filter(
        user=request.user, 
        is_active=True
    ).select_related('unit', 'role').first()

    # التحقق من الصلاحيات الأمنية لمنع التلاعب عن طريق الـ URL مباشرة
    can_approve = False
    if request.user.is_superuser:
        can_approve = True
    elif current_assignment and current_assignment.role and current_assignment.unit:
        role_name = current_assignment.role.name.strip()
        unit_name = current_assignment.unit.name.strip()

        if approval_type == 'transport' and "مدير" in role_name and "النقل والصيانة" in unit_name:
            can_approve = True
        elif approval_type == 'governorate' and ("مدير المحافظة" in role_name or "مدير مديرية" in role_name):
            can_approve = True

    if not can_approve:
        messages.error(request, "عذراً، لا تملك الصلاحية اللازمة لتنفيذ هذا الاعتماد.")
        return redirect('Vehicle/vehicle_detail', pk=pk)

    # تنفيذ الاعتماد حسب النوع
    if approval_type == 'transport':
        approval.approved_by_transport_manager = True
        approval.transport_manager_user = request.user
        approval.transport_approval_date = timezone.now()
        messages.success(request, "تم اعتماد المركبة بنجاح من قبل مدير النقل والصيانة.")
    
    elif approval_type == 'governorate':
        approval.approved_by_governorate_manager = True
        approval.governorate_manager_user = request.user
        approval.governorate_approval_date = timezone.now()
        messages.success(request, "تم اعتماد المركبة بنجاح من قبل مدير المحافظة.")

    approval.save()
    return redirect('Vehicle/vehicle_detail', pk=pk)
from django.shortcuts import render, get_object_or_404, redirect
from .models import Vehicle
from .forms import VehicleForm # سنستخدم نفس الفورم أو فورم مخصص
from .forms import VehicleDriversForm # استيراد الفورم الجديد

def edit_vehicle_drivers(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    
    if request.method == "POST":
        # استخدم الفورم الجديد المخصص للسائقين فقط
        form = VehicleDriversForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            return redirect('Vehicle/vehicle_detail', pk=vehicle.pk)
    else:
        form = VehicleDriversForm(instance=vehicle)
        
    return render(request, 'Vehicle/edit_drivers.html', {'form': form, 'vehicle': vehicle})

from django.http import JsonResponse
from .models import Center

def get_centers_by_governorate(request):
    governorate_id = request.GET.get('governorate_id')
    centers = Center.objects.filter(governorate_id=governorate_id).values('id', 'name')
    return JsonResponse(list(centers), safe=False)








from .models import Driver
from .forms import DriverForm

def driver_list(request):
    drivers = Driver.objects.all()
    return render(request, "Driver/driver_list.html", {"drivers": drivers})


def add_driver(request):
    if request.method == "POST":
        form = DriverForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("Driver/driver_list")
    else:
        form = DriverForm()
    return render(request, "Driver/add_driver.html", {"form": form})


from .models import Driver

def driver_detail(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    return render(request, "Driver/driver_detail.html", {"driver": driver})



from django.contrib.auth.decorators import login_required, user_passes_test



@login_required
@user_passes_test(lambda u: u.is_superuser)
def superuser_all_phones_view(request):
    # من جدول السلامة العامة
    public_safety_entries = PublicSafety.objects.filter(whatsapp__isnull=False).exclude(whatsapp='').values('whatsapp', 'owner_name')
    public_safety_phones = [
        {
            'number': entry['whatsapp'],
            'owner': entry['owner_name'] or 'غير معروف',
            'source': 'السلامة العامة'
        }
        for entry in public_safety_entries
    ]

    # من جدول المباني
    building_entries = BuildingInfo.objects.filter(phone_number__isnull=False).exclude(phone_number='').values('phone_number', 'owner_name')
    building_phones = [
        {
            'number': entry['phone_number'],
            'owner': entry['owner_name'],
            'source': 'معلومات المبنى'
        }
        for entry in building_entries
    ]

    # دمج وحذف التكرارات
    phone_dict = {}
    for entry in public_safety_phones + building_phones:
        phone_dict[entry['number']] = entry

    all_phones = sorted(phone_dict.values(), key=lambda x: x['number'])

    if request.method == "POST":
        selected_numbers = request.POST.getlist("selected_numbers")
        message = request.POST.get("message")

        # للعرض فقط (اختبار) – تقدر بعدين تربطه مع API
        print("الأرقام المختارة:", selected_numbers)
        print("الرسالة:", message)

        return render(request, 'superuser_all_phones.html', {
            'all_phones': all_phones,
            'success': True
        })

    return render(request, 'superuser_all_phones.html', {
        'all_phones': all_phones
    })







from .models import PublicSafety
from django.contrib.auth.decorators import login_required

from .models import PublicSafety, ReceiptImage, RequiredDocumentsImage


@login_required
def history_publicSafety_details(request):
    records = PublicSafety.objects.filter(user=request.user)
    return render(request, 'PublicSafety/history_publicSafety_details.html', {'records': records})

@login_required
def history_publicSafety_detail_user(request, record_id):
    record = get_object_or_404(PublicSafety, id=record_id, user=request.user)

    if request.method == 'POST':
        # حفظ صور الوصل
        receipt_files = request.FILES.getlist('receipt_images')
        for img in receipt_files:
            ReceiptImage.objects.create(public_safety=record, image=img)

        # حفظ صور الأوراق
        doc_files = request.FILES.getlist('doc_images')
        for img in doc_files:
            RequiredDocumentsImage.objects.create(public_safety=record, image=img)

        return redirect('PublicSafety/history_publicSafety_detail_user', record_id=record.id)

    return render(request, 'PublicSafety/history_publicSafety_detail_user.html', {'record': record})



import os
from io import BytesIO
from datetime import timedelta

import arabic_reshaper
import folium
import requests
from bidi.algorithm import get_display

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .forms import PublicSafetyForm
from .models import PublicSafety, PublicSafetyMedia
@login_required
def download_public_safety_pdf(request, safety_id):
    try:
        if request.user.is_superuser:
            # السوبر يوزر يشاهد كل السجلات
            safety = PublicSafety.objects.get(id=safety_id)
        else:
            # باقي المستخدمين يرون فقط سجلاتهم
            safety = PublicSafety.objects.get(id=safety_id, user=request.user)
    except PublicSafety.DoesNotExist:
        return HttpResponse("🚫 السجل غير موجود أو ليس لديك صلاحية.", status=404)

    buffer = BytesIO()
    
    # تسجيل الخط العربي (تأكد من وجود الخط في المسار)
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Amiri-Regular.ttf')
    pdfmetrics.registerFont(TTFont("Arabic", font_path))

    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Arabic", 14)
    y = 800

    p.drawRightString(550, y, reshape_arabic_text(f"تقرير السلامة العامة للمستخدم: {request.user.username}"))
    y -= 40

    fields = [
        ("اسم صاحب المحل", safety.owner_name),
        ("رقم الهوية", safety.national_id),
        ("رقم الواتساب", safety.whatsapp),
        ("اسم الحرفة", safety.business_name),
        ("المدينة", safety.city),
        ("العنوان من الخريطة", safety.map_address),
        ("العنوان التفصيلي", safety.manual_address),
        ("المساحة", safety.area),
        ("رقم الوصل", safety.receipt_number),
        ("الإجراءات المطلوبة", safety.required_actions),
        ("الإجراءات المنفذة", safety.actions_done),
        ("المبلغ", safety.amount),
        ("تاريخ الكشف", safety.start_date),
        ("تاريخ الانتهاء", safety.end_date),
        ("إحداثيات العرض", safety.latitude),
        ("إحداثيات الطول", safety.longitude),
    ]

    for label, value in fields:
        if y < 100:
            p.showPage()
            p.setFont("Arabic", 14)
            y = 800
        display_value = value if value not in [None, ''] else "لم يحدد"
        line = reshape_arabic_text(f"{label}: {display_value}")
        p.drawRightString(550, y, line)
        y -= 30

    p.showPage()
    p.save()
    buffer.seek(0)

    return HttpResponse(buffer, content_type='application/pdf')


from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from datetime import timedelta
import requests
import folium

from .forms import PublicSafetyForm
from .models import PublicSafety, PublicSafetyMedia


@login_required
def publicSafety_user_view(request):
    user = request.user

    # ✅ صلاحيات الوصول: جميع الأدوار (بما فيها user) يمكنها الإدخال
    allowed_roles = ["super_admin", "governorate_admin", "center_admin", "user"]
    if user.role not in allowed_roles:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("❌ ليس لديك صلاحية للوصول إلى صفحة السلامة العامة")

    lat = float(request.GET.get('lat', 0.0))
    lng = float(request.GET.get('lng', 0.0))
    color = request.GET.get('color', 'blue')
    saved_safety_id = None

    # 🔹 جلب العنوان من OpenStreetMap
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"format": "json", "lat": lat, "lon": lng, "accept-language": "ar"},
            headers={"User-Agent": "DjangoApp/1.0"}
        )
        data = response.json()
        address = data.get("display_name", "بدون عنوان")
    except Exception:
        address = "خطأ في جلب العنوان"

    # 🔹 معالجة الفورم
    if request.method == 'POST':
        form = PublicSafetyForm(request.POST, request.FILES)
        images = request.FILES.getlist('images')
        videos = request.FILES.getlist('videos')

        if form.is_valid():
            public_safety = form.save(commit=False)
            public_safety.user = user
            public_safety.latitude = lat
            public_safety.longitude = lng
            public_safety.map_address = address
            public_safety.start_date = timezone.now().date()
            public_safety.end_date = public_safety.start_date + timedelta(days=14)

            # 🆕 ربط المحافظة والمركز حسب المستخدم (إن وُجدت)
            if user.governorate:
                public_safety.governorate = user.governorate
            if user.center:
                public_safety.center = user.center

            public_safety.save()

            # حفظ الصور والفيديوهات
            for img in images:
                PublicSafetyMedia.objects.create(public_safety=public_safety, image=img)
            for vid in videos:
                PublicSafetyMedia.objects.create(public_safety=public_safety, video=vid)

            messages.success(
                request,
                f"✅ تم حفظ المعلومات بنجاح! تاريخ الانتهاء هو {public_safety.end_date}."
            )
            saved_safety_id = public_safety.id
            form = PublicSafetyForm()  # إعادة تهيئة الفورم بعد الحفظ

    else:
        form = PublicSafetyForm()

    # 🔹 إنشاء الخريطة
    m = folium.Map(location=[lat, lng], zoom_start=16)
    folium.Marker([lat, lng], tooltip="موقعك الحالي", icon=folium.Icon(color=color)).add_to(m)
    map_html = m._repr_html_()

    return render(request, 'PublicSafety/publicSafety_user.html', {
        'form': form,
        'm': map_html,
        'address': address,
        'saved_safety_id': saved_safety_id,
    })
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.serializers.json import DjangoJSONEncoder
from datetime import date
from urllib.parse import quote_plus
import json
import re
import folium
from .models import PublicSafety


@login_required
def publicSafety_admin(request):
    user = request.user

    # ✅ منطق الصلاحيات (المستخدم العادي لا يرى هذه الصفحة)
    if user.role == "super_admin" or user.is_superuser:
        public_safety_records = PublicSafety.objects.all()
    elif user.role == "governorate_admin":
        public_safety_records = PublicSafety.objects.filter(governorate=user.governorate)
    elif user.role == "center_admin":
        public_safety_records = PublicSafety.objects.filter(center=user.center)
    else:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("❌ ليس لديك صلاحية رؤية هذه الصفحة")

    public_safety_records = public_safety_records.select_related('user').order_by('-start_date')

    # بقية الكود كما هو (إظهار النقاط على الخريطة)
    today = date.today()
    first_with_coords = next((r for r in public_safety_records if r.latitude and r.longitude), None)
    if first_with_coords:
        center_lat = first_with_coords.latitude
        center_lng = first_with_coords.longitude
    else:
        center_lat = 31.95
        center_lng = 35.91

    m = folium.Map(location=[center_lat, center_lng], zoom_start=13)

    for record in public_safety_records:
        if record.latitude and record.longitude:
            popup_html = f'''
                <b>{record.owner_name}</b><br>
                {record.business_name}<br>
                <a href="/publicSafety/details/{record.id}/" class="btn btn-sm btn-dark mt-2">رؤية التفاصيل</a>
            '''
            folium.Marker(
                location=[record.latitude, record.longitude],
                tooltip=f"{record.owner_name} - {record.business_name}",
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.Icon(color='blue')
            ).add_to(m)

    map_html = m._repr_html_()

    return render(request, 'PublicSafety/publicSafety_admin.html', {
        'public_safety_records': public_safety_records,
        'map_html': map_html,
    })




from django.contrib.auth.decorators import login_required
from .models import PublicSafety, PublicSafetyMedia, ReceiptImage, RequiredDocumentsImage
import folium
@login_required
def publicSafety_detail(request, safety_id):
    user = request.user

    # ✅ السماح فقط للأدوار التالية:
    allowed_roles = ['super_admin', 'governorate_admin', 'center_admin', ]

    # إذا لم يكن لديه دور مسموح
    if user.role not in allowed_roles:
        return render(request, '403.html', status=403)  # صفحة مخصصة للرفض (يمكنك إنشاؤها)

    record = get_object_or_404(PublicSafety, id=safety_id)
    media = PublicSafetyMedia.objects.filter(public_safety=record)
    receipts = ReceiptImage.objects.filter(public_safety=record)
    required_docs = RequiredDocumentsImage.objects.filter(public_safety=record)

    if request.method == 'POST':
        # ✅ فقط المشرفين يمكنهم تعديل حالة الجاهزية
        if user.role in ['super_admin', 'governorate_admin', 'center_admin']:
            record.is_ready = 'is_ready' in request.POST
            record.save()
        return redirect('PublicSafety/history_publicSafety_detail_userss', safety_id=safety_id)

    # ✅ عرض الخريطة إذا كانت هناك إحداثيات
    if record.latitude and record.longitude:
        m = folium.Map(location=[record.latitude, record.longitude], zoom_start=16)
        folium.Marker(
            [record.latitude, record.longitude],
            tooltip=record.owner_name,
            icon=folium.Icon(color='blue')
        ).add_to(m)
        map_html = m._repr_html_()
    else:
        map_html = "<p>❌ لا توجد إحداثيات لعرض الخريطة.</p>"

    return render(request, 'PublicSafety/publicSafety_detail.html', {
        'record': record,
        'media': media,
        'map_html': map_html,
        'receipts': receipts,
        'required_docs': required_docs,
    })


from .models import LocationLog
import folium


from django.shortcuts import render
from .models import Announcement, EmergencyTicker

def services_page_view(request):

    # التنبيهات الموجودة في EmergencyTicker والمفعلة فقط
    tickers = EmergencyTicker.objects.filter(
        is_active=True
    ).order_by("-created_at")

    # آخر 6 إعلانات عادية
    announcements = Announcement.objects.all().order_by("-created_at")[:6]

    context = {
        "tickers": tickers,
        "announcements": announcements,
    }

    return render(request, "main.html", context)


from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import views as auth_views

# -----------------------------
# استيرادات Forms و Models
# -----------------------------
from .forms import BuildingForm, BuildingInfoForm
from .models import LocationLog, BuildingInfo, BuildingMedia
import folium
import requests


@login_required
def catastrophes_user_view(request):
    lat = float(request.GET.get('lat', 0.0))
    lng = float(request.GET.get('lng', 0.0))
    color = request.GET.get('color', 'blue')

    address = "بدون عنوان"
    disaster_governorate = "غير محددة"

    # 🧩 محاولة جلب العنوان من OpenStreetMap (Nominatim)
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "format": "json",
                "lat": lat,
                "lon": lng,
                "accept-language": "ar"
            },
            headers={"User-Agent": "DjangoApp/1.0"}
        )
        data = response.json()
        address = data.get("display_name", "بدون عنوان")

        # ✅ استخراج اسم المحافظة من نص العنوان بطريقة ذكية
        if "display_name" in data:
            display_name = data["display_name"]
            parts = [p.strip() for p in display_name.split(",")]

            # المحاولة الأولى: نأخذ العنصر الثاني (عادة هو اسم المحافظة)
            if len(parts) >= 2:
                if not any(x in parts[1] for x in ["منطقة", "حي", "شارع", "مخيم"]):
                    disaster_governorate = parts[1]
                elif len(parts) >= 3:
                    disaster_governorate = parts[2]

            # تنظيف المحافظة من أي كلمات إضافية
            disaster_governorate = disaster_governorate.replace("محافظة", "").strip()

    except Exception as e:
        print("❌ خطأ في جلب العنوان:", e)
        address = "خطأ في جلب العنوان"

    # 🧾 معالجة حفظ البيانات
    if request.method == 'POST':
        form = BuildingInfoForm(request.POST, request.FILES)
        if form.is_valid():
            building = form.save(commit=False)
            building.user = request.user
            building.latitude = lat
            building.longitude = lng
            building.address = address
            building.status = "لم يتم التقييم"
            building.disaster_governorate = disaster_governorate  # ✅ تعبئة المحافظة التلقائية

            # تعبئة المحافظة والمركز من حساب المستخدم إن وُجدت
            if hasattr(request.user, 'governorate') and request.user.governorate:
                building.governorate = request.user.governorate
            if hasattr(request.user, 'center') and request.user.center:
                building.center = request.user.center

            building.save()

            # ✅ حفظ الصور والفيديوهات
            for img in request.FILES.getlist('images'):
                BuildingMedia.objects.create(building=building, image=img)
            for vid in request.FILES.getlist('videos'):
                BuildingMedia.objects.create(building=building, video=vid)

            messages.success(request, "✅ تم حفظ المعلومات بنجاح!")
            return redirect('Catastrophe/catastrophes_user')
        else:
            print("❌ أخطاء الفورم:", form.errors)
            messages.error(request, "حدث خطأ أثناء الحفظ، تأكد من تعبئة كل الحقول بشكل صحيح.")
    else:
        form = BuildingInfoForm()

    # حذف حقل التقييم من الفورم إن وجد
    if 'evaluation' in form.fields:
        form.fields.pop('evaluation')

    # إنشاء الخريطة
    m = folium.Map(location=[lat, lng], zoom_start=16)
    folium.Marker([lat, lng], tooltip="موقع الكارثة", icon=folium.Icon(color=color)).add_to(m)

    # تمرير المتغيرات للقالب
    return render(request, 'Catastrophe/catastrophes_user.html', {
        'form': form,
        'address': address,
        'disaster_governorate': disaster_governorate,
        'm': m._repr_html_(),
    })

from django.contrib.auth.decorators import user_passes_test
from .models import BuildingInfo
import folium
from django.views.decorators.cache import never_cache
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.db.models import Q

@login_required
@never_cache
def catastrophes_admin(request):
    user = request.user

    # تصفية حسب الدور
    if user.role == "super_admin":
        buildings = BuildingInfo.objects.all()
    elif user.role == "governorate_admin":
        buildings = BuildingInfo.objects.filter(governorate=user.governorate)
    elif user.role == "center_admin":
        buildings = BuildingInfo.objects.filter(center=user.center)
    else:
        # المستخدم العادي لا يملك صلاحية المشاهدة
        messages.warning(request, "❌ ليس لديك صلاحية الوصول لهذه الصفحة.")
        return redirect('Catastrophe/catastrophes_user')

    un_evaluated_buildings = buildings.filter(
        Q(evaluation__isnull=True) | Q(evaluation='')
    ).select_related('user').order_by('-id')

    building_data = [
         {
        'id': b.id,
        'lat': b.latitude,
        'lng': b.longitude,
        'evaluation': b.evaluation,
        'owner': b.owner_name,
        'name': b.building_name,
        'governorate': b.governorate.name if b.governorate else "غير محددة",
        'center': b.center.name if b.center else "غير محدد",
        'disaster_governorate': b.disaster_governorate or "غير محددة",
    }
        for b in buildings
    ]

    return render(request, 'Catastrophe/catastrophes_admin.html', {
        'un_evaluated_buildings': un_evaluated_buildings,
        'buildings': buildings,
        'building_data': json.dumps(building_data, cls=DjangoJSONEncoder),
    })

from .models import BuildingInfo
from .models import BuildingInfo, BuildingMedia

@login_required
def catastrophe_detail(request, building_id):
    building = get_object_or_404(BuildingInfo, id=building_id)

    user = request.user
    # تحقق حسب الدور
    if user.role == "super_admin":
        pass  # يرى كل شيء
    elif user.role == "governorate_admin" and building.governorate != user.governorate:
        return redirect('catastrophes')
    elif user.role == "center_admin" and building.center != user.center:
        return redirect('catastrophes')
    elif user.role == "user" and building.user != user:
        return redirect('catastrophes')
    
    if request.method == 'POST':
        evaluation = request.POST.get('evaluation')
        status = request.POST.get('status')
        building.evaluation = evaluation
        building.status = status
        building.evaluated = True
        building.save()
        return redirect('Catastrophe/catastrophes_admin')

    media_files = building.media.all()

    return render(request, 'Catastrophe/catastrophe_detail.html', {
        'building': building,
        'media_files': media_files,
    })

from django.contrib.auth.decorators import login_required
from .models import BuildingInfo
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
import json

@login_required
def history_catastrophe_details(request):
    user = request.user

    # تصفية المباني حسب دور المستخدم
    if user.role == "super_admin":
        buildings_qs = BuildingInfo.objects.all().prefetch_related('media')
    elif user.role == "governorate_admin":
        buildings_qs = BuildingInfo.objects.filter(governorate=user.governorate).prefetch_related('media')
    elif user.role == "center_admin":
        buildings_qs = BuildingInfo.objects.filter(center=user.center).prefetch_related('media')
    else:  # user عادي
        buildings_qs = BuildingInfo.objects.filter(user=user).prefetch_related('media')

    # تجهيز JSON للخرائط
    buildings_json = [
        {
            'id': b.id,
            'latitude': b.latitude,
            'longitude': b.longitude,
            'evaluation': b.evaluation,
            'owner_name': b.owner_name,
            'building_name': b.building_name,
            'disaster_governorate': b.disaster_governorate or "غير محددة",
        } for b in buildings_qs
    ]

    return render(request, 'Catastrophe/history_catastrophe_details.html', {
        'buildings': buildings_qs,
        'buildings_json': json.dumps(buildings_json, cls=DjangoJSONEncoder)
    })


import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test


@user_passes_test(lambda u: u.is_superuser)
def export_buildings_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "تقييمات المباني"

    headers = [
        "المستخدم", "اسم صاحب المبنى", "اسم المبنى", "رقم الهاتف",
        "عدد الطوابق", "موقف سيارات", "العنوان", "الإحداثيات",
        "الحالة", "التقييم"
    ]
    ws.append(headers)

    for building in BuildingInfo.objects.all().select_related('user'):
        row = [
            building.user.username,
            building.owner_name,
            building.building_name,
            building.phone_number,
            building.floors,
            "نعم" if building.has_parking else "لا",
            building.address,
            f"{building.latitude}, {building.longitude}",
            building.status,
            building.get_evaluation_display() if building.evaluation else "لم يتم التقييم"
        ]
        ws.append(row)

    # تنسيق الأعمدة
    for col in ws.columns:
        max_length = max(len(str(cell.value)) for cell in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=building_evaluations.xlsx'
    wb.save(response)
    return response



from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import InvestigationForm
from .models import Investigation, InvestigationMedia

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


@login_required
def investigation_user_view(request):
    success_message = None
    investigation = None

    if request.method == 'POST':
        form = InvestigationForm(request.POST, request.FILES)
        files = request.FILES.getlist('images')
        videos = request.FILES.getlist('videos')
        signature_image = request.FILES.get('signature_image')

        if form.is_valid():
            investigation = form.save(commit=False)

            # ربط المستخدم
            investigation.user = request.user

            # تعبئة المحافظة والمركز تلقائيًا من حساب المستخدم
            if hasattr(request.user, 'governorate') and request.user.governorate:
                investigation.governorate = request.user.governorate
            if hasattr(request.user, 'center') and request.user.center:
                investigation.center = request.user.center

            # الإحداثيات والعنوان
            investigation.latitude = request.POST.get('latitude', 0.0)
            investigation.longitude = request.POST.get('longitude', 0.0)
            investigation.current_address = request.POST.get('current_address', '')

            # توقيع اللجنة
            signature_text = form.cleaned_data.get('committee_signature_text')
            if signature_text:
                investigation.committee_signature = signature_text
            investigation.signature_image = signature_image

            investigation.save()

            # حفظ الصور والفيديوهات
            for img in files:
                InvestigationMedia.objects.create(investigation=investigation, image=img)
            for vid in videos:
                InvestigationMedia.objects.create(investigation=investigation, video=vid)

            success_message = "تم حفظ التحقيق بنجاح!"
            form = InvestigationForm()
    else:
        form = InvestigationForm()

    return render(request, 'Investigation/investigation_user.html', {
        'form': form,
        'success_message': success_message,
        'investigation': investigation
    })

def reshape_arabic_text(text):
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    bidi_text = get_display(reshaped_text)
    return bidi_text

def download_investigation_pdf(request, investigation_id):
    investigation = Investigation.objects.get(id=investigation_id)

    buffer = BytesIO()
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Amiri-Regular.ttf')
    pdfmetrics.registerFont(TTFont("Arabic", font_path))

    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Arabic", 14)

    y = 800  # موضع البداية من الأعلى

    fields = [
        ("المركز", investigation.center),
        ("العنوان الحالي", investigation.current_address),
        ("إحداثيات العرض", investigation.latitude),
        ("إحداثيات الطول", investigation.longitude),
        ("اسم المالك", investigation.owner_name),
        ("طبيعة الأشغال", investigation.occupation_type),
        ("هل المبنى مؤمن؟", investigation.insured_status),
        ("تاريخ الحادث", investigation.event_date),
        ("وقت الحادث", investigation.event_time),
        ("تاريخ المعاينة", investigation.inspection_date),
        ("وقت المعاينة", investigation.inspection_time),
        ("تاريخ نهاية المعاينة", investigation.end_inspection_date),
        ("وقت نهاية المعاينة", investigation.end_inspection_time),
        ("الوصف العام", investigation.general_description),
        ("الملاحظات الفنية", investigation.technical_observations),
        ("مكان بدء الحريق", investigation.fire_start_area),
        ("الأضرار", investigation.damages),
        ("سبب الحريق", investigation.cause_of_incident),
        ("التحليل الفني", investigation.technical_analysis),
        ("توقيع اللجنة", investigation.committee_signature),
    ]

    for label, value in fields:
        if y < 100:
            p.showPage()
            p.setFont("Arabic", 14)
            y = 800

        # إذا كانت القيمة None أو فارغة، نستخدم "لم يحدد"
        display_value = value if value not in [None, ''] else "لم يحدد"
        text_line = reshape_arabic_text(f"{label}: {display_value}")
        p.drawRightString(550, y, text_line)
        y -= 30

    p.showPage()
    p.save()
    buffer.seek(0)

    return HttpResponse(buffer, content_type='application/pdf')

from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Investigation

@login_required
def investigations_admin(request):
    user = request.user

    if user.role == 'super_admin':
        investigations = Investigation.objects.all()
    elif user.role == 'governorate_admin':
        investigations = Investigation.objects.filter(governorate=user.governorate)
    elif user.role == 'center_admin':
        investigations = Investigation.objects.filter(center=user.center)
    else:
        # المستخدم العادي (Staff لإدخال التحقيقات) لا يحق له الوصول
        return redirect('home')  # أو أي صفحة تريد إعادة التوجيه إليها

    return render(request, 'Investigation/investigations_admin.html', {'investigations': investigations})



# views.py
from django.contrib.auth.decorators import login_required
from .models import Investigation

@login_required
def history_investigations_details(request):
    investigations = Investigation.objects.filter(user=request.user)
    return render(request, 'Investigation/history_investigation_details.html', {'investigations': investigations})


def get_coordinates(location):
    headers = {
        'User-Agent': 'MyMapApp/1.0 (myemail@example.com)'  # ضع أي اسم تطبيق أو بريدك
    }
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': location,
        'format': 'jsonv2',
        'addressdetails': 1,
        'limit': 1
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            lat = float(data[0]['lat'])
            lng = float(data[0]['lon'])
            country = data[0]['display_name']
            return lat, lng, country
    return None, None, None


@login_required
def investigation_detail(request, investigation_id):
    investigation = get_object_or_404(Investigation, id=investigation_id)
    user = request.user

    # صلاحيات الوصول
    allowed = False

    # ✅ 1. أدمن رئيسي: وصول كامل
    if user.role == "super_admin" or user.is_superuser:
        allowed = True

    # ✅ 2. أدمن محافظة: الوصول إذا التحقيق ضمن محافظته
    elif user.role == "governorate_admin":
        if investigation.governorate and user.governorate:
            if user.governorate.id == investigation.governorate.id:
                allowed = True

    # ✅ 3. أدمن مركز: الوصول إذا التحقيق ضمن مركزه
    elif user.role == "center_admin":
        if investigation.center and user.center:
            if user.center.id == investigation.center.id:
                allowed = True

    # ✅ 4. مستخدم عادي: لا صلاحية
    elif user.role == "user":
        allowed = False

    # ❌ إذا لم يكن مسموح له
    if not allowed:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("❌ ليس لديك صلاحية رؤية هذا التحقيق")

    # ✅ الحقول المعروضة في القالب
    fields = [
        ("المركز", investigation.center),
        ("العنوان الحالي", investigation.current_address),
        ("إحداثيات العرض", investigation.latitude),
        ("إحداثيات الطول", investigation.longitude),
        ("اسم المالك", investigation.owner_name),
        ("طبيعة الأشغال", investigation.occupation_type),
        ("هل المبنى مؤمن؟", investigation.insured_status),
        ("تاريخ الحادث", investigation.event_date),
        ("وقت الحادث", investigation.event_time),
        ("تاريخ المعاينة", investigation.inspection_date),
        ("وقت المعاينة", investigation.inspection_time),
        ("تاريخ نهاية المعاينة", investigation.end_inspection_date),
        ("وقت نهاية المعاينة", investigation.end_inspection_time),
        ("الوصف العام", investigation.general_description),
        ("الملاحظات الفنية", investigation.technical_observations),
        ("مكان بدء الحريق", investigation.fire_start_area),
        ("الأضرار", investigation.damages),
        ("سبب الحريق", investigation.cause_of_incident),
        ("التحليل الفني", investigation.technical_analysis),
    ]

    return render(request, 'Investigation/investigation_detail.html', {
        'investigation': investigation,
        'fields': fields,
    })

# def create_investigation(request):
#     if request.method == 'POST':
#         form = InvestigationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('investigation_success')  # أو صفحة تعرض التحقيقات
#     else:
#         form = InvestigationForm()
#     return render(request, 'investigation_form.html', {'form': form})

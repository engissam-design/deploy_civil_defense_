from django.contrib import admin
from django.urls import path
from map import views as map_views

from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path
from django.urls import path
# from .map_views import services_page_view
urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        '',
        auth_views.LoginView.as_view(
            template_name='login.html',
            redirect_authenticated_user=True
        ),
        name='login'
    ),
    path("main/", map_views.services_page_view, name="main_page"),    # path('catastrophes/', map_views.catastrophes_view, name='catastrophes'),#بدي احاول استنغي عنها

    path('after_login/', map_views.after_login_redirect, name='after_login_redirect'),
# path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('catastrophes_user/', map_views.catastrophes_user_view, name='Catastrophe/catastrophes_user'),
    path('notifications/status/mark-as-read/<int:id>/', map_views.mark_status_read, name='mark_status_read'),
    path('catastrophes_admin/', map_views.catastrophes_admin, name='Catastrophe/catastrophes_admin'),

    path('building/<int:building_id>/', map_views.catastrophe_detail, name='Catastrophe/catastrophe_detail'),
    path('history_catastrophe_details/', map_views.history_catastrophe_details, name='Catastrophe/history_catastrophe_details'),
    path('export_excel/', map_views.export_buildings_excel, name='export_buildings_excel'),
    
    
    path('investigation_staff/', map_views.investigation_user_view, name='Investigation/investigation_staff'),
    path('investigation_pdf/<int:investigation_id>/', map_views.download_investigation_pdf, name='download_investigation_pdf'),
    path('investigations_admin/', map_views.investigations_admin, name='Investigation/investigations_admin'),
    path('investigation/<int:investigation_id>/', map_views.investigation_detail, name='Investigation/investigation_detail'),
    path('investigations_user/', map_views.history_investigations_details, name='Investigation/investigations_user'),

    
    # path('investigations/', map_views.investigations_redirect, name='investigations_redirect'),

    # path('catastrophes/', map_views.catastrophes_redirect, name='catastrophes_redirect'),
    path("drivers/", map_views.driver_list, name="Driver/driver_list"),
    path('driver/<int:pk>/', map_views.driver_detail, name='Driver/driver_detail'),
    
    path("maintenance/", map_views.maintenance_list, name="Maintenance/maintenance_list"),
    path("maintenance/<int:pk>/", map_views.maintenance_detail, name="Maintenance/maintenance_detail"),
    path("maintenance/create/<int:vehicle_id>/", map_views.maintenance_create, name="maintenance_create"), 
    path("maintenance/<int:maintenance_id>/add-item/", map_views.maintenance_item_create, name="maintenance_item_create"),
    
    
    path(
    "vehicle/<int:vehicle_id>/maintenances/",
    map_views.maintenance_list_by_vehicle,
    name="maintenance_list_by_vehicle"
    ),
    path('vehicle/<int:vehicle_id>/maintenance/calculate/',map_views.calculate_monthly_maintenance,name='Maintenance/calculate_monthly_maintenance'),
    path('vehicle/<int:vehicle_id>/maintenance/pdf/',map_views.download_monthly_maintenance_pdf,name='download_monthly_maintenance_pdf'),
    path('vehicle/<int:vehicle_id>/maintenance/pdf/', map_views.download_monthly_maintenance_pdf, name='download_monthly_maintenance_pdf'),
    path("vehicles/", map_views.vehicle_list, name="Vehicle/vehicle_list"),
    path('vehicles/add/', map_views.add_vehicle, name='add_vehicle'),
    path('ajax/get-centers/', map_views.get_centers_by_governorate, name='get_centers_by_governorate'),

    path("drivers/add/", map_views.add_driver, name="Driver/add_driver"),
    
    # path('publicSafety/', map_views.public_safety_redirect, name='public_safety_redirect'),



    path('publicSafety_user/', map_views.publicSafety_user_view, name='PublicSafety/publicSafety_user'),
    path('publicSafety/pdf/<int:safety_id>/', map_views.download_public_safety_pdf, name='public_safety_pdf'),
    path('publicSafety_superuser/', map_views.publicSafety_admin, name='PublicSafety/public_safety_superuser'),
    path('publicSafety/details/<int:safety_id>/', map_views.publicSafety_detail, name='PublicSafety/history_publicSafety_detail_userss'),
    path('history_publicSafety_details/', map_views.history_publicSafety_details, name='PublicSafety/history_publicSafety_details'),
    path('public-safety/<int:record_id>/', map_views.history_publicSafety_detail_user, name='PublicSafety/history_publicSafety_detail_user'),
    
    
    
    
    path('operations/', map_views.operations_map, name='Operation/operations_map'),
    path('add-operation/', map_views.add_operation, name='Operation/add_operation'),
    path('operation/<int:pk>/', map_views.operation_detail, name='Operation/operation_detail'),
    path('operation/<int:pk>/edit/', map_views.update_operation, name='Operation/edit_operation'),

    path('add-attendance/<int:operation_id>/', map_views.add_attendance, name='add_attendance'),
    path('attendance/print/<int:operation_id>/', map_views.print_attendance_pdf, name='print_attendance_pdf'),
    path('operation/<int:operation_id>/working-today/', map_views.working_today_employees, name='Employees/working_today_employees'),

    path('employee/<int:pk>/', map_views.employee_detail, name='Employees/employee_detail'),
    path("add-employee/", map_views.add_employee, name="Employees/add_employee"),
    path('employees/', map_views.employees_by_operation, name='Employees/employees_by_operation'),
    path("employees/governorate/", map_views.employees_by_governorate, name="Employees/employees_by_governorate"),
    path('notifications/mark-status-read/<int:id>/', map_views.mark_status_read, name='mark_status_read'),


    path("vehicles/<int:vehicle_id>/trips/", map_views.trip_list, name="Trip/trip_list"),
    path("vehicles/<int:vehicle_id>/trips/add/", map_views.add_trip, name="Trip/add_trip"),
    path('vehicle/<int:vehicle_id>/trips/count/', map_views.trip_filter_view, name='Trip/trip_count'),
    path('vehicle/<int:vehicle_id>/trips/pdf/', map_views.download_trips_pdf, name='download_trips_pdf'),
    path('vehicle/<int:pk>/', map_views.vehicle_detail, name='Vehicle/vehicle_detail'),
    path('vehicle/<int:pk>/approve/<str:approval_type>/', map_views.approve_vehicle, name='approve_vehicle'),
    path('vehicle/<int:vehicle_id>/drivers/', map_views.vehicle_drivers, name='Driver/vehicle_drivers'),
    path("vehicle/<int:pk>/edit-drivers/", map_views.edit_vehicle_drivers, name="edit_vehicle_drivers"),
    path("vehicles/<int:vehicle_id>/status/", map_views.vehicle_status, name="vehicle_status"),
    path("vehicles/<int:vehicle_id>/toggle_status/", map_views.toggle_vehicle_status, name="toggle_vehicle_status"),   
    path("fuel-quotas/", map_views.fuel_quota_list, name="Fuel/fuel_quota_list"),
    path("fuel-quotas/<int:quota_id>/", map_views.fuel_quota_detail, name="Fuel/fuel_quota_detail"),
    path("fuel-quotas/<int:quota_id>/add-filling/", map_views.add_fuel_filling, name="add_fuel_filling"),
    path("fuel-quotas/add/", map_views.fuel_quota_add, name="Fuel/fuel_quota_add"),  # ✅ مسار إضافة مخصص
    
    path('fuel_quota/<int:quota_id>/pdf/', map_views.download_fuel_quota_pdf, name='download_fuel_quota_pdf'),
    path("fuel-quotas/vehicle/<int:vehicle_id>/", map_views.fuel_quota_list_by_vehicle, name="Fuel/fuel_quota_list_by_vehicle"),


    path('services/', map_views.services_page_view, name='services_page'),

    path('superuser/all-phones/', map_views.superuser_all_phones_view, name='superuser_all_phones'),
    path('notifications/mark-as-read/<int:noti_id>/', map_views.mark_notification_as_read),
    path('notifications/mark-as-read-all/', map_views.mark_all_notifications_as_read),  
    path('logout/', map_views.logout_view, name='logout')
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
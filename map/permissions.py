from django.contrib.auth.mixins import AccessMixin

class HierarchyFilterMixin(AccessMixin):
    """
    هذا المكسن يطبق الفلترة الجغرافية والوظيفية تلقائياً
    """
    def get_queryset(self):
     user = self.request.user
     qs = super().get_queryset()
    
    # 🔹 السوبر يوزر يرى كل شيء
     if user.is_superuser:
        return qs

     assignment = getattr(user, 'assignment', None)
     if not assignment:
        return qs.none()

    # ✅ فلترة حسب القسم فقط إذا موجود
     if assignment.department_id:
        qs = qs.filter(department=assignment.department)

    # 🔹 فلترة حسب النطاق الجغرافي
     if assignment.level == 'hq':
        return qs
    
     if assignment.level == 'governorate':
        return qs.filter(governorate=assignment.governorate)
    
     if assignment.level == 'center':
        return qs.filter(center=assignment.center)

     return qs.none()
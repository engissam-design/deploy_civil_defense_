from django.contrib.auth.backends import BaseBackend
from .models import UserAssignment

class RoleBasedPermissionBackend(BaseBackend):
    """
    باكيند مخصص لفحص صلاحيات المستخدم بناءً على "التعيين الوظيفي النشط" والـ Role المسند إليه.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        return None

    def get_user_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()

        # جلب التعيين الوظيفي النشط للمستخدم
        assignment = UserAssignment.objects.filter(
            user=user_obj, 
            is_active=True
        ).select_related('role').first()

        if not assignment or not assignment.role:
            return set()

        # جلب الصلاحيات بصيغة "app_label.codename" مثل "map.can_view_operations_map"
        perms = assignment.role.permissions.select_related('content_type').all()
        
        return {f"{p.content_type.app_label}.{p.codename}" for p in perms}

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False

        if user_obj.is_superuser:
            return True

        # الفحص المباشر داخل مجموعة الصلاحيات المستخرجة من الدور
        return perm in self.get_user_permissions(user_obj, obj)

    def has_module_perms(self, user_obj, app_label):
        """مهمة جداً لكي تظهر الجداول داخل لوحة تحكم الإدارة (Admin)"""
        if user_obj.is_active and user_obj.is_superuser:
            return True
            
        # إذا كان يمتلك أي صلاحية تبدأ باسم التطبيق المطلوب
        user_perms = self.get_user_permissions(user_obj)
        return any(perm.startswith(f"{app_label}.") for perm in user_perms)
    
    def get_all_permissions(self, user_obj, obj=None):
        """
        دمج الصلاحيات (في حال وجود صلاحيات أخرى مستقبلاً)
        """
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()
            
        return self.get_user_permissions(user_obj, obj)
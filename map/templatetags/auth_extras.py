from django import template
register = template.Library()

@register.filter(name='has_perm')
def has_perm(user, permission_codename):
    if user.is_superuser: return True
    # نستخدم .assignments لأنها الـ related_name في الـ UserAssignment
    assignment = user.assignments.filter(is_active=True).first()
    if assignment and assignment.role:
        return assignment.role.permissions.filter(codename=permission_codename).exists()
    return False
    

@register.filter(name='can_add_vehicle')
def can_add_vehicle(user):
    if user.is_superuser: return True
    
    assignment = user.assignments.filter(is_active=True).first()
    if assignment and assignment.role and assignment.unit:
        # التحقق من كلا النوعين
        is_transport_manager = "مدير" in assignment.role.name and "النقل والصيانة" in assignment.unit.name
        is_ops_manager = "مدير" in assignment.role.name and "إدارة العمليات" in assignment.unit.name
        
        if is_transport_manager or is_ops_manager:
            return True
            
    return False
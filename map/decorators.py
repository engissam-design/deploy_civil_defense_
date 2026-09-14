from django.core.exceptions import PermissionDenied
from functools import wraps
from .models import UserAssignment
from django.core.exceptions import PermissionDenied
from functools import wraps


def transport_manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        if request.user.has_perm("map.add_vehicle"):
            return view_func(request, *args, **kwargs)

        raise PermissionDenied("ليس لديك الصلاحية.")

    return _wrapped_view



from django.core.exceptions import PermissionDenied
from functools import wraps


def vehicle_status_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # ✔ صلاحية من Django
        if request.user.has_perm("map.change_vehicle_status"):
            return view_func(request, *args, **kwargs)

        raise PermissionDenied("ليس لديك صلاحية تغيير حالة المركبة.")

    return _wrapped_view